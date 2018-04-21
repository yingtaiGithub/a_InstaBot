import logging
from logging.handlers import RotatingFileHandler

# Logging for Instagram Bot
insta_logFile = 'log/insta.log'

logger = logging.getLogger('insta_bot')

formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

stream_handler = logging.StreamHandler()
# file_handler1 = logging.FileHandler('log/.log', 'w', 'utf-8')
file_handler1 = RotatingFileHandler(insta_logFile, mode='a', maxBytes=5*1024*1024,
                                 backupCount=2, encoding=None, delay=0)

stream_handler.setFormatter(formatter)
file_handler1.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler1)
logger.setLevel(logging.DEBUG)


# # Logging for Auto Emailing
# email_logFile = 'log/email.log'
#
# email_logger = logging.getLogger('email_bot')
#
# formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
#
# stream_handler = logging.StreamHandler()
# # file_handler1 = logging.FileHandler('log/.log', 'w', 'utf-8')
# file_handler2 = RotatingFileHandler(email_logFile, mode='a', maxBytes=5*1024*1024,
#                                  backupCount=2, encoding=None, delay=0)
#
# stream_handler.setFormatter(formatter)
# file_handler2.setFormatter(formatter)
#
# email_logger.addHandler(stream_handler)
# email_logger.addHandler(file_handler2)
# email_logger.setLevel(logging.DEBUG)







