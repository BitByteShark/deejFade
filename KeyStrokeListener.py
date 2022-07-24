from pynput import keyboard

def process_key_press(key):
    if key == keyboard.Key.esc:
        return False  # stop listener
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys    
    print('Key pressed: ' + k)
    if k in ['1', '2', 'left', 'right']:  # keys of interest
        # self.keys.append(k)  # store it in global-like variable
        return False  # stop listener; remove this if want more keys

listener = keyboard.Listener(on_press= process_key_press)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keys




# https://www.kedardangal.com.np/how-to-program-a-keylogger-using-python-application-in-linux/
# alternativ ggf: https://pypi.org/project/pyudev/