import gi
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

gi.require_version("Gdk", "3.0")
from src.items import quick_capute_note, show_notes, create_note
from src.functions import (
    append_to_note_in_vault,
    find_note_in_vault,
    find_string_in_vault,
    create_note_in_vault,
    generate_daily_url,
    generate_url,
)
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
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
            return OpenAction(url)

        elif type == "quick-capture":
            quick_capute_note = extension.preferences["obsidian_quick_capture_note"]
            append_to_note_in_vault(vault, quick_capute_note, data.get("content"))
            return HideWindowAction()

        return DoNothingAction()


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        vault = extension.preferences["obsidian_vault"]

        keyword_search_note_vault = extension.preferences["obsidian_search_note_vault"]
        keyword_search_string_vault = extension.preferences[
            "obsidian_search_string_vault"
        ]
        keyword_open_daily = extension.preferences["obsidian_open_daily"]
        keyword_quick_capture = extension.preferences["obsidian_quick_capture"]

        keyword = event.get_keyword()
        search = event.get_argument()

        if keyword == keyword_search_note_vault:
            notes = find_note_in_vault(vault, search)
            items = show_notes(vault, notes)
            items += create_note(search)
            return RenderResultListAction(items)

        elif keyword == keyword_search_string_vault:
            notes = find_string_in_vault(vault, search)
            items = show_notes(vault, notes)
            items += create_note(search)
            return RenderResultListAction(items)

        elif keyword == keyword_open_daily:
            return OpenAction(generate_daily_url(vault))

        elif keyword == keyword_quick_capture:
            items = quick_capute_note(search)
            return RenderResultListAction(items)

        return DoNothingAction()


if __name__ == "__main__":
    ObisidanExtension().run()
