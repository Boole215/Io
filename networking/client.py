from networking import lagcerts
from networking.connection import Connection, Response
from networking.errors import InvalidHostError, MetaOverflowError

from networking.log import netlog

from dataclasses import dataclass

@dataclass
class DisplayForm:
    media_type: str
    content: str
    properties: str

from networking.log import netlog

invalid_host_page = b'# Host not found\nPlease make sure the address is correct.\n'

start_page = b'# Welcome Page\nWelcomeeee, here are some useful keybinds for you:\n* C-Q - quit\n* C-S - Toggles the search bar (click the search bar to type in it, and onto the document body to stop)\n* l - cycles through links present on the current page\nThose are all the binds we have for now,\nRemember what they say:\n> Poop.\n=> gemini://gemini.circumlunar.space/ sample link'

server_error_page = b'# Server configuration error\nIt seems that the server responded with a Meta tag that was greater than 1024 characters.\nIf you believe this is a mistake please submit a bug report.'


"""
Stock pages for non-'2x' server status in response
"""
# Format response's meta into page
status_1x_input = b'# P}age desires input:\n{}'

status_3x_redirect = b"# Redirecting...\n"

# Format code into string, as well as meta response;s
status_4x_temp_fail = b"# {}: Temporary Failure\n{}"

status_5x_perm_fail = b"# {}: Permanent Failure\n"

status_6x_cert_req = b"# Client certificate required, retrying..."

class Client:

    def __init__(self):
        # generate a client cert just in case
        self.cert = lagcerts.generate_client_cert()


    def prompt_for_safety():
        return 0

    def make_start_page(self):
        return self._make_placeholder(start_page)

    def _make_placeholder(self, body):
        return DisplayForm("text/gemini", self._parse_gmi(body.decode(encoding = "utf-8")), {"charset":"utf-8"})


    def _gmi_parse_line(self, line):
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


    def _parse_gmi(self, raw_gem):
        lines = raw_gem.split('\n')
        parsed_lines = []
        ret_str = ""
        link_indices = []
        links = []
        idx = 0

        for line in lines:
            ret_str += line

        for line in lines:
            pl = self._gmi_parse_line(line)
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

    # E.x.
    # text/gemini
    # text/gemini; lang=en
    # text/gemini; charset=utf-8; lang=en
    #
    def _parse_MIME(self, MIME):
        MIME = MIME.decode("utf-8")
        if "text" in MIME:
            pieces = [x for x in MIME.split(';') if x != ' ']
            text_type = pieces[0]


            if not pieces[1:]:
                return (text_type, {"charset":"utf-8"})
            elif pieces:
                properties = [x.split("=") for x in pieces[1:]]
                prop_dict = {}
                for prop in properties:
                    prop_dict[prop[0]] = prop[1]

                return (text_type, prop_dict)
        else:
            return (MIME, {})


    def _parse_response(self, MIME, content):
        doc_type, properties = self._parse_MIME(MIME)
        # TODO: take into account mediatypes
        if doc_type == "text/gemini":
            content = self._parse_gmi(content.decode(encoding = properties["charset"]))

        elif 'text/plain' == doc_type:
            if not "charset" in properties:
                content = content.decode(encoding="utf-8")
            else:
                #TODO Error checking in case of invalid properties?
                content = content.decode(encoding = properties["charset"])
        else:
            content = content.decode()
        return (doc_type, content, properties)





    def get_page(self, URL, cert=None):
        if URL == "start://":
            return self.get_start_page()

        try:
            page_conn = Connection(URL)

        except InvalidHostError:
            return self._make_placeholder(invalid_host_page)

        if page_conn.need_to_prompt():
            netlog.debug("Unsafe")


        page_conn.send_request()
        #print("Receiving response")
        try:
            response = page_conn.receive_response()
        except MetaOverflorError:
            page_conn.close_connection()
            return self._make_placeholder(server_error_page)

        page_conn.close_connection()

        netlog.debug("response from {}: {}".format(URL, response))
        netlog.debug(response.code[0])

        if response.code[0:1] == b'2':

            parsed_mime = self._parse_response(response.MIME, response.body)
            netlog.debug(parsed_mime)
            return DisplayForm(parsed_mime[0], parsed_mime[1],
                               parsed_mime[2])
        elif response.code[0:1] == b'4':
            return self._make_placeholder(status_4x_perm_fail)
        elif response.code[0:1] == b'5':
            return self._make_placeholder(status_5x_perm_fail)
        else:
            return self._make_placeholder(invalid_host_page)
