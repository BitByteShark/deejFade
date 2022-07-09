# %%
#import wmi #windows management instruments
import logging
import sys
import time
import win32gui
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL#, COMObject, GUID
import serial
import serial.tools.list_ports
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume #, ISimpleAudioVolume

#PID and VID of my Arduino Pro Micro (hope those are const)
SERIALDEVICEVID=6991
SERIALDEVICEPID=37382

def mapPercentTo1023(percent):
    return round(percent * 1023)

def PortOfSerialDeviceConnected(deviceSearialPID, deviceSearialVID):
    portsFound = serial.tools.list_ports.comports()
    numConnections = len(portsFound)
    
    for i in range(0,numConnections):
        port = portsFound[i]
        try:
            devicePID=port.pid
            deviceVID=port.vid
            if devicePID==deviceSearialPID and deviceVID==deviceSearialVID:
                return port.name

        except Exception as e:
            logging.warning(f'coudn\'t identify portnumber:',exc_info=True)

def intIncrementWrapped(number, minEnd, maxEnd, forwards):
    if forwards:
        if number>=minEnd and number<maxEnd:
            number += 1
            return number
        else:
            return minEnd
    else:
        if number>minEnd and number<=maxEnd:
            number -= 1
            return number
        else:
            return maxEnd

def iconFromExecutablePath(path):
    #see https://coderedirect.com/questions/523553/best-way-to-extract-ico-from-exe-and-paint-with-pyqt
    #or https://stackoverflow.com/questions/43011012/get-icon-from-process-list-instead-of-file
    #or https://programtalk.com/python-examples/win32gui.ExtractIconEx/
    icons = win32gui.ExtractIconEx(path, 0) #returns Objecttype HIcon big [0] and small [1] icon
    info = win32gui.GetIconInfo(icons [0] [0])
    win32gui.DestroyIcon(small[0])

def attempt_print(s):
    try:
        print(s)
    except:
        pass

