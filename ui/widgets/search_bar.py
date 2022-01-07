from typing import Union
from rich.panel import Panel
from rich import box


from textual import events
from textual.widget import Widget
from textual.reactive import Reactive

class SearchBar(Widget):
    has_focus: Reactive[bool] = Reactive(False)
    mouse_over: Reactive[bool] = Reactive(False)
    query: Reactive(str) = Reactive("~Blank~")

    def render(self) -> Panel:
        return Panel(self.query, width = None, height = 3,
                     box=box.HEAVY if self.has_focus else box.ASCII,)




    #def __rich_repr__(self) -> rich.repr.Result:
        #yield "name", self.name
        #yield "has_focus", self.has_focus, False
        #yield "mouse_over", self.mouse_over, False

    async def on_focus(self, event: events.Focus):
        self.has_focus = True
    async def on_blur(self, event:events.Blur):
        self.has_focus = False

    async def backspace(self):
        query_len = len(self.query)
        if query_len > 0:
            self.query = self.query[0:query_len-1]

    async def push_char(self, char):
        self.query += char

    async def set_title(self, new_title):
        self.query = new_title
