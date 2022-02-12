import logging


logging.basicConfig(
    filename='sbotify.log', level=logging.DEBUG,
    datefmt='%y-%m-%d %H:%M:%S', format='%(asctime)s | %(levelname)5s | %(message)s')
# logging.getLogger('asyncio').setLevel(logging.WARNING)


def log_info(msg):
    logging.info(msg)


def log_debug(msg):
    logging.debug(msg)


def log_error(msg):
    logging.error(msg)