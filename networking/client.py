from networking import lagcerts
from networking.connection import Connection, Response
from networking.errors import InvalidHostError

invalid_host_page = b'# Host not found\nPlease make sure the address is correct.\n'

class Client:

    def __init__(self):
        # generate a client cert just in case
        self.cert = lagcerts.generate_client_cert()

    def prompt_for_safety():
        # prompt user using ncurses
        if user_in == "Y" or user_in == "y":
            return 1
        elif user_in == "N" or user_in == "n":
            return 0
        else:
            # tell user to use right response
            return 0

    def _make_dummy_response(self, body):
        return Response("20", b"gemini/text", body)

    def get_page(self, URL, cert=None):
        try:
            page_conn = Connection(URL)

            if page_conn.need_to_prompt():
                if input("Unsafe maybe, continue? y/n: ") != 'y':
                    return 1

            page_conn.send_request()
            #print("Receiving response")
            response = page_conn.receive_response()
            page_conn.close_connection()
            return response

        except InvalidHostError:
            return self._make_dummy_response(invalid_host_page)
