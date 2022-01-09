from rich.panel import Panel
from rich.text import Text
from rich import box

from textual import events
from textual.widget import Widget
from textual.reactive import Reactive

class GemPage(Widget):
    highlight_idx = Reactive(-1)
    link_indices = []
    cycling = Reactive(False)
    links = []

    body = Text()
    doc_type = ""

    url = ""

    def __init__(self, doc_type, content, url):
        super().__init__()
        self.url = url

        self.doc_type = doc_type
        #self.log(content)
        if doc_type == "text/gemini":
            self.link_indices = content[0]
            self.links = content[1]
            self.body = content[2]
        else:
            self.body = content



    def _format_parsed_gem(self, gem_page):
        self.log("parsed_gem: {}".format(gem_page))
        pretty_page = Text("")
        idx = 0
        hover_idx = self.link_indices[self.highlight_idx] if self.cycling else -1
        #self.log("{} {} {}".format(self.cycling, self.highlight_idx, hover_idx))
        for line in gem_page:
            if line[1] == 'h1':
                pretty_page.append(line[0] + "\n", style = "bold bright_white")
            elif line[1] == 'h2':
                pretty_page.append(line[0] + "\n", style = "bold bright_white")
            elif line[1] == 'h3':
                pretty_page.append(line[0] + "\n", style = "bold bright_white")
            elif line[1] == 'link':
                placeholder = line[0]
                if self.cycling:
                    if hover_idx == idx:
                        placeholder = Text(placeholder, style = "light_slate_blue")
                        link_text = self.links[self.highlight_idx]
                        link_text = Text(" => " + link_text + "\n", style = "grey42")
                        pretty_page.append(placeholder + link_text)
                    else:
                        pretty_page.append(placeholder + "\n", style = "green_yellow")

                else:
                    pretty_page.append(placeholder + "\n", style = "green_yellow")


            elif line[1] == 'quote':
                pretty_page.append('\t| ' + line[0] + "\n", style = "grey42")
            elif line[1] == 'list':
                pretty_page.append("\t" + line[0] + "\n")
            elif line[1] == 'nl':
                pretty_page.append('\n')
            else:
                pretty_page.append(line[0]+'\n')
            idx += 1


        return pretty_page

    #def set_document(self, new_page):
        #self.link_indices, document = parse_page(new_page)
        #self.document = self.prettify_parsed_gem(document)
        #self.log(self.document)

    def toggle_cycle_links(self):
        if len(self.link_indices) != 0:
            self.cycling = True
            self.highlight_idx = 0



    def cycle_link(self) -> None:
        #self.log("IDX INCREMENTED {}({}) -> {}({})".format(self.highlight_idx, self.link_indices[old], self.highlight_idx, self.link_indices[new]))
        self.highlight_idx = self.highlight_idx+1
        if self.highlight_idx == len(self.link_indices):
            self.highlight_idx = -1
            self.cycling = False

    def get_highlighted(self):
        if(self.cycling):
            return self.link_indices[self.highlight_idx]
        else:
            return -1

    def get_highlighted_link(self):
        return self.links[self.highlight_idx]

    def _format_body(self):
        if self.doc_type == "text/gemini":
            return self._format_parsed_gem(self.body)
        elif self.doc_type == "text/plain":
            return self.body

    def render(self) -> Panel:
        self.log(self.body)
        formatted_body = self._format_body()
        self.log(self.log(formatted_body))
        return Panel(formatted_body,
                     box=box.MINIMAL)
