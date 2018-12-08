"""LWCP Client (Communication Class). An Open-Source Python Client for the Axia Livewire Control Protocol."""

import socket
import time
import threading

__author__ = "Anthony Eden"
__copyright__ = "Copyright 2015-2018, Anthony Eden / Media Realm"
__credits__ = ["Anthony Eden"]
__license__ = "Commercial"
__version__ = "1.0"


class LWCPClientComms(threading.Thread):
    """This class handles all the communications with the LWCP server."""

    def __init__(self, host, port):
        """Create a socket connection to the LWCP server."""

        # The handle for the socket connection to the LWCP server
        self.sock = None

        # A list of all commands to send to the LWCP server
        self.sendQueue = []

        # A list of data types to subscribe to (with callbacks)
        self.dataSubscriptions = []

        # Should we be shutting down this thread? Set via self.stop()
        self._stop = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect((host, port))
        self.sock.setblocking(0)

        # Start the thread
        threading.Thread.__init__(self)

    def stop(self):
        """Attempt to close this thread."""
        self._stop = True

    def run(self):
        """Method keeps running forever, and handles all the communication with the open LWCP socket."""
        while True:

            # Try and receive data from the LWCP server
            recvData = self.recvUntilNewline()

            if recvData is not None:
                self.processReceivedData(recvData)

            # Check if we've got data to send back to the LWCP server
            if len(self.sendQueue) > 0:
                dataToSend = self.sendQueue[0]

                while dataToSend:
                    sent = self.sock.send(dataToSend)
                    dataToSend = dataToSend[sent:]

                # Once the message has been sent, take it out of the queue
                self.sendQueue.pop(0)

            if self._stop is True:
                # End the thread
                self.sock.close()
                break

            # Lower this number to receive data quicker
            if len(self.sendQueue) == 0:
                time.sleep(0.1)

    def recvUntilNewline(self):
        """Receive data until we get to the end of a message (also accounts for encapsulation blocks)."""
        totalData = ""
        inBlock = False

        while True:
            try:
                totalData += self.sock.recv(1024)
            except:
                pass
                
            # Check if we're in a data block
            if "%BeginEncap%" in totalData:
                inBlock = True

            # Check if the datablock is over
            if "%EndEncap%" in totalData and inBlock is True:
                return totalData

            # If we're not in a datablock and a newline is found, return the data
            if "\n" in totalData and inBlock is False:
                return totalData

            # We return 'None' if there's no data to return
            if totalData == "":
                return None

    def processReceivedData(self, recvData):
        """Process the received data from the LWCP server. Attempts to parse it and trigger all the subscribed callbacks."""
        # A dict with all the different message types we've received
        messageTypes = {}

        # Remove newlines between %BeginEncap% abd %EndEncap%
        if "%BeginEncap%" in recvData:
            recvData = recvData.replace("\n", " ").replace("\r", " ")
        
        # Parse the data so it's in a usable format
        # We receive a list in return (one per message - for blocks of data)
        parsedData = self.parseMessage(recvData)

        # Enumerate over all the messages
        for dataIndex, data in enumerate(parsedData):

            # Check if messageTypes already contains a list for this type.
            # If not, create one
            if parsedData[dataIndex]['type'] not in messageTypes:
                messageTypes[parsedData[dataIndex]['type']] = []

            # Add this message to the appropriate messageTypes list
            messageTypes[parsedData[dataIndex]['type']].append(parsedData[dataIndex])

        # Loop over every subscription
        for subI, subX in enumerate(self.dataSubscriptions):

            # If the subscribed command type matches the message's command type
            if subX['commandType'] in messageTypes:

                # Execute the callback!
                subX['callback'](messageTypes[subX['commandType']])

            # Check if we need to decrement the limit
            if self.dataSubscriptions[subI]['limit'] is not False:
                self.dataSubscriptions[subI]['limit'] = self.dataSubscriptions[subI]['limit'] - 1

            # Check if we need to remove this subscription
            if self.dataSubscriptions[subI]['limit'] <= 0 and self.dataSubscriptions[subI]['limit'] is not False:
                self.dataSubscriptions.pop(subI)

    def sendCommand(self, msg):
        """Buffer a command to send."""
        self.sendQueue.append(msg + "\n")

    def addSubscription(self, subType, callbackObj, limit=False, filters={}):
        """Add a subscription to the list of data subscriptions."""
        self.dataSubscriptions.append({
            "commandType": subType,
            "callback": callbackObj,
            "limit": limit
        })

    def splitSegments(self, string):
        """Attempt to parse all the segments provided in return data."""
        segments = []
        currentText = ""
        inSubStr = False
        inBlock = False
        skipUntilChar = False
        string += " "

        for i, char in enumerate(string):
            if (char == " " or char == ",") and inSubStr is False and inBlock is False:
                # Finish the segment

                if currentText[-1:] == ",":
                    currentText = currentText[:-1]

                segments.append(currentText)
                currentText = ""

            else:
                # Continue the segment
                if char == '"' and inSubStr is False and inBlock is False:
                    inSubStr = True

                elif char == '%'and string[i:i+12] == '%BeginEncap%':
                    inBlock = True
                    skipUntilChar = i+12

                elif char == '"' and inSubStr is True:
                    inSubStr = False
                
                elif char == '%' and inBlock is True and string[i:i+10] == '%EndEncap%':
                    inBlock = False
                    skipUntilChar = i+10

                elif skipUntilChar is not False and skipUntilChar > i:
                    continue

                else:
                    currentText += char

        return segments

    def parseMessage(self, data):
        """Parse the messages and put them into a list of dictionaries."""
        allData = []

        for x in data.splitlines():
            data = {}

            if x[:5] == "EVENT" or x[:4] == "INDI":
                segments = self.splitSegments(x[5:])
                data['type'] = "DATA"
                data["attributes"] = self.parseAttributes(segments)
                
                if 'profile_list' in data['attributes']:
                    data['type'] = "ShowProfileList"
                
                if 'profile_id' in data['attributes'] or 'profile_name' in data['attributes'] or 'profile_status' in data['attributes']:
                    data['type'] = "ShowProfile"
                
                if 'source_list' in data['attributes']:
                    data['type'] = "SourceProfiles"
                
                if 'source_id' in data['attributes'] or 'source_name' in data['attributes'] or 'source_livewire' in data['attributes'] or 'source_status' in data['attributes']:
                    data['type'] = "SourceProfile"
                
                if 'fader_gain' in data['attributes']:
                    data['type'] = "FaderGain"
                
                if 'ChannelOn' in data['attributes']:
                    data['type'] = "FaderState"
                
                if 'bus_pgm1' in data['attributes'] or 'bus_pgm2' in data['attributes'] or 'bus_pgm3' in data['attributes'] or 'bus_pgm4' in data['attributes'] or 'bus_prev' in data['attributes']:
                    data['type'] = "ChannelBus"
                
                if 'VMixOn' in data['attributes'] or 'vmix_gain' in data['attributes'] or 'vmix_timeup' in data['attributes'] or 'vmix_timedown' in data['attributes']:
                    data['type'] = "VMix"

            elif x[:3] == "SET":
                segments = self.splitSegments(x[4:])
                data['type'] = "SET"
                data["attributes"] = self.parseAttributes(segments)

            elif x[:5] == "ERROR":
                data['type'] = "ERROR"
                data["message"] = x[6:]

            # Do we need to combine this message with the last?
            if 'type' in data and len(allData) >= 1 and allData[len(allData)-1]['type'] == data['type'] and (data['type'] == "ShowProfile" or data['type'] == "SourceProfile"):
                allData[len(allData)-1]['attributes'].update(data['attributes'])

            elif data != {}:
                allData.append(data)

        return allData

    def parseAttributes(self, sections):
        """Parse all known attributes for a command and return in a dictionary."""
        attrs = {}

        for i, x in enumerate(sections):
            # Work out what the channel number is
            if x[:5] == "FaCH#":
                attrs['fader_number'] = int(x[5:])

            if x[:5] == "LwCH#":
                attrs['livewire_number'] = int(x[5:])

            if x[:8] == "ON_State":
                # Channel on/off state
                if x[-2:] == "ON":
                    attrs["ChannelOn"] = True
                else:
                    attrs["ChannelOn"] = False

            elif x[:12] == "ShowProfList":
                # TODO: Parse this as XML
                attrs['profile_list'] = x[13:].strip()

            elif x[:10] == "ShowProfID":
                attrs['profile_id'] = int(x[11:].strip())

            elif x[:12] == "ShowProfName":
                attrs['profile_name'] = x[13:].strip()

            elif x[:12] == "ShowProfStat":
                attrs['profile_status'] = x[13:].strip()
            
            elif x[:8] == "src_list":
                # TODO: Parse this as XML
                attrs['source_list'] = x[9:].strip()
            
            elif x[:6] == "src_id":
                attrs['source_id'] = int(x[7:].strip())
            
            elif x[:8] == "src_name":
                attrs['source_name'] = x[9:].strip()
            
            elif x[:8] == "src_lwch":
                attrs['source_livewire'] = x[9:].strip()
            
            elif x[:8] == "src_stat":
                attrs['source_status'] = x[9:].strip()
            
            elif x[:10] == "Fader_Gain":
                attrs['fader_gain'] = float(x[11:].strip())
            
            elif x[:8] == "Asg_PGM1":
                if x[-2:] == "ON":
                    attrs["bus_pgm1"] = True
                else:
                    attrs["bus_pgm1"] = False
            
            elif x[:8] == "Asg_PGM2":
                if x[-2:] == "ON":
                    attrs["bus_pgm2"] = True
                else:
                    attrs["bus_pgm2"] = False
            
            elif x[:8] == "Asg_PGM3":
                if x[-2:] == "ON":
                    attrs["bus_pgm3"] = True
                else:
                    attrs["bus_pgm3"] = False
            
            elif x[:8] == "Asg_PGM4":
                if x[-2:] == "ON":
                    attrs["bus_pgm4"] = True
                else:
                    attrs["bus_pgm4"] = False
            
            elif x[:8] == "Asg_PREV":
                if x[-2:] == "ON":
                    attrs["bus_prev"] = True
                else:
                    attrs["bus_prev"] = False
            
            elif x[:5].lower() == "state":
                if x[-2:] == "ON":
                    attrs["VMixOn"] = True
                else:
                    attrs["VMixOn"] = False
            
            elif x[:4].lower() == "gain":
                attrs['vmix_gain'] = float(x[5:].strip())
            
            elif x[:6].lower() == "timeup":
                attrs['vmix_timeup'] = float(x[7:].strip())
            
            elif x[:8].lower() == "timedown":
                attrs['vmix_timedown'] = float(x[9:].strip())
            

        return attrs
