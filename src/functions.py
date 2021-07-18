import os
import glob
import json
import datetime
from urllib.parse import quote, urlencode
from pathlib import Path
from typing import List, Literal
import logging
from ulauncher.utils.fuzzy_search import get_score

from .moment import convert_moment_to_strptime_format

logger = logging.getLogger(__name__)


def fuzzyfinder(search: str, items: List[str]) -> List[str]:
    """
    >>> fuzzyfinder("hallo", ["hi", "hu", "hallo", "false"])
    ['hallo', 'false', 'hi', 'hu']
    """
    scores = []
    for i in items:
        score = get_score(search, get_name_from_path(i))
        scores.append((score, i))

    scores = sorted(scores, key=lambda score: score[0], reverse=True)

    return list(map(lambda score: score[1], scores))


class Note:
    def __init__(self, name: str, path: str, description: str):
        self.name = name
        self.path = path
        self.description = description

    def __repr__(self):
        return f"Note<{self.path}>"


def generate_url(vault: str, file: str, mode: Literal["open", "new"] = "open") -> str:
    """
    >>> generate_url("~/vault", "test.md")
    'obsidian://open?vault=vault&file=test.md'

    >>> generate_url("~/vault", "test")
    'obsidian://open?vault=vault&file=test.md'

    >>> generate_url("~/vault", "~/vault/test")
    'obsidian://open?vault=vault&file=test.md'

    >>> generate_url("~/vault", "~/vault/test")
    'obsidian://open?vault=vault&file=test.md'

    >>> generate_url("~/vault", "Java - Programming Language")
    'obsidian://open?vault=vault&file=Java%20-%20Programming%20Language.md'

    >>> generate_url("/home/kira/Documents/main_notes/", "Ulauncher Test", mode="new")
    'obsidian://new?vault=main_notes&file=Ulauncher%20Test.md'

    >>> generate_url("/home/[me]/Development/ObsidianVaults/", "Ulauncher Test", mode="new")
    'obsidian://new?vault=ObsidianVaults&file=Ulauncher%20Test.md'

    """
    if vault.endswith("/"):
        vault = vault[:-1]

    vault_name = get_name_from_path(vault, exclude_ext=False)
    if not file.endswith(".md"):
        file = file + ".md"

    try:
        relative_file = Path(file).relative_to(vault)
        return (
            "obsidian://"
            + mode
            + "?"
            + urlencode({"vault": vault_name, "file": relative_file}, quote_via=quote)
        )
    except ValueError:
        if not file.endswith(".md"):
            file = file + ".md"
        return (
            "obsidian://"
            + mode
            + "?"
            + urlencode({"vault": vault_name, "file": file}, quote_via=quote)
        )


class DailyPath:
    path: str
    date: str
    folder: str
    exists: bool

    def __init__(self, path, date, folder, exists) -> None:
        self.path = path
        self.date = date
        self.folder = folder
        self.exists = exists


def get_daily_path(vault: str) -> DailyPath:
    daily_notes_path = os.path.join(vault, ".obsidian", "daily-notes.json")
    try:
        f = open(daily_notes_path, "r")
        daily_notes_config = json.load(f)
        f.close()
    except:
        daily_notes_config = {}
    format = daily_notes_config.get("format", "YYYY-MM-DD")
    folder = daily_notes_config.get("folder", "")

    if format == "":
        format = "YYYY-MM-DD"

    date = datetime.datetime.now().strftime(convert_moment_to_strptime_format(format))
    path = os.path.join(vault, folder, date + ".md")
    exists = os.path.exists(path)

    return DailyPath(path, date, folder, exists)


def generate_daily_url(vault: str) -> str:
    """
    >>> generate_daily_url("~/vault")
    'obsidian://new?vault=vault&file=2021-07-16.md'
    """
    daily_path = get_daily_path(vault)
    mode = "new"
    if daily_path.exists:
        mode = "open"

    return generate_url(
        vault, os.path.join(daily_path.folder, daily_path.date), mode=mode
    )


def get_name_from_path(path: str, exclude_ext=True) -> str:
    """
    >>> get_name_from_path("~/home/test/bla/hallo.md")
    'hallo'

    >>> get_name_from_path("~/home/Google Drive/Brain 1.0", False)
    'Brain 1.0'
    """
    base = os.path.basename(path)
    if exclude_ext:
        split = os.path.splitext(base)
        return split[0]
    return base


def find_note_in_vault(vault: str, search: str) -> List[Note]:
    """
    >>> find_note_in_vault("test-vault", "Test")
    [Note<test-vault/Test.md>, Note<test-vault/Test2.md>, Note<test-vault/subdir/Test.md>, Note<test-vault/subdir/Hallo.md>]
    """
    search_pattern = os.path.join(vault, "**", "*.md")
    logger.info(search_pattern)
    files = glob.glob(search_pattern, recursive=True)
    suggestions = fuzzyfinder(search, files)
    return [
        Note(name=get_name_from_path(s), path=s, description=s) for s in suggestions
    ]


def find_string_in_vault(vault: str, search: str) -> List[Note]:
    """
    >>> find_string_in_vault("test-vault", "Test")
    [Note<test-vault/Test.md>, Note<test-vault/subdir/Test.md>]
    """
    files = glob.glob(os.path.join(vault, "**", "*.md"), recursive=True)

    suggestions = []

    CONTEXT_SIZE = 10

    search = search.lower()
    for file in files:
        if os.path.isfile(file) and search is not None:
            with open(file, "r") as f:
                for line in f:
                    left, sep, right = line.lower().partition(search)
                    if sep:
                        context = left[CONTEXT_SIZE:] + sep + right[:CONTEXT_SIZE]
                        suggestions.append(
                            Note(
                                name=get_name_from_path(file),
                                path=file,
                                description=context,
                            )
                        )
                        break

    return suggestions


def create_note_in_vault(vault: str, name: str) -> str:
    path = os.path.join(vault, name + ".md")
    if not os.path.isfile(path):
        with open(path, "w") as f:
            f.write(f"# {name}")
    return path


def append_to_note_in_vault(vault: str, file: str, content: str):
    if file == "":
        file = get_daily_path(vault).path
    elif not file.endswith(".md"):
        file = file + ".md"
    path = os.path.join(vault, file)

    with open(path, "a") as f:
        f.write(os.linesep)
        f.write(content)


if __name__ == "__main__":
    import doctest
    import time_machine

    traveller = time_machine.travel(datetime.datetime(2021, 7, 16))
    traveller.start()

    doctest.testmod()

    traveller.stop()
