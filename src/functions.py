import os
import glob
from urllib.parse import quote, urlencode
from pathlib import Path
from typing import List
import logging
from ulauncher.utils.fuzzy_search import get_score

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


def generate_url(vault: str, file: str) -> str:
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

    """
    vault_name = get_name_from_path(vault)
    if not file.endswith(".md"):
        file = file + ".md"

    try:
        relative_file = Path(file).relative_to(vault)
        return "obsidian://open?" + urlencode(
            {"vault": vault_name, "file": relative_file}, quote_via=quote
        )
    except ValueError:
        if not file.endswith(".md"):
            file = file + ".md"
        return "obsidian://open?" + urlencode(
            {"vault": vault_name, "file": file}, quote_via=quote
        )


def get_name_from_path(path: str) -> str:
    """
    >>> get_name_from_path("~/home/test/bla/hallo.md")
    'hallo'
    """
    base = os.path.basename(path)
    split = os.path.splitext(base)
    return split[0]


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
                        context = left[CONTEXT_SIZE:] + \
                            sep + right[:CONTEXT_SIZE]
                        suggestions.append(
                            Note(
                                name=get_name_from_path(file),
                                path=file,
                                description=context,
                            )
                        )

    return suggestions


def create_note_in_vault(vault: str, name: str) -> str:
    path = os.path.join(vault, name + ".md")
    if not os.path.isfile(path):
        with open(path, "w") as f:
            f.write(f"# {name}")
    return path


if __name__ == "__main__":
    import doctest

    doctest.testmod()
