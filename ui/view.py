import rich
import string

from typing import Union
import textual.__init__
from os import get_terminal_size

from rich.console import RenderableType
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich.pretty import Pretty
from rich.text import Text
from rich import box


from textual import events
from textual.app import App
from textual.widget import Widget
from textual.widgets import ScrollView, Footer
from textual.views import DockView
from textual.reactive import Reactive
from textual.keys import Keys


from .widgets.status_bar import StatusBar
from .widgets.search_bar import SearchBar
from .widgets.gem_page import GemPage
from networking.client import Client

start_page = b'# Welcome Page\nWelcomeeee, here are some useful keybinds for you:\n* C-Q - quit\n* C-S - Toggles the search bar (click the search bar to type in it, and onto the document body to stop)\n* l - cycles through links present on the current page\nThose are all the binds we have for now,\nRemember what they say:\n> Poop.\n=> gemini://gemini.circumlunar.space/ sample link'

app_client = Client()

#Put LagannApp here, and make separate files for each widget
# have two views, one will be the gemini page and the other will
# be the searchbar, when the user presses 's' the serachbar will come out
# if they click away from the searchbar, it goes away.
#
class LagannView(App):
    show_search_bar = Reactive(False)

    MIME = "Gemini/Text"
    statuses = Reactive([MIME])

    # TODO: Provide some way for dispatch_search to obtain and return the query
    #       that's created in connection


    async def on_key(self, key: events.Key) -> None:
        if self.show_search_bar and self.search_bar.has_focus:
            query_len = len(self.search_bar.query)
            if key.key in string.printable:
                await self.search_bar.push_char(key.key)
            elif key.key == Keys.ControlH:
                await self.search_bar.backspace()
            elif key.key == Keys.Enter:
                query = self.search_bar.query
                if not "/" in query:
                    query = query + "/"
                if not "gemini://" in self.search_bar.query:
                    query = "gemini://" + query
                    await self.search_bar.set_title(query)
                await self.set_page(await self.dispatch_search(query), query)
                #new_page = await self.dispatch_search(self.search_bar.query);
                #self.panic(type(new_page), new_page)
                #self.center_page = GemPage(new_page)
                #await self.gem_page.update(self.center_page)
        elif key.key == Keys.ControlQ:
            quit()
        elif key.key == Keys.ControlS:
            await self.toggle_search_bar()
        elif key.key == "l":
            #TODO: Let Keys.ShiftL cycle backwards
            if not self.center_page.cycling:
                self.center_page.toggle_cycle_links()
            else:
                self.center_page.cycle_link()

            highlight_idx = self.center_page.get_highlighted()
            if highlight_idx == -1:
                #self.statuses.append("L: No Links in Document")
                return

            self.gem_page.scroll_to_center(highlight_idx)
        elif key.key == Keys.Enter and self.center_page.cycling:
            new_url = self.center_page.get_highlighted_link()
            if not "gemini://" in new_url:
                # this is a relative link, append the url
                new_url = self.center_page.url + new_url

            await self.set_page(await self.dispatch_search(new_url), new_url)
            await self.search_bar.set_title(new_url)
            return




    async def toggle_search_bar(self) -> None:
        self.show_search_bar = not self.show_search_bar

    async def disable_search_bar(self) -> None:
        self.show_search_bar = Reactive(None)

    async def watch_show_search_bar(self, show_search_bar) -> None:
        self.animator.animate(self.search_bar, "layout_offset_y", 0 if show_search_bar else -20)

    async def dispatch_search(self, search_url):
        global app_client
        result = app_client.get_page(search_url)
        return result.body

    async def set_page(self, page, url):
        self.center_page = GemPage(page, url)
        await self.gem_page.update(self.center_page)

    async def on_mount(self, event: events.Mount) -> None:

        self.footer = StatusBar()
        self.footer.set_status_text(self.statuses)

        self.center_page = GemPage(start_page, "~Blank~")
        self.gem_page = ScrollView(self.center_page)

        self.search_bar = SearchBar()
        self.search_bar.layout_offset_x = 0
        self.search_bar.layout_offset_y = -20

        await self.view.dock(self.footer, edge="bottom", z = 1)
        await self.view.dock(self.search_bar, edge="top", size = 3, z=1)

        sub_view = DockView()

        await sub_view.dock(self.gem_page, edge="top")
        await self.view.dock(sub_view)



def start_ui():
    LagannView.run(log = "textual.log")
