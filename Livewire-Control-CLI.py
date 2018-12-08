"""Livewire Control CLI: A command line interface for Livewire Control Protocol Devices"""

__author__ = "Media Realm"
__copyright__ = "Copyright 2015-2018, Anthony Eden / Media Realm"
__credits__ = ["Anthony Eden"]
__license__ = "Proprietary"
__version__ = "1.1.0"

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
    
    # Show Profile get/set
    parser.add_argument('--get_showprofile', default=False, action='store_true', help="Get the name and ID of the current show profile")
    parser.add_argument('--get_showprofiles', default=False, action='store_true', help="Get the names and IDs of all configured show profiles")
    parser.add_argument("--set_showprofile", type=int, help="Specify the ID of a Show Profile, to change the active show profile on the desk")

    # Specify fader number
    parser.add_argument("--fadernum", type=int, help="Enter the fader number you wish to control")
    parser.add_argument("--faderlivewire", type=int, help="Enter the Livewire channel number you wish to control on the console")

    # Source Profile get/set
    parser.add_argument('--get_sourceprofile', default=False, action='store_true', help="Get the name and ID of the current source profile")
    parser.add_argument('--get_sourceprofiles', default=False, action='store_true', help="Get the names and IDs of all available source profiles for the selected channel")
    parser.add_argument("--set_sourceprofile", type=int, help="Specify the ID of a Source Profile, to change the active source profile for the selected channel")

    # Various fader channel states
    parser.add_argument('--get_channelstate', default=False, action='store_true', help="Get the on/off button state of the currently selected channel")
    parser.add_argument('--set_channelstate', type=str, choices=["ON", "OFF"], help="Change the on/off button state for the currently selected channel")
    parser.add_argument('--get_fadergain', default=False, action='store_true', help="Get the fader gain level of the currently selected channel")
    parser.add_argument('--set_fadergain', type=int, help="Set the fader gain level for the currently selected channel")
    parser.add_argument('--get_channelbus', type=str, choices=["ALL", "PGM1", "PGM2", "PGM3", "PGM4", "PREV"], help="Get the bus assignment of the currently selected channel")
    parser.add_argument('--set_channelbus_pgm1', type=str, choices=["ON", "OFF"], help="Change the PGM1 Bus Assignment for the currently selected channel")
    parser.add_argument('--set_channelbus_pgm2', type=str, choices=["ON", "OFF"], help="Change the PGM1 Bus Assignment for the currently selected channel")
    parser.add_argument('--set_channelbus_pgm3', type=str, choices=["ON", "OFF"], help="Change the PGM1 Bus Assignment for the currently selected channel")
    parser.add_argument('--set_channelbus_pgm4', type=str, choices=["ON", "OFF"], help="Change the PGM1 Bus Assignment for the currently selected channel")
    parser.add_argument('--set_channelbus_prev', type=str, choices=["ON", "OFF"], help="Change the PGM1 Bus Assignment for the currently selected channel")

    # VMix
    parser.add_argument("--vmix_num", type=int, help="Enter the VMix number you wish to control")
    parser.add_argument("--vmix_chnum", type=int, help="Enter the VMix Channel number you wish to control")
    parser.add_argument('--get_vmixstate', default=False, action='store_true', help="Get the on/off state of the currently selected VMix channel")
    parser.add_argument('--set_vmixstate', type=str, choices=["ON", "OFF"], help="Change the on/off state for the currently selected VMix channel")
    parser.add_argument('--get_vmixgain', default=False, action='store_true', help="Get the on/off state of the currently selected VMix channel")
    parser.add_argument('--set_vmixgain', type=int, help="Set the gain level for the currently selected VMix channel")

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
        device = LWCPClient(args.lwcp_ip)
    except Exception, e:
        LivewireCLILogging.critical("Unable to connect", e.message)
        sys.exit(1)

    device.errorSub(LivewireCLILogging.error)


    # Show Profile - Get Current
    if args.get_showprofile:
        profile = device.getShowProfile()
        if profile is not None and len(profile) >= 1 and 'attributes' in profile[0] and 'profile_id' in profile[0]['attributes'] and 'profile_name' in profile[0]['attributes']:
            print "ActiveShowProfile:" + str(profile[0]['attributes']['profile_id']) + "=" + str(profile[0]['attributes']['profile_name'])

    # Show Profiles - Get All
    if args.get_showprofiles:
        profiles = device.getShowProfiles()
        if profiles is not None and len(profiles) >= 1 and 'attributes' in profiles[0] and 'profile_list' in profiles[0]['attributes']:
            for profile in profiles[0]['attributes']['profile_list']:
                print "ShowProfile:" + str(profile['id']) + "=" + str(profile['name'])

    # Show Profile - Set
    if args.set_showprofile:
        device.setShowProfile(args.set_showprofile)

    # Actions to do with console faders
    if args.fadernum or args.faderlivewire:

        if args.fadernum:
            chnum = args.fadernum
            chtype = 'fader'
        else:
            chnum = args.faderlivewire
            chtype = 'livewire'

        # Source Profile - Get Active
        if args.get_sourceprofile:
            source = device.getSourceProfile(chnum, chtype)
            if source is not None and len(source) >= 1 and 'attributes' in source[0]:
                for attr in source[0]['attributes']:
                    print "active_" + str(attr) + "=" +str(source[0]['attributes'][attr]) 

        # Source Profiles - Get All
        if args.get_sourceprofiles:
            sources = device.getSourceProfiles(chnum, chtype)
            if sources is not None and len(sources) >= 1 and 'attributes' in sources[0] and 'source_list' in sources[0]['attributes']:
                for source in sources[0]['attributes']['source_list']:
                    if 'lwch' in source:
                        lwch = "/Lw" + str(source['lwch'])
                    else:
                        lwch = ""
                    print "SourceProfile:" + str(source['id']) + lwch + "=" + str(source['name'])

        # Source Profile - Set
        if args.set_sourceprofile:
            device.setSourceProfile(chnum, args.set_sourceprofile, chtype)

        # Channel - State Get
        if args.get_channelstate:
            state = device.getChannelState(chnum, chtype)
            if state is not None and len(state) >= 1 and 'attributes' in state[0] and 'ChannelOn' in state[0]['attributes']:
                if state[0]['attributes']['ChannelOn'] is True:
                    print "ChannelOn"
                else:
                    print "ChannelOff"

        # Channel - State Set
        if args.set_channelstate and args.set_channelstate == "ON":
            device.setChannelState(chnum, True, chtype)
        elif args.set_channelstate and args.set_channelstate == "OFF":
            device.setChannelState(chnum, False, chtype)

        # Channel - Fader Level Get
        if args.get_fadergain:
            gain = device.getChannelGain(chnum, chtype)
            if gain is not None and len(gain) >= 1 and 'attributes' in gain[0] and 'fader_gain' in gain[0]['attributes']:
                print "FaderGain:" + str(gain[0]['attributes']['fader_gain'])

        # Channel - Fader Level Set
        if args.set_fadergain is not None:
            device.setChannelGain(chnum, args.set_fadergain, chtype)

        # Channel - Bus Get
        if args.get_channelbus:
            bus = device.getChannelBus(chnum, chtype)
            if bus is not None and len(bus) >= 1:
                for bus_info in bus:
                    if 'bus_pgm1' in bus_info['attributes'] and (args.get_channelbus == "PGM1" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_pgm1'] is True:
                        print "PGM1:ON"
                    elif 'bus_pgm1' in bus_info['attributes'] and (args.get_channelbus == "PGM1" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_pgm1'] is False:
                        print "PGM1:OFF"
                    
                    if 'bus_pgm2' in bus_info['attributes'] and (args.get_channelbus == "PGM2" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_pgm2'] is True:
                        print "PGM2:ON"
                    elif 'bus_pgm2' in bus_info['attributes'] and (args.get_channelbus == "PGM2" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_pgm2'] is False:
                        print "PGM2:OFF"
                    
                    if 'bus_pgm3' in bus_info['attributes'] and (args.get_channelbus == "PGM3" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_pgm3'] is True:
                        print "PGM3:ON"
                    elif 'bus_pgm3' in bus_info['attributes'] and (args.get_channelbus == "PGM3" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_pgm3'] is False:
                        print "PGM3:OFF"
                    
                    if 'bus_pgm4' in bus_info['attributes'] and (args.get_channelbus == "PGM4" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_pgm4'] is True:
                        print "PGM4:ON"
                    elif 'bus_pgm4' in bus_info['attributes'] and (args.get_channelbus == "PGM4" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_pgm4'] is False:
                        print "PGM4:OFF"
                    
                    if 'bus_prev' in bus_info['attributes'] and (args.get_channelbus == "PREV" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_prev'] is True:
                        print "PREV:ON"
                    elif 'bus_prev' in bus_info['attributes'] and (args.get_channelbus == "PREV" or args.get_channelbus == "ALL") and bus_info['attributes']['bus_prev'] is False:
                        print "PREV:OFF"

        # Channel - Bus Set PGM1
        if args.set_channelbus_pgm1 and args.set_channelbus_pgm1 == "ON":
            device.setChannelBus(chnum, True, None, None, None, None, chtype)
        elif args.set_channelbus_pgm1 and args.set_channelbus_pgm1 == "OFF":
            device.setChannelBus(chnum, False, None, None, None, None, chtype)
        
        # Channel - Bus Set PGM2
        if args.set_channelbus_pgm2 and args.set_channelbus_pgm2 == "ON":
            device.setChannelBus(chnum, None, True, None, None, None, chtype)
        elif args.set_channelbus_pgm2 and args.set_channelbus_pgm2 == "OFF":
            device.setChannelBus(chnum, None, False, None, None, None, chtype)
        
        # Channel - Bus Set PGM3
        if args.set_channelbus_pgm3 and args.set_channelbus_pgm3 == "ON":
            device.setChannelBus(chnum, None, None, True, None, None, chtype)
        elif args.set_channelbus_pgm3 and args.set_channelbus_pgm3 == "OFF":
            device.setChannelBus(chnum, None, None, False, None, None, chtype)
        
        # Channel - Bus Set PGM4
        if args.set_channelbus_pgm4 and args.set_channelbus_pgm4 == "ON":
            device.setChannelBus(chnum, None, None, None, True, None, chtype)
        elif args.set_channelbus_pgm4 and args.set_channelbus_pgm4 == "OFF":
            device.setChannelBus(chnum, None, None, None, False, None, chtype)
        
        # Channel - Bus Set PREV
        if args.set_channelbus_prev and args.set_channelbus_prev == "ON":
            device.setChannelBus(chnum, None, None, None, None, True, chtype)
        elif args.set_channelbus_prev and args.set_channelbus_prev == "OFF":
            device.setChannelBus(chnum, None, None, None, None, False, chtype)

    # Actions to do with vmixes (Studio Engine only - not QOR)
    if args.vmix_num and args.vmix_chnum:

        # VMix - On/Off State Get
        if args.get_vmixstate:
            vmix = device.getVMixChannelState(args.vmix_num, args.vmix_chnum)
            if vmix is not None and len(vmix) >= 1 and 'attributes' in vmix[0] and 'VMixOn' in vmix[0]['attributes'] and vmix[0]['attributes']['VMixOn'] is True:
                print "VMix:ON"
            elif vmix is not None and len(vmix) >= 1 and 'attributes' in vmix[0] and 'VMixOn' in vmix[0]['attributes'] and vmix[0]['attributes']['VMixOn'] is False:
                print "VMix:OFF"

        # VMix - On/Off State Set
        if args.set_vmixstate and args.set_vmixstate == "ON":
            device.setVMixChannelState(args.vmix_num, args.vmix_chnum, True)
        elif args.set_vmixstate and args.set_vmixstate == "OFF":
            device.setVMixChannelState(args.vmix_num, args.vmix_chnum, False)

        # VMix - Gain Get
        if args.get_vmixgain:
            vmix = device.getVMixChannelState(args.vmix_num, args.vmix_chnum)
            if vmix is not None and len(vmix) >= 1 and 'attributes' in vmix[0] and 'vmix_gain' in vmix[0]['attributes']:
                print "VMixGain:" + str(vmix[0]['attributes']['vmix_gain'])

        # VMix - Gain Set
        if args.set_vmixgain is not None:
            device.setVMixChannelGain(args.vmix_num, args.vmix_chnum, args.set_vmixgain)

    # Disconnect from the LWCP
    time.sleep(0.4)
    device.stop()
    sys.exit(0)
