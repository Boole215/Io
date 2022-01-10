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

    ignore_gem_rules = False

    def __init__(self):
        # generate a client cert just in case
        self.cert = lagcerts.generate_client_cert()


    def prompt_for_safety():
        return 0

    def make_start_page(self):
        return self._make_placeholder(start_page)

    def _make_placeholder(self, body):
        return (DisplayForm("text/gemini", self._parse_gmi(body.decode(encoding = "utf-8")), {"charset":"utf-8"}),
                "//CLIENT//")


    def _gmi_parse_line(self, line):


        if line == "```" and not self.ignore_gem_rules:
            self.ignore_gem_rules = True
            return ('', "plain")

        elif line == "```" and self.ignore_gem_rules:
            self.ignore_gem_rules = False
            return ('', "plain")


        if self.ignore_gem_rules:
            return (line, "plain")

        text_parts = [x for x in line.split(" ") if x != " " and x != '']

        if not text_parts:
            return ("\n", "nl")

        if text_parts[0] == "=>":

            if '\t' in text_parts[1]:
                text_parts[1] = text_parts[1].split('\t')
                text_parts[1] = [x for x in text_parts[1] if x != '']

            #netlog.debug(text_parts[1])

            if type(text_parts[1]) != str:
                text_parts = [text_parts[0]] + text_parts[1] + text_parts[2:]

            #netlog.debug("text_parts: {}".format(text_parts))

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
            pieces = [x.strip() for x in MIME.split(';') if x != ' ']
            text_type = pieces[0]


            if not pieces[1:]:
                return (text_type, {"charset":"utf-8"})
            elif pieces:
                properties = [x.split("=") for x in pieces[1:]]
                prop_dict = {}
                for prop in properties:
                    prop_dict[prop[0]] = prop[1]

                if not "charset" in properties:
                    prop_dict["charset"] = "utf-8"

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


    def _parse_query(self, query, relative = None):
        GEM_LEN = 9

        #TODO: Do this using .find("://") rather than harcoding it only to work with gemini://

        # Find the end of the protocol
        netlog.debug("Searching for '://' in {}".format(query))
        protocol_end = query.find("://")

        if protocol_end == -1:
            protocol_end = GEM_LEN
            query = "gemini://" + query
            netlog.debug("New query: {}".format(query))
        else:
            protocol_end += 3

        netlog.debug("Protocol end: {}".format(protocol_end))
        # split the query up into parts

        protocol = query[0:protocol_end]
        core = [x for x in query[protocol_end:].split('/') if x != '']
        host = core[0]

        netlog.debug("Protocol:{}\nCore:{}\nHost:{}".format(protocol, core, host))
        netlog.debug("Relative:{}".format(relative))

        # Account for: Files on the same directory
        #              Prev directory
        #              Deeper directory
        #              Combo of Prev and Deeper
        if relative != None:
            idx = len(core)-1

            relatives = [x for x in relative.split('/') if x != '']
            netlog.debug("Core: {}".format(core))
            netlog.debug("Relatives: {}".format(relatives))


            #TODO: Maintaining an index for where we are in the list doesn't seem
            #      like it's completely necessary, experiment on getting this to
            #      work without it.

            #TODO: Take into account that a directory may also have a '.' in it (maybe?)

            for element in relatives:
                # Move up the file hierarchy
                if element == "..":
                    if '.' in core[-1]:
                        core.pop()
                        idx -= 1

                    core.pop()
                    idx -= 1
                    netlog.debug("Moving up hierarchy: {}".format(core))
                elif element == ".":
                    if "." in core[-1]:
                        core.pop()
                        idx -= 1
                elif "." in element:
                    if "." in core[-1]:
                        core[idx] = element
                    else:
                        core.append(element)
                    # media is in the same directory
                    netlog.debug("{} is a file name right?".format(element))
                else:
                    # must be a directory name, just append it
                    netlog.debug("{} is a directory name right?".format(element))
                    core.append(element)
                    idx += 1

        # If the top level item isn't a file and it doesn't have a trailing slash,
        # add it

        netlog.debug("Core after relative parsing: {}".format(core))
        if len(core) > 1:
            if not '.' in core[-1] and core[-1].find('/') == -1:
                netlog.debug("Adding a trailing slash")
                core[-1] += '/'
        else:
            if core[0][-1] != '/':
                netlog.debug("Adding a trailing slash")
                core[-1] += '/'

        query = protocol + '/'.join(core)

        netlog.debug("Final query: {}".format(query))
        return (host, query)


    def get_page(self, URL, relative=None,cert=None):
        if URL == "start://":
            return self.get_start_page()

        host, query = self._parse_query(URL, relative)
        netlog.debug("Host: {}\n\tURL: {}".format(host, query))
        try:
            page_conn = Connection(host, query)

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
        netlog.debug("Response code type: {}x".format(response.code[0:1]))

        if response.code[0:1] == b'2':

            parsed_mime = self._parse_response(response.MIME, response.body)
            netlog.debug("Parsed MIME: {}".format(parsed_mime))
            netlog.debug("query to return: {}".format(query))
            return (DisplayForm(parsed_mime[0], parsed_mime[1],
                                parsed_mime[2]),
                    query)
        elif response.code[0:1] == b'4':
            return self._make_placeholder(status_4x_perm_fail)
        elif response.code[0:1] == b'5':
            return self._make_placeholder(status_5x_perm_fail)
        else:
            return self._make_placeholder(invalid_host_page)
