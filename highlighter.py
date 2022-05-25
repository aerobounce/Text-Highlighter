from collections import OrderedDict
from re import escape
from typing import List
from typing import OrderedDict as tOrderedDict

from sublime import DRAW_NO_OUTLINE, Region, View
from sublime_plugin import EventListener, WindowCommand

COLORS_BY_SCOPE: tOrderedDict[str, str] = OrderedDict()


def plugin_loaded():
    COLORS_BY_SCOPE["markup.changed.git_gutter"] = ""  # vivid purple
    COLORS_BY_SCOPE["support.class"] = ""  # yellow
    COLORS_BY_SCOPE["markup.deleted.git_gutter"] = ""  # vivid pink
    COLORS_BY_SCOPE["markup.inserted.git_gutter"] = ""  # vivid green
    COLORS_BY_SCOPE["constant.numeric"] = ""  # orange
    COLORS_BY_SCOPE["constant.character.escape"] = ""  # light blue
    COLORS_BY_SCOPE["variable"] = ""  # red
    COLORS_BY_SCOPE["string"] = ""  # light green
    COLORS_BY_SCOPE["comment"] = ""  # glay


def plugin_unloaded():
    COLORS_BY_SCOPE.clear()


class TextHighlighterToggleCommand(WindowCommand):
    def run(self):  # pyright: ignore
        if active_view := self.window.active_view():
            selected_region = active_view.sel()
            selection = active_view.substr(selected_region[0])

            # Get word on cursor if any region isn't selected.
            if not selection:
                word_region = active_view.word(selected_region[0])
                selection = active_view.substr(word_region)

            views = self.window.views()
            if is_highlighted(selection):
                if color := find_used_color(selection):
                    for view in views:
                        eraser(view, selection, color)
            else:
                if color := find_usable_color():
                    for view in views:
                        highlighter(view, selection, color)


class TextHighlighterClearAllCommand(WindowCommand):
    def run(self):  # pyright: ignore
        views = self.window.views()

        for selection in COLORS_BY_SCOPE.values():
            if selection:
                color = find_used_color(selection)
                if color:
                    for view in views:
                        eraser(view, selection, color)


class HighlighterCommand(EventListener):
    def on_activated(self, view: View):
        highlightAll(view)

    def on_modified(self, view: View):
        highlightAll(view)


def highlightAll(view: View):
    if window := view.window():
        views = window.views()

        for view in views:
            for color, selection in COLORS_BY_SCOPE.items():
                if color and selection:
                    highlighter(view, selection, color)


def highlighter(view: View, selection: str, color: str):
    regions = find_all(view, selection)
    if color and regions:
        if not COLORS_BY_SCOPE[color]:
            COLORS_BY_SCOPE[color] = selection

        view.add_regions(selection, regions, color, "dot", DRAW_NO_OUTLINE)


def eraser(view: View, selection: str, color: str):
    COLORS_BY_SCOPE[color] = ""
    view.erase_regions(selection)


def find_all(view: View, selection: str) -> List[Region]:
    return view.find_all(escape(selection))


def is_highlighted(selection: str):
    highlighted = False
    for _, value in COLORS_BY_SCOPE.items():
        if value == selection:
            highlighted = True
            break
    return highlighted


def find_used_color(selection: str):
    color = None
    for key, value in COLORS_BY_SCOPE.items():
        if value == selection:
            color = key
    return color


def find_usable_color():
    color = None
    for key, value in COLORS_BY_SCOPE.items():
        if not value:
            color = key
            break
    return color
