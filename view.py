import py_cui, client

text= b'# \033[33mProject Gemini\033[0m\n\n## Announcement\n\nThe mailing list is currently down due to a hardware failure.  It will reappear in some form or another as soon as possible.  Watch this space.\n\n## Overview\n\nGemini is a new internet protocol which:\n\n* Is heavier than gopher\n* Is lighter than the web\n* Will not replace either\n* Strives for maximum power to weight ratio\n* Takes user privacy very seriously\n\n## Resources\n\n=> docs/\tGemini documentation\n=> software/\tGemini software\n=> servers/\tKnown Gemini servers\n=> https://lists.orbitalfox.eu/listinfo/gemini\tGemini mailing list\n=> gemini://gemini.conman.org/test/torture/\tGemini client torture test\n\n## Web proxies\n\n=> https://portal.mozz.us/?url=gemini%3A%2F%2Fgemini.circumlunar.space%2F&fmt=fixed\tGemini-to-web proxy service\n=> https://proxy.vulpes.one/gemini/gemini.circumlunar.space\tAnother Gemini-to-web proxy service\n\n## Search engine\n\n=> gemini://geminispace.info/\tgeminispace.info\n\n## Geminispace aggregators\n\n=> capcom/\tCAPCOM\n=> gemini://rawtext.club:1965/~sloum/spacewalk.gmi\tSpacewalk\n=> gemini://calcuode.com/gmisub-aggregate.gmi\tgmisub\n=> gemini://caracolito.mooo.com/deriva/\tBot en deriva (Spanish language content)\n\n## Gemini mirrors of web resources\n\n=> gemini://gempaper.strangled.net/mirrorlist/\tA list of mirrored services\n\n## Free Gemini hosting\n\n=> users/\tUsers with Gemini content on this server\n'

# Add line parsing functionality
def parse_line(line):
    #for text in line:
    return

def parse_page(raw_gem):
    ret_str = ""
    for line in raw_gem.split(b'\n'):
        ret_str += line.decode() + "\n"

    #return list(map(lambda x: x.decode(), raw_gem.split(b'\n')))
    return ret_str

#parse_page(main)

class LagannApp:

    def __init__(self, master):
        #self.client = user
        self.master = master
        # Add binding to brind up the search bar
        #self.master.add_key_command(py_cui.keys.KEY_S_LOWER, self.show_search_bar)

        #self.master.add_text_box("", 0, 0, column_span = 20, initial_text="startpage")
        self.master.add_block_label(parse_page(text), 0, 0, row_span = 10, column_span=10, center=False)
        #self.master.add_text_block("Circumlunar",0,0, row_span = 10, column_span = 10, initial_text=parse_page(text))
        #self.cur_page = parse_page(text)
        #self.scroll_menu = self.master.add_scroll_menu("Ah", 0,0, row_span = 10, column_span = 10)
        #self.scroll_menu.add_item_list(self.cur_page)
        #self.scroll_menu.set_color_mode(57)


       # self.block_label.set_selectable(True)

    def show_search_bar(self):
        self.master.show_text_box_popup("Search", self.nothing);

    def nothing(self, x):
        return

def main():
    root = py_cui.PyCUI(10,10)
    #root._grid._offset_y = -2
    #root.toggle_unicode_borders()
    root.set_title("Lagann")
    wrapper =  LagannApp(root)
    root.start()

main()