class sessionControl:
    
    def __init__(self) -> None:
        self.count=0
        self.sessionDict={}
        self.serialActive=False

        self.updateSessionList()
        
    def primaryLoop(self):
        while True:
            ser=self.awaitNewSerialConnection()
            time.sleep(1)
            self.updateSessionList
            self.sendSessionInfo(ser, 1)
            while self.serialActive:
                line=None
                try:
                    if ser.inWaiting():
                        #tmpSerialChunk=ser.readline().decode('utf-8')
                        #logging.info(f'{tmpSerialChunk}')
                        line = ser.readline().decode('utf-8').rstrip()
                    else:
                        line=None
                        time.sleep(0.04)
                except serial.SerialException as e:
                    if "ClearCommError failed" in str(e):
                        #case of hot-unplug of serial connection
                        logging.info(f'serial interrupted, device on port {ser._port} disconnected')
                    else:
                        attempt_print(str(e))
                        logging.error(f'serial couldnt be read unexpactedly:',exc_info=True)
                    time.sleep(3)#serial.tools.list_ports.comports() seems to need time to update/recognize disconnected serial port
                    break
                
                if line:
                    attempt_print("text received("+line+")")
                    split_line = line.split("|")

                    try:
                        if split_line[1]=="sC":#sessionChange
                            if split_line[2]=="n":#next
                                updatedPID=self.updateToNextSessionPID(int(split_line[0]),True)
                            elif split_line[2]=="p":#previous
                                updatedPID=self.updateToNextSessionPID(int(split_line[0]),False)
                            self.sendSessionInfo(ser, updatedPID)
                            
                        elif split_line[1]=="vL":#volumeLevel change
                            attempt_print("volumeChange for PID "+split_line[0]+" to "+split_line[2])
                            self.setSessionVolume(int(split_line[0]),int(split_line[2]))

                    except Exception as e:
                        logging.info(f'serial Input not as expected:',exc_info=True)
                        continue
            
    def updateSessionList(self):
        #currently nothing is reused and everything ist 
        logging.info(f'sessionList updated')
        self.sessionDict={}
        allAudioSessions=AudioUtilities.GetAllSessions()
        for idx,singlesession in enumerate(allAudioSessions):
            sessionID=singlesession.ProcessId
            self.sessionDict[sessionID]={}
            self.sessionDict[sessionID]=singlesession
        
        activeOutputDevice = AudioUtilities.GetSpeakers()
        activeOutputDeviceInterface = activeOutputDevice.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.sessionDict[1] = cast(activeOutputDeviceInterface, POINTER(IAudioEndpointVolume))

        self.count=len(self.sessionDict)

    def getSessionName(self, PID):
        session=self.sessionDict[PID]
        if hasattr(session,'DisplayName') and session.DisplayName!="":
            return session.DisplayName
        elif hasattr(session,'Process'):
            return session.Process.name()
        elif PID==1:
            return "Speaker Volume"
        else:
            return
        
    def getSessionPath(self, PID):
        #session.Process.cwd(): current working directory
        if hasattr(self.sessionDict[PID],'Process'):
            return self.sessionDict[PID].Process.exe().replace("\\", "/")
        else:
            return

    def getSessionVolume(self, PID):
        session=self.sessionDict[PID]
        if hasattr(session, 'SimpleAudioVolume'):
            return mapPercentTo1023(session.SimpleAudioVolume.GetMasterVolume())
        else:
            return mapPercentTo1023(session.GetMasterVolumeLevelScalar())

    def setSessionVolume(self, PID, volumeValue):
        if volumeValue>1016:
            percentVolume=1
        elif volumeValue<7:
            percentVolume=0
        else:
            percentVolume=round(volumeValue/1023,2)

        if hasattr(self.sessionDict[PID], 'SimpleAudioVolume'):
            self.sessionDict[PID].SimpleAudioVolume.SetMasterVolume(percentVolume,None)
        else:
            self.sessionDict[PID].SetMasterVolumeLevelScalar(percentVolume,None)

    def setOutputDeviceLevel(self):
        
        return

    def updateToNextSessionPID(self,previousPID,forwards):
        self.updateSessionList()
        if previousPID in self.sessionDict:
            idx=list(self.sessionDict).index(previousPID)
            newIdx=intIncrementWrapped(idx, 0, len(self.sessionDict)-1, forwards)
            newPID=list(self.sessionDict)[newIdx]
        else:
            newPID=list(self.sessionDict)[0]

        return newPID
        
    def awaitNewSerialConnection(self):
        ser = serial.Serial(parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE) #timeout=
        ser.baudrate = 9600
        portName=None
        while portName==None:
            portName=PortOfSerialDeviceConnected(SERIALDEVICEPID,SERIALDEVICEVID)

            if portName:
                ser.port = portName
                ser.open()
                
                self.serialActive=True
                logging.info(f'device on port {portName} connected and serial started')

                # ensure we start clean
                ser.flushInput()
                ser.flushOutput()

                #if ser.inWaiting():
                #    ser.readline()
                return ser
                
            attempt_print("await Connection...")
            time.sleep(2)

    def examineSerial(self):
        return

    def sendSessionInfo(self, serial, transmitPID):
        outputString=str(transmitPID).zfill(6)+"|sI|"+str(self.getSessionVolume(transmitPID)).zfill(4)+"|"+self.getSessionName(transmitPID)
        attempt_print("sending Answer:("+outputString+")")
        serial.write(outputString.encode())

def main():
    logging.basicConfig(format='%(asctime)s (%(levelname)s) - %(message)s', level=logging.INFO)
    #logging.debug(f'debug')
    logging.info(f'start of exec')
    #logging.warning(f'warning')
    #logging.error(f'error')
    #logging.critical(f'critical')

    try:#"global" try catch
        #tester=sessionList()
        testRaw=AudioUtilities.GetAllSessions()
        activeAudioOutputDevices = AudioUtilities.GetSpeakers()
        #active_device_interface = active_device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        
        deej=sessionControl()
        #attempt_print(deej.getNextSession(2,"next"))
        deej.primaryLoop()
    except KeyboardInterrupt:
        attempt_print('Keyboard Interrupt.')
        sys.exit(1)
    except Exception as e:
        logging.critical(f'unexpected critical global deej application error:',exc_info=True)

if __name__ == '__main__':
    main()