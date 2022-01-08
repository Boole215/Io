import logging
logging.basicConfig(filename='networking.log', filemode='w', format='%(asctime)s:\n  %(name)s - %(levelname)s - %(message)s\n')



netlog = logging.getLogger()
netlog.setLevel(logging.DEBUG)
