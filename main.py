from src.items import show_notes, create_note
from src.functions import (
    find_note_in_vault,
    find_string_in_vault,
    create_note_in_vault,
    generate_url,
)
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.LaunchAppAction import LaunchAppAction
import logging

logger = logging.getLogger(__name__)


class ObisidanExtension(Extension):
    def __init__(self):
        super(ObisidanExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        vault = extension.preferences["obsidian_vault"]
        data = event.get_data()
        type = data.get("type")

        if type == "create-note":
            path = create_note_in_vault(vault, data.get("name"))
            url = generate_url(vault, path)
            return OpenUrlAction(url)

        return DoNothingAction()


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        vault = extension.preferences["obsidian_vault"]

        keyword_search_note_vault = extension.preferences["obsidian_search_note_vault"]
        keyword_search_string_vault = extension.preferences[
            "obsidian_search_string_vault"
        ]

        keyword = event.get_keyword()
        search = event.get_argument()

        if keyword == keyword_search_note_vault:
            notes = find_note_in_vault(vault, search)
            items = show_notes(vault, notes)
            items += create_note(vault, search)
            return RenderResultListAction(items)

        elif keyword == keyword_search_string_vault:
            notes = find_string_in_vault(vault, search)
            items = show_notes(vault, notes)
            items += create_note(vault, search)
            return RenderResultListAction(items)

        return DoNothingAction()


if __name__ == "__main__":
    ObisidanExtension().run()
