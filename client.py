import connection, lagcerts
from connection import Connection, Response
class Client:

    cur_page = ""
    tabs = []

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


    def get_page(self, URL, cert=None):
        page_conn = Connection(URL)
        #print("Conneciton created")
        if page_conn.need_to_prompt():
            if input("Unsafe maybe, continue? y/n: ") != 'y':
                return 1

        page_conn.send_request()
        #print("Receiving response")
        response = page_conn.receive_response()
        return response
