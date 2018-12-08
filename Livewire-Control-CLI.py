"""Livewire Control CLI: A command line interface for Livewire Control Protocol Devices"""

__author__ = "Media Realm"
__copyright__ = "Copyright 2015-2018, Anthony Eden / Media Realm"
__credits__ = ["Anthony Eden"]
__license__ = "Proprietary"
__version__ = "1.0.1"

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/libs")

import time
import argparse
from LWCPClient import LWCPClient
import AxiaLivewireAddressHelper
import LivewireCLILogging

if __name__ == "__main__":

    description = "Livewire Control Command Line Interface (CLI). " + "\r\n"
    description += __copyright__ + ". \r\n"
    description += "Version " + __version__ + ". \r\n"
    description += "This software is sold under a proprietary license. Please purchase a license from https://mediarealm.com.au/. " + "\r\n"

    # Setup Argparser
    parser = argparse.ArgumentParser(description=description)

    # Default connection parameters
    parser.add_argument("lwcp_ip", help="Enter the IP Address of your LWCP Device")
    
    # Logging parameters
    parser.add_argument('--debug', default=False, action='store_true', help="Specify this option to see debug/error output on the console")
    parser.add_argument('--disable_logging', default=False, action='store_true', help="Specify this option to disable logging to a file")
    
    # Parse parameters
    args = parser.parse_args()

    # Setup the logger
    if args.debug:
        LivewireCLILogging.setupLogger(True)
    else:
        LivewireCLILogging.setupLogger(False)
    
    if args.disable_logging:
        LivewireCLILogging.disableLogging()
    
    # Log all exceptions
    sys.excepthook = LivewireCLILogging.exception

    # Trim all arguments
    for arg in vars(args):
        if isinstance(getattr(args, arg), str):
            setattr(args, arg, getattr(args, arg).strip())

    # Attempt to connect
    try:
        LivewireCLILogging.info("Attempting to connect to IP", args.lwcp_ip)
        device = LWCPClient(args.lwcp_ip, 93)
    except Exception, e:
        LivewireCLILogging.critical("Unable to connect", e.message)
        sys.exit(1)

    device.errorSub(LivewireCLILogging.error)


    # Disconnect from the LWCP
    time.sleep(0.4)
    device.stop()
    sys.exit(0)
