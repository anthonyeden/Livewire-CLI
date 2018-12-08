"""Livewire Routing CLI: A command line interface for Livewire Routing Protocol Devices"""

__author__ = "Media Realm"
__copyright__ = "Copyright 2015-2018, Anthony Eden / Media Realm"
__credits__ = ["Anthony Eden"]
__license__ = "Proprietary"
__version__ = "1.0.1"

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/libs")

import time
import argparse
from LWRPClient import LWRPClient
import AxiaLivewireAddressHelper
import LivewireCLILogging

if __name__ == "__main__":

    description = "Livewire Routing Command Line Interface (CLI). " + "\r\n"
    description += __copyright__ + ". \r\n"
    description += "Version " + __version__ + ". \r\n"
    description += "This software is sold under a proprietary license. Please purchase a license from https://mediarealm.com.au/. " + "\r\n"

    # Setup Argparser
    parser = argparse.ArgumentParser(description=description)

    # Default connection parameters
    parser.add_argument("lwrp_ip", help="Enter the IP Address of your LWRP Device")
    parser.add_argument("-p", "--lwrp_password", metavar="PASSWORD", help="The Password for your LWRP Device")
    #parser.add_argument("-f", "--format", choices=["TEXT", "JSON"], default="TEXT", help="Enter 'json' or 'text'")
    
    # Specify which port on the device we're going to be dealing with
    parser.add_argument("--sourcenum", type=int, help="Enter the input channel number for your physical device")
    parser.add_argument("--destinationnum", type=int, help="Enter the output channel number for your physical device")
    parser.add_argument("--gpio_port_num", type=int, help="Enter the GPIO port number for your physical device")
    parser.add_argument("--gpio_pin_num", type=int, help="Enter the GPIO pin number for your physical device")

    # Options to get data
    parser.add_argument('--get_name', default=False, action='store_true', help="Get the current name of the specified channel")
    parser.add_argument('--get_ch', default=False, action='store_true', help="Get the current channel number (raw) of the specified channel")
    parser.add_argument('--get_chlw', default=False, action='store_true', help="Get the current Livewire Stream Number of the specified channel")
    parser.add_argument('--get_chlwtype', default=False, action='store_true', help="Specify the Livewire Stream Type for the specified channel")
    parser.add_argument('--get_gpiportstate', default=False, action='store_true', help="Get the current state of all pins on the GPI port")
    parser.add_argument('--get_gpipinstate', default=False, action='store_true', help="Get the current state of one specified pin on the GPI port")
    parser.add_argument('--get_gpoportstate', default=False, action='store_true', help="Get the current state of all pins on the GPO port")
    parser.add_argument('--get_gpopinstate', default=False, action='store_true', help="Get the current state of one specified pin on the GPO port")

    # Options to set data
    #parser.add_argument('--set_name', type=str, metavar="NAME", help="Change the name of the specified channel")
    parser.add_argument('--set_ch', type=str, metavar="XXX.XXX.XXX.XXX", help="Change the current channel number (raw) of a specified channel")
    parser.add_argument('--set_chlw', type=int, metavar="123", help="Change the Livewire Stream Number of the specified channel")
    parser.add_argument('--set_chlwtype', type=str, default="standard", choices=["standard", "livestream", "backfeed_standard", "backfeed_livestream", "surround"], help="Specify the Livewire Stream Type for the specified channel")
    #parser.add_argument('--set_gpiportstate', type=str, metavar="XXXXX", help="Change the state of all pins on the GPIO port")
    parser.add_argument('--set_gpipinstate', type=str, choices=["HIGH", "LOW"], help="Change the state of one specified pin on the GPO port")
    #parser.add_argument('--set_gpoportstate', type=str, metavar="XXXXX", help="Change the state of all pins on the GPIO port")
    parser.add_argument('--set_gpopinstate', type=str, choices=["HIGH", "LOW"], help="Change the state of one specified pin on the GPO port")
    parser.add_argument('--set_gpiomomentary', default=False, action='store_true', help="Specify this option to make this a momentary GPIO trigger")

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
        LivewireCLILogging.info("Attempting to connect to IP", args.lwrp_ip)
        device = LWRPClient(args.lwrp_ip, 93)
    except Exception, e:
        LivewireCLILogging.critical("Unable to connect", e.message)
        sys.exit(1)

    device.errorSub(LivewireCLILogging.error)

    if args.lwrp_password:
        LivewireCLILogging.info("Attempting to login with password", args.lwrp_password)
        device.login(args.lwrp_password)
    else:
        LivewireCLILogging.info("Attempting to login without password")
        device.login()

    # Source information
    if args.sourcenum and (args.get_name or args.get_ch or args.get_chlw or args.get_chlwtype):
        sources = device.sourceData()
        for source in sources:
            if int(source['num']) == args.sourcenum:
                if args.get_name:
                    print source['attributes']['name']
                
                if args.get_ch:
                    print source['attributes']['rtp_destination']
                
                if args.get_chlw:
                    print AxiaLivewireAddressHelper.multicastAddrToStreamNum(source['attributes']['rtp_destination'])
                
                if args.get_chlwtype:
                    print AxiaLivewireAddressHelper.streamFormatFromMulticastAddr(source['attributes']['rtp_destination'])

    # Destination information
    if args.destinationnum and (args.get_name or args.get_ch or args.get_chlw or args.get_chlwtype):
        destinations = device.destinationData()
        for destination in destinations:
            if int(destination['num']) == args.destinationnum:
                if args.get_name:
                    print destination['attributes']['name']
                
                if args.get_ch:
                    print destination['attributes']['address']
                
                if args.get_chlw:
                    print AxiaLivewireAddressHelper.multicastAddrToStreamNum(destination['attributes']['address'])
                
                if args.get_chlwtype:
                    print AxiaLivewireAddressHelper.streamFormatFromMulticastAddr(destination['attributes']['address'])

    # Set source
    if args.sourcenum and args.set_ch:
        # Send the raw data
        device.setSource(args.sourcenum, args.set_ch)
    elif args.sourcenum and args.set_chlw:
        # Take a LW channel number and turn it into a Multicast Address of the correct type
        channel_addr = AxiaLivewireAddressHelper.streamNumToMulticastAddr(args.set_chlw, args.set_chlwtype)
        device.setSource(args.sourcenum, channel_addr)
    
    # Set destination
    if args.destinationnum and args.set_ch:
        # Send the raw data
        device.setDestination(args.destinationnum, args.set_ch)
    elif args.destinationnum and args.set_chlw:
        # Take a LW channel number and turn it into a Multicast Address of the correct type
        channel_addr = AxiaLivewireAddressHelper.streamNumToMulticastAddr(args.set_chlw, args.set_chlwtype)
        device.setDestination(args.destinationnum, channel_addr)

    elif (not args.sourcenum or not args.destinationnum) and (args.get_name or args.get_ch or args.get_chlw or args.get_chlwtype):
        LivewireCLILogging.error("Source/Destination Number parameter not specified")
    

    # Get GPI Port/Pin data
    if args.gpio_port_num and (args.get_gpiportstate or (args.gpio_pin_num and args.get_gpipinstate)):
        ports = device.GPIData()
        for port in ports:
            if int(port['num']) == args.gpio_port_num and args.get_gpiportstate:
                # Combine all pins into one string XXXXX
                pinStr = ""
                for pin in port['pin_states']:
                    if pin['state'] == "high":
                        pinStr += "H"
                    elif pin['state'] == "low":
                        pinStr += "L"
                print pinStr
            elif int(port['num']) == args.gpio_port_num and args.get_gpipinstate:
                # Output one string as 'HIGH' or 'LOW'
                print port['pin_states'][args.gpio_pin_num]['state'].upper()
    
    # Get GPO Port/Pin data
    if args.gpio_port_num and (args.get_gpoportstate or (args.gpio_pin_num and args.get_gpopinstate)):
        ports = device.GPOData()
        for port in ports:
            if int(port['num']) == args.gpio_port_num and args.get_gpoportstate:
                # Combine all pins into one string XXXXX
                pinStr = ""
                for pin in port['pin_states']:
                    if pin['state'] == "high":
                        pinStr += "H"
                    elif pin['state'] == "low":
                        pinStr += "L"
                print pinStr
            elif int(port['num']) == args.gpio_port_num and args.get_gpopinstate:
                # Output one string as 'HIGH' or 'LOW'
                print port['pin_states'][args.gpio_pin_num]['state'].upper()

    # Set GPI Pin Data
    if args.gpio_port_num and args.gpio_pin_num and args.set_gpipinstate:
        
        # If it's momentary, store the current state
        if args.set_gpiomomentary:
            returnState = None
            for port in device.GPIData():
                if int(port['num']) == args.gpio_port_num:
                    # Get the current state
                    returnState = port['pin_states'][args.gpio_pin_num]['state']

        # Change the pin state
        device.setGPI(args.gpio_port_num, args.gpio_pin_num, args.set_gpipinstate.lower())

        if args.set_gpipmomentary and returnState is not None:
            time.sleep(1)
            device.setGPI(args.gpio_port_num, args.gpio_pin_num, returnState)

    # Set GPO Pin Data
    if args.gpio_port_num and args.gpio_pin_num and args.set_gpopinstate:

        # If it's momentary, store the current state
        if args.set_gpiomomentary:
            returnState = None
            for port in device.GPOData():
                if int(port['num']) == args.gpio_port_num:
                    # Get the current state
                    returnState = port['pin_states'][args.gpio_pin_num]['state']

        device.setGPO(args.gpio_port_num, args.gpio_pin_num, args.set_gpopinstate.lower())

        if args.set_gpiomomentary and returnState is not None:
            time.sleep(1)
            device.setGPO(args.gpio_port_num, args.gpio_pin_num, returnState)

    # Disconnect from the LWRP
    time.sleep(0.4)
    device.stop()
    sys.exit(0)
