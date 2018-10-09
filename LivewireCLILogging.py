""" LivewireCLILogging: A simple global logger for use across Livewire-CLI """

import os, sys
import platform
import logging
from logging.handlers import TimedRotatingFileHandler
import inspect
import random

# This is a module-level variable so it's always accessible by someone loading this module
logger = None
debug_output_enabled = False

def setupLogger(debugEnabled = False):
    # Setup the logger
    global logger
    global debug_output_enabled

    logger = logging.getLogger()
    logger_formatter = logging.Formatter('%(asctime)s ['+str(random.randint(1000,9999))+'] %(levelname)-8s %(message)s')

    # Add a handler to show the INFO output on the console
    if debugEnabled:
        handler_console = logging.StreamHandler(sys.stdout)
        handler_console.setLevel(logging.INFO)
        handler_console.setFormatter(logger_formatter)
        logger.addHandler(handler_console)
        debug_output_enabled = True

    if platform.system() == "Darwin":
        appdata_path_base = "~/Library/"
    else:
        appdata_path_base = os.environ['ALLUSERSPROFILE']

    try:
        if not os.path.exists(os.path.join(appdata_path_base, "Media Realm", "Livewire-CLI")):
            os.makedirs(os.path.join(appdata_path_base, "Media Realm", "Livewire-CLI"))
    except Exception, e:
        critical('%s %s %s' % ("Could not create directory", os.path.join(appdata_path_base, "Media Realm", "Livewire-CLI"), e))

    else:

        handler_file = TimedRotatingFileHandler(os.path.join(appdata_path_base, "Media Realm", "Livewire-CLI", "Livewire-CLI.log"), when="midnight", backupCount=14)
        handler_file.suffix = "%Y-%m-%d"
        handler_file.setFormatter(logger_formatter)
        handler_file.setLevel(logging.DEBUG)
        
        logger.addHandler(handler_file)
        logger.setLevel(logging.DEBUG)

        debug("The logger has started successfully")

def disableLogging():
    global logger
    global debug_output_enabled

    logger.handlers = []
    logger.addHandler(logging.NullHandler())

    if debug_output_enabled:
        handler_console = logging.StreamHandler(sys.stdout)
        handler_console.setLevel(logging.INFO)
        logger_formatter = logging.Formatter('%(asctime)s ['+str(random.randint(1000,9999))+'] %(levelname)-8s %(message)s')
        handler_console.setFormatter(logger_formatter)
        logger.addHandler(handler_console)

def info(msg, *args):
    # Log something at INFO level
    # We support any number of arguments, to make replacing PRINT statements easier
    global logger

    frame_records = inspect.stack()[1]
    calling_module = inspect.getmodulename(frame_records[1])

    for item in args:
        msg += " " + str(item.encode('ascii', errors='ignore'))
    
    # Log to the global logger
    logger.info('[%s] %s' % (calling_module, msg))

def debug(msg):
    # Log something at DEBUG level
    global logger

    frame_records = inspect.stack()[1]
    calling_module = inspect.getmodulename(frame_records[1])

    # Log to the global logger
    logger.debug('[%s] %s' % (calling_module, msg))

def warning(msg):
    # Log something at WARNING level
    global logger

    frame_records = inspect.stack()[1]
    calling_module = inspect.getmodulename(frame_records[1])

    # Log to the global logger
    logger.warning('[%s] %s' % (calling_module, msg))

def error(msg):
    # Log something at ERROR level
    global logger

    frame_records = inspect.stack()[1]
    calling_module = inspect.getmodulename(frame_records[1])

    # Log to the global logger
    logger.error('[%s] %s' % (calling_module, msg))

def critical(msg, *args):
    # Log something at CRITICAL level
    global logger

    frame_records = inspect.stack()[1]
    calling_module = inspect.getmodulename(frame_records[1])

    for item in args:
        msg += " " + str(item.encode('ascii', errors='ignore'))

    # Log to the global logger
    logger.critical('[%s] %s' % (calling_module, msg))

def exception(exc_type, exc_value, exc_traceback):
    # Log an unhandled EXCEPTION
    global logger

    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Log to the global logger
    logger.critical("Unhandled Exception", exc_info = (exc_type, exc_value, exc_traceback))
    sys.exit(2)
