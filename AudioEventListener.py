import pulsectl
import json

#https://pypi.org/project/pulsectl/
#https://github.com/mk-fg/python-pulse-control

#https://pypi.org/project/pulsectl-asyncio/

#Arch Pulse Examples: https://wiki.archlinux.org/title/PulseAudio/Examples

pulse = pulsectl.Pulse('my-client-name')
"""
sink_input=pulse.sink_input_list()[1]
test=sink_input.volume.values


var=sink_input.proplist.values()

json.load(pulse.sink_input_list()[1].proplist)
for audiosources in pulse.sink_input_list():
    print(pulse.sink_input_list()[1].proplist)

pulse.server_info(), pulse.source_list(), pulse.sink_list()

"""


with pulsectl.Pulse('event-printer') as pulse:
  print('Event types:', pulsectl.PulseEventTypeEnum)
  print('Event facilities:', pulsectl.PulseEventFacilityEnum)
  print('Event masks:', pulsectl.PulseEventMaskEnum)

  def print_events(ev):
    print('Pulse event:', ev)
    ### Raise PulseLoopStop for event_listen() to return before timeout (if any)
    # raise pulsectl.PulseLoopStop

  pulse.event_mask_set('all')
  pulse.event_callback_set(print_events)
  pulse.event_listen(timeout=10)



















#https://stackoverflow.com/questions/5810399/how-to-get-icon-icons-path-of-running-app-in-linux-windows
import pygtk  
pygtk.require('2.0')  
import gtk  
import wnck  

screen = wnck.screen_get_default()  

while gtk.events_pending():  
    gtk.main_iteration(False)  

for w in screen.get_windows():  
    name = w.get_name()  
    icon = w.get_icon()







# =============================================================================
with pulsectl.Pulse('volume-increaser') as pulse:
  for sink in pulse.sink_list():
    # Volume is usually in 0-1.0 range, with >1.0 being soft-boosted
    pulse.volume_change_all_chans(sink, 0.1)

# =============================================================================


#=============================================================================
with pulsectl.Pulse('event-printer') as pulse:
  # print('Event types:', pulsectl.PulseEventTypeEnum)
  # print('Event facilities:', pulsectl.PulseEventFacilityEnum)
  # print('Event masks:', pulsectl.PulseEventMaskEnum)

  def print_events(ev):
    print('Pulse event:', ev)
    ### Raise PulseLoopStop for event_listen() to return before timeout (if any)
    # raise pulsectl.PulseLoopStop

  pulse.event_mask_set('all')
  pulse.event_callback_set(print_events)
  pulse.event_listen(timeout=10)
#=============================================================================


# =============================================================================
pulse = pulsectl.Pulse('my-client-name')
pulse.sink_list()
pulse.sink_input_list()
pulse.sink_input_list()[0].proplist
sources=pulse.source_list()
sink = pulse.sink_list()[0]
pulse.volume_change_all_chans(sink, -0.1)
pulse.volume_set_all_chans(sink, 0.5)
pulse.server_info().default_sink_name
pulse.default_set(sink)
card = pulse.card_list()[0]
card.profile_list
pulse.card_profile_set(card, 'output:hdmi-stereo')
help(pulse)
pulse.close()
# =============================================================================