import logging

def sigint(arg1, arg2):
    logging.debug("received SIGINT")

def sigquit(arg1, arg2):
    logging.debug("received SIGQUIT")

def sigtstp(arg1, arg2):
    logging.debug("received SIGTSTP")

def sigstop(arg1, arg2):
    logging.debug("recieved SIGSTOP")
