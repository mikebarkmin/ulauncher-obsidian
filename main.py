import gi
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

gi.require_version("Gdk", "3.0")
from src.items import quick_capture_note, show_notes, create_note, select_note, cancel
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
from ulauncher.api.shared.event import (
    KeywordQueryEvent,
    ItemEnterEvent,
    SystemExitEvent,
)
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
import logging

logger = logging.getLogger(__name__)


class ObisidanExtension(Extension):
    def __init__(self):
        super(ObisidanExtension, self).__init__()

        self.state = "default"
        self.content = ""
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(SystemExitEvent, SystemExitEventListener())

    def reset(self):
        self.state = "default"
        self.content = ""


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        vault = extension.preferences["obsidian_vault"]
        data = event.get_data()
        type = data.get("type")

        if type == "cancel":
            extension.reset()
            return SetUserQueryAction("")

        elif type == "create-note" and extension.state == "quick-capture-to-note":
            path = create_note_in_vault(vault, data.get("name"))
            append_to_note_in_vault(vault, path, extension.content)
            extension.reset()
            return HideWindowAction()

        elif type == "create-note":
            path = create_note_in_vault(vault, data.get("name"))
            url = generate_url(vault, path)
            return OpenAction(url)

        elif type == "quick-capture":
            quick_capute_note = extension.preferences["obsidian_quick_capture_note"]
            append_to_note_in_vault(vault, quick_capute_note, data.get("content"))
            return HideWindowAction()

        elif type == "quick-capture-to-note":
            keyword_quick_capture = extension.preferences["obsidian_quick_capture"]
            extension.state = "quick-capture-to-note"
            extension.content = data.get("content")
            return SetUserQueryAction(keyword_quick_capture + " ")

        elif extension.state == "quick-capture-to-note" and type == "select-note":
            quick_capute_note = data.get("note").path
            append_to_note_in_vault(vault, quick_capute_note, extension.content)
            extension.reset()
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
        number_of_notes = int(extension.preferences.get("number_of_notes", 8))

        keyword = event.get_keyword()
        search = event.get_argument()

        if extension.state == "quick-capture-to-note":
            notes = find_note_in_vault(vault, search)
            items = select_note(notes, number_of_notes)
            items += create_note(search)
            items += cancel()
            return RenderResultListAction(items)

        if keyword == keyword_search_note_vault:
            notes = find_note_in_vault(vault, search)
            items = show_notes(vault, notes, number_of_notes)
            items += create_note(search)
            items += cancel()
            return RenderResultListAction(items)

        elif keyword == keyword_search_string_vault:
            notes = find_string_in_vault(vault, search)
            items = show_notes(vault, notes, number_of_notes)
            items += create_note(search)
            items += cancel()
            return RenderResultListAction(items)

        elif keyword == keyword_open_daily:
            return OpenAction(generate_daily_url(vault))

        elif keyword == keyword_quick_capture:
            items = quick_capture_note(search)
            return RenderResultListAction(items)

        return DoNothingAction()


class SystemExitEventListener(EventListener):
    def on_event(self, event, extension):
        extension.reset()


if __name__ == "__main__":
    ObisidanExtension().run()
