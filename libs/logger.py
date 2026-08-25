import logging

class Logger:
	log = logging.basicConfig(format="%(level_name)s:%(message)s", level=logging.DEBUG)
