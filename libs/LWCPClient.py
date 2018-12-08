"""LWCP Client. An Open-Source Python Client for the Axia Livewire Control Protocol."""

import time

from LWCPClientComms import LWCPClientComms

__author__ = "Anthony Eden"
__copyright__ = "Copyright 2015-2018, Anthony Eden / Media Realm"
__credits__ = ["Anthony Eden"]
__license__ = "Commercial"
__version__ = "1.0"


class LWCPClient():
    """Provides a friendly API for the Livewire Control Protocol."""

    def __init__(self, host, port=4010):
        """Init LWCP connection."""

        # This is our access to the LWCP
        self.LWCP = None

        # This variable gets given the callback data, ready to be processed by a waiting function
        self.waitingForCallback = False
        self.callbackData = None

        self.LWCP = LWCPClientComms(host, port)
        self.LWCP.start()

    def stop(self):
        """Close LWCP connection."""
        self.LWCP.stop()

    def waitForCallback(self, timeout=5):
        """Wait for data to be returned from the Comms class."""
        # The time we need to stop waiting for data and return it
        waitTimeout = time.time() + timeout

        while True:
            if self.waitingForCallback is False or waitTimeout <= time.time():
                returnData = self.callbackData
                self.callbackData = None
                return returnData

            else:
                time.sleep(0.1)

    def genericCallback(self, data):
        """Generic callback receiving function."""
        self.callbackData = data
        self.waitingForCallback = False

    def errorSub(self, callback):
        """Subscribe to error messages."""
        self.LWCP.addSubscription("ERROR", callback, False)

    def getShowProfiles(self):
        """Get a list of profiles on the console."""
        self.LWCP.addSubscription("ShowProfileList", self.genericCallback, 1)
        self.LWCP.sendCommand("GET AppControl ShowProfList")

        self.waitingForCallback = True
        return self.waitForCallback()
    
    def getShowProfile(self):
        """Gets the active show profile on the console."""
        self.LWCP.addSubscription("ShowProfile", self.genericCallback, 1)
        self.LWCP.sendCommand("GET AppControl ShowProfID,ShowProfName,ShowProfStat")

        self.waitingForCallback = True
        return self.waitForCallback()
    
    def setShowProfile(self, profile_id):
        """Activates the specified Show Profile"""
        self.LWCP.sendCommand("SET AppControl ShowProfID=" + str(profile_id))
    
    def getSourceProfiles(self, chnum, chtype = "fader"):
        """Gets the list of source profiles on the selected fader."""
        
        # Fader or Livewire
        if chtype == "fader":
            chtype_cmd = "FaCH#"
        elif chtype == "livewire":
            chtype_cmd = "LwCH#"
        else:
            raise Exception("Invalid channel type provided. Use 'fader' or 'livewire'.")
        
        self.LWCP.addSubscription("SourceProfiles", self.genericCallback, 1)
        self.LWCP.sendCommand("GET " + chtype_cmd + str(chnum) + " src_list")

        self.waitingForCallback = True
        return self.waitForCallback()
    
    def getSourceProfile(self, chnum, chtype = "fader"):
        """Gets the currently active source profile on the selected fader."""
        
        # Fader or Livewire
        if chtype == "fader":
            chtype_cmd = "FaCH#"
        elif chtype == "livewire":
            chtype_cmd = "LwCH#"
        else:
            raise Exception("Invalid channel type provided. Use 'fader' or 'livewire'.")
        
        self.LWCP.addSubscription("SourceProfile", self.genericCallback, 1)
        self.LWCP.sendCommand("GET " + chtype_cmd + str(chnum) + " src_id, src_name, src_lwch, src_stat")

        self.waitingForCallback = True
        return self.waitForCallback()
    
    def setSourceProfile(self, chnum, src_id, chtype = "fader"):
        """Sets a new active source profile on the selected fader."""
        
        # Fader or Livewire
        if chtype == "fader":
            chtype_cmd = "FaCH#"
        elif chtype == "livewire":
            chtype_cmd = "LwCH#"
        else:
            raise Exception("Invalid channel type provided. Use 'fader' or 'livewire'.")
        
        self.LWCP.addSubscription("SourceProfile", self.genericCallback, 1)
        self.LWCP.sendCommand("SET " + chtype_cmd + str(chnum) + " src_id=" + str(src_id))

    def getChannelState(self, chnum, chtype = "fader"):
        """Gets the on/off state for the specified channel."""
        
        # Fader or Livewire
        if chtype == "fader":
            chtype_cmd = "FaCH#"
        elif chtype == "livewire":
            chtype_cmd = "LwCH#"
        else:
            raise Exception("Invalid channel type provided. Use 'fader' or 'livewire'.")
        
        self.LWCP.addSubscription("FaderState", self.genericCallback, 1)
        self.LWCP.sendCommand("GET " + chtype_cmd + str(chnum) + " ON_State")

        self.waitingForCallback = True
        return self.waitForCallback()
        
    def setChannelState(self, chnum, on, chtype = "fader"):
        """Sets the specified channel on/off"""

        # Fader or Livewire
        if chtype == "fader":
            chtype_cmd = "FaCH#"
        elif chtype == "livewire":
            chtype_cmd = "LwCH#"
        else:
            raise Exception("Invalid channel type provided. Use 'fader' or 'livewire'.")

        # On or Off
        if on is True:
            on_cmd = "ON_State=ON"
        else:
            on_cmd = "ON_State=OFF"

        self.LWCP.sendCommand("SET " + chtype_cmd + str(chnum) + " " + on_cmd)
    
    def getChannelGain(self, chnum, chtype = "fader"):
        """Gets the level for the specified channel."""
        
        # Fader or Livewire
        if chtype == "fader":
            chtype_cmd = "FaCH#"
        elif chtype == "livewire":
            chtype_cmd = "LwCH#"
        else:
            raise Exception("Invalid channel type provided. Use 'fader' or 'livewire'.")
        
        self.LWCP.addSubscription("FaderGain", self.genericCallback, 1)
        self.LWCP.sendCommand("GET " + chtype_cmd + str(chnum) + " Fader_Gain")

        self.waitingForCallback = True
        return self.waitForCallback()
    
    def setChannelGain(self, chnum, level, chtype = "fader"):
        """Sets the level for the specified channel"""

        # Fader or Livewire
        if chtype == "fader":
            chtype_cmd = "FaCH#"
        elif chtype == "livewire":
            chtype_cmd = "LwCH#"
        else:
            raise Exception("Invalid channel type provided. Use 'fader' or 'livewire'.")

        self.LWCP.sendCommand("SET " + chtype_cmd + str(chnum) + " Fader_Gain=" + str(level))

    def getChannelBus(self, chnum, chtype = "fader"):
        """Gets the bus assignment for the specified channel."""

        # Fader or Livewire
        if chtype == "fader":
            chtype_cmd = "FaCH#"
        elif chtype == "livewire":
            chtype_cmd = "LwCH#"
        else:
            raise Exception("Invalid channel type provided. Use 'fader' or 'livewire'.")
        
        self.LWCP.addSubscription("ChannelBus", self.genericCallback, 1)
        self.LWCP.sendCommand("GET " + chtype_cmd + str(chnum) + " Asg_PGM1, Asg_PGM2, Asg_PGM3, Asg_PGM4, Asg_PREV")

        self.waitingForCallback = True
        return self.waitForCallback()
        
    def setChannelBus(self, chnum, pgm1=None, pgm2=None, pgm3=None, pgm4=None, prev=None, chtype = "fader"):
        """Assign or unassign channels from each bus on the console"""

        # Fader or Livewire
        if chtype == "fader":
            chtype_cmd = "FaCH#"
        elif chtype == "livewire":
            chtype_cmd = "LwCH#"
        else:
            raise Exception("Invalid channel type provided. Use 'fader' or 'livewire'.")
        
        commands_bus = []
        commands_bus_text = ""
        
        if pgm1 is True:
            commands_bus.append("Asg_PGM1=ON")
        elif pgm1 is False:
            commands_bus.append("Asg_PGM1=OFF")
            
        if pgm2 is True:
            commands_bus.append("Asg_PGM2=ON")
        elif pgm2 is False:
            commands_bus.append("Asg_PGM2=OFF")
        
        if pgm3 is True:
            commands_bus.append("Asg_PGM3=ON")
        elif pgm3 is False:
            commands_bus.append("Asg_PGM3=OFF")
        
        if pgm4 is True:
            commands_bus.append("Asg_PGM4=ON")
        elif pgm4 is False:
            commands_bus.append("Asg_PGM4=OFF")
        
        if prev is True:
            commands_bus.append("Asg_PREV=ON")
        elif prev is False:
            commands_bus.append("Asg_PREV=OFF")
        
        for cmd in commands_bus:
            if commands_bus_text != "":
                commands_bus_text += ", " + cmd
            else:
                commands_bus_text += cmd

        self.LWCP.sendCommand("SET " + chtype_cmd + str(chnum) + " " + str(commands_bus_text))

    def getVMixChannelState(self, vmix, chnum):
        """Gets the level for the specified channel."""
        self.LWCP.addSubscription("VMix", self.genericCallback, 1)
        self.LWCP.sendCommand("GET VMIX.SUB#"+str(vmix)+".IN#"+str(chnum)+" State, Gain, TimeUp, TimeDown")

        self.waitingForCallback = True
        return self.waitForCallback()

    def setVMixChannelState(self, vmix, chnum, on):
        """Sets the channel on/off for the specified vmix channel"""

        # On or Off
        if on is True:
            on_cmd = "State=ON"
        else:
            on_cmd = "State=OFF"

        self.LWCP.sendCommand("SET VMIX.SUB#"+str(vmix)+".IN#"+str(chnum)+" " + on_cmd)

    def setVMixChannelGain(self, vmix, chnum, gain):
        """Sets the level for the specified vmix channel"""
        self.LWCP.sendCommand("SET VMIX.SUB#"+str(vmix)+".IN#"+str(chnum)+" Gain=" + str(gain))
