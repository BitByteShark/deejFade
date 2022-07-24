import pulsectl
import logging
#import sys
from pynput import keyboard
import threading
#import concurrent.futures
import time
import serial
import serial.tools.list_ports

#PID and VID of my Arduino Pro Micro (hope those are const)
SERIALDEVICE_VID=6991
SERIALDEVICE_PID=37382
BAUDRATE = 9600

def collectAudioSessionsInfo():
    print("collecting Audio info")
    return

def keystroke_event_reaction(key):
    print(f'clap {key}')
    #Bongocat
    return

def audio_event_reaction():
    print("print audio event differentiation")
    return

def serial_processing(serial_message):
    #read and react to Serial information
    print(f'Serial Message is: \"{serial_message}\"')

class serial_control_thread(threading.Thread):
    def __init__(self, name='serial_control_thread'):
        self._stopevent = threading.Event()
        self.ser = serial.Serial(parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE) #timeout=
        self.ser.baudrate=BAUDRATE
        self.port_name=None
        threading.Thread.__init__(self, name=name)
    
    def run(self):
        while self.port_name==None and not self._stopevent.isSet():
            self.port_name=identify_serialdevice_connection_port(SERIALDEVICE_PID,SERIALDEVICE_VID)
            
            if self.port_name:
                self.ser.port = f'/dev/{self.port_name}'
                try:
                    self.ser.open()
                    logging.info(f'device on port {self.port_name} connected and serial started')
        
                    # ensure clean start of the serial buffer
                    self.ser.flushInput()
                    self.ser.flushOutput()
                    
                    while not self._stopevent.isSet():
                        if self.ser.inWaiting():
                            logging.debug("something found in serial buffer")
                            #tmpSerialChunk=ser.readline().decode('utf-8')
                            #logging.info(f'{tmpSerialChunk}')
                            line = self.ser.readline().decode('utf-8').rstrip()
                            logging.debug("decoded line from serial buffer")
                            serial_processing(line)
                        else:
                            line=None
                            time.sleep(0.04)
                
                except Exception as e:
                # except serial.SerialException as e:
                    if "[Errno 5] Input/output error" in str(e): #if "ClearCommError failed" in str(e):
                        #case of hot-unplug of serial connection
                        logging.info(f'serial interrupted, device on port {self.ser.port} disconnected')
                        self.ser.close()
                    else:
                        logging.debug(f'{str(e)}')
                        logging.error('serial couldnt be opened or read unexpactedly:',exc_info=True)
                    self.port_name=None
            else:
                logging.info("await Connection...")
            time.sleep(1)
        #logging.info('serial_handler_thread_exited')
    def join(self, timeout=None):
        #by example for stopEvent:https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s03.html
        self._stopevent.set()
        threading.Thread.join(self, timeout)
        logging.info('audio_handler_thread_exited')

class pulse_audio_listener_thread(threading.Thread):
    def __init__(self, name='pulse_audio_listener_thread'):
        #self._stopevent = threading.Event()
        self.pulse_audio_listener = pulsectl.Pulse('event-printer')
        self.pulse_audio_listener.event_mask_set('all')
        self.pulse_audio_listener.event_callback_set(print)
        threading.Thread.__init__(self, name=name)
        
    def run(self):
        self.pulse_audio_listener.event_listen()#timeout=10
        #mute
        #unmute
        #new Soundlevel of sink
            
    def join(self, timeout=None):
        #by example for stopEvent:https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s03.html
        pulsectl.PulseLoopStop()#self._stopevent.set()
        #threading.Thread.join(self, timeout)
        logging.info('pulse_audio_listener_thread_exited')

def identify_serialdevice_connection_port(deviceSearial_PID, deviceSearial_VID):
    portsFound = serial.tools.list_ports.comports()
    numConnections = len(portsFound)
    
    for i in range(0,numConnections):
        port = portsFound[i]
        try:
            devicePID=port.pid
            deviceVID=port.vid
            if devicePID==deviceSearial_PID and deviceVID==deviceSearial_VID:
                logging.info(f'Portname identified as: {port.name}')
                return port.name
        except Exception:# as e:
            logging.warning('coudn\'t identify portnumber:',exc_info=True)

def print_events(ev):
    print('Pulse event:', ev)

def main():
    logging.basicConfig(format='%(asctime)s (%(levelname)s) - %(message)s', level=logging.INFO)
    #logging.debug(f'debug')
    logging.info('start of exec')
    #logging.warning(f'warning')
    #logging.error(f'error')
    #logging.critical(f'critical')
    try:
        #setup Listeners
        keystroke_listener = keyboard.Listener(on_press=keystroke_event_reaction)#, daemon=True
        serial_listener = serial_control_thread()
        audio_event_listener = pulse_audio_listener_thread()
        
        #start Listeners
        keystroke_listener.start()
        serial_listener.start()
        audio_event_listener.start()
        
        keystroke_listener.join()#used as infinte wait/sleep
        #time.sleep(20)
    except KeyboardInterrupt:
        logging.info('Client got interrupted.')
    except Exception as error:
        logging.critical(f"crashed due to error:\n{str(error)}")
    finally:
        serial_listener.join()
        audio_event_listener.join()
        keystroke_listener.stop()
        logging.info('keystroke_handler_thread_exited')

        
if __name__ == '__main__':
    main()