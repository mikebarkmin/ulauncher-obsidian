from typing import List
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

from src.functions import generate_url, Note, create_note_in_vault


ICON_FILE = "images/icon.png"
ICON_ADD_FILE = "images/icon-add.png"


def create_note(vault, name):
    return [
        ExtensionResultItem(
            icon=ICON_ADD_FILE,
            name=f'Create "{name}"',
            on_enter=ExtensionCustomAction(
                {"type": "create-note", "name": name}, keep_app_open=False
            ),
        )
    ]


def show_notes(vault, notes: List[Note]):
    return [
        ExtensionResultItem(
            icon=ICON_FILE,
            name=note.name,
            description=note.description,
            on_enter=OpenAction(generate_url(vault, note.path)),
        )
        for note in notes[:10]
    ]
