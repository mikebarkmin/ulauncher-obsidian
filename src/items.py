from typing import List
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

from .functions import generate_url, Note


ICON_FILE = "images/icon.png"
ICON_ADD_FILE = "images/icon-add.png"


def create_note(name):
    return [
        ExtensionResultItem(
            icon=ICON_ADD_FILE,
            name=f'Create "{name}"',
            on_enter=ExtensionCustomAction(
                {"type": "create-note", "name": name}, keep_app_open=True
            ),
        )
    ]


def quick_capture_note(content):
    return [
        ExtensionResultItem(
            icon=ICON_ADD_FILE,
            name="Quick Capture",
            on_enter=ExtensionCustomAction(
                {"type": "quick-capture", "content": content}, keep_app_open=True
            ),
        ),
        ExtensionResultItem(
            icon=ICON_ADD_FILE,
            name="Quick Capture to Note",
            on_enter=ExtensionCustomAction(
                {"type": "quick-capture-to-note", "content": content}, keep_app_open=True
            ),
        ),
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


def select_note(notes: List[Note]):
    return [
        ExtensionResultItem(
            icon=ICON_FILE,
            name=note.name,
            description=note.description,
            on_enter=ExtensionCustomAction(
                {"type": "select-note", "note": note},
                keep_app_open=True,
            ),
        )
        for note in notes[:10]
    ]
