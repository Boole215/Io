from rich.console import RenderableType
from rich.text import Text

from textual.widget import Widget
from textual.reactive import Reactive



class StatusBar(Widget):
    status: Reactive[str] = Reactive(Text(" ",
                                          style="white on steel_blue3",
                                          no_wrap=True,
                                          overflow="ellipsis",
                                          justify="left",
                                          end="",
                            ))


    def __init__(self):
        super().__init__()
        self.layout_size = 1


    def set_status_text (self, statuses: list) -> Text:
        self.status = Text("",
            style="white on steel_blue3",
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
            )
        for status in statuses:
            self.status.append(" " + status)

    def render(self) -> RenderableType:
        return self.status
