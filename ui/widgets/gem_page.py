from rich.panel import Panel
from rich.text import Text
from rich import box

from textual import events
from textual.widget import Widget
from textual.reactive import Reactive

class GemPage(Widget):
    highlight_idx = Reactive(-1)
    cycling = Reactive(False)
    link_indices = Reactive([])
    url = ""
    document = Reactive("")


    def __init__(self, page, url):
        super().__init__()
        self.url = url
        self.link_indices, self.links, self.document = self._parse_page(page)

    def prettify_parsed_gem(self, gem_page):
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


    def _parse_line(self, line):
        text_parts = [x for x in line.split(" ") if x != " " and x != '']
        if not text_parts:
            return ("\n", "nl")

        if text_parts[0] == "=>":
            text_parts = [x if '\t' not in x else x.split('\t') for x in text_parts]
            if type(text_parts[1]) != str:
                text_parts = [text_parts[0]] + text_parts[1] + text_parts[2:]
            return ((text_parts[1], " ".join(text_parts[2:])), 'link')

        elif text_parts[0] == ">":
            return (" ".join(text_parts[1:]), "quote")
        elif text_parts[0] == "*":
            return(line, "list")
        elif len([x for x in text_parts[0] if x != "#"]) == 0:
            if text_parts[0] == "#":
                return (line, "h1")
            elif text_parts[0] == "##":
                return (line, "h2")
            elif text_parts[0] == "###":
                return (line, "h3")
        else:
            return (line, "plain")

    def _parse_page(self, raw_gem):
        lines = raw_gem.decode().split('\n')
        parsed_lines = []
        ret_str = ""
        link_indices = []
        links = []
        idx = 0

        for line in lines:
            ret_str += line

        for line in lines:
            pl = self._parse_line(line)
            if pl[1] == "link":
                link_indices.append(idx)
                links.append(pl[0][0])
                parsed_lines.append((pl[0][1], pl[1]))
            else:
                parsed_lines.append((pl[0], pl[1]))

                idx += 1


        #return raw_gem.decode().split("\n")
        #return ret_str
        return (link_indices, links, parsed_lines)

    def render(self) -> Panel:
        #self.log(self.document)
        return Panel(self.prettify_parsed_gem(self.document),
                     box=box.MINIMAL)
