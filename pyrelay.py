import os
import sys
import ctypes

from time import sleep

# Helper Func
if sys.version_info.major >= 3:
  def charpToString(charp):
     return str(ctypes.string_at(charp), 'ascii')
  
  def stringToCharp(s) :   
    return bytes(s, "ascii")
else:
  def charpToString(charp) :
     return str(ctypes.string_at(charp))
  
  def stringToCharp(s) :   
    return bytes(s)  #bytes(s, "ascii")
  
def exc(msg):
  return Exception(msg)

def fail(msg): 
  raise exc(msg)


# Params
libfile = {'nt':   "usb_relay_device.dll", 
           'posix': "usb_relay_device.so",
           'darwin':"usb_relay_device.dylib",
           } [os.name]

usb_relay_lib_funcs = [
  # TYpes: h=handle (pointer sized), p=pointer, i=int, e=error num (int), s=string
  ("usb_relay_device_enumerate",               'h', None),
  ("usb_relay_device_close",                   'e', 'h'),
  ("usb_relay_device_open_with_serial_number", 'h', 'si'),
  ("usb_relay_device_get_num_relays",          'i', 'h'),
  ("usb_relay_device_get_id_string",           's', 'h'),
  ("usb_relay_device_next_dev",                'h', 'h'),
  ("usb_relay_device_get_status_bitmap",       'i', 'h'),
  ("usb_relay_device_open_one_relay_channel",  'e', 'hi'),
  ("usb_relay_device_close_one_relay_channel", 'e', 'hi'),
  ("usb_relay_device_close_all_relay_channel", 'e', 'h')
  ]

ret = {1: 'on', 0: 'off', -1: 'error'} 

# Main
class Lib: pass 
setattr(Lib, "dll", None)

def loadLib():
  Lib.dll = ctypes.CDLL(f"resources/{libfile}")
  
  ret = Lib.dll.usb_relay_init()
  if ret != 0 : fail("Failed lib init!")
  
  ctypemap = { 'e': ctypes.c_int, 'h':ctypes.c_void_p, 'p': ctypes.c_void_p,
            'i': ctypes.c_int, 's': ctypes.c_char_p}
  for x in usb_relay_lib_funcs :
      fname, ret, param = x
      try:
        f = getattr(Lib.dll, fname)
      except Exception:  
        fail("Missing lib export:" + fname)

      ps = []
      if param :
        for p in param :
          ps.append( ctypemap[p] )
      f.restype = ctypemap[ret]
      f.argtypes = ps
      setattr(Lib, fname, f)
  return Lib
      
def openDevById(idstr, lib):
  hdev = lib.usb_relay_device_open_with_serial_number(stringToCharp(idstr), 5)
  if not hdev: fail("Cannot open device with id="+idstr)
  numch = lib.usb_relay_device_get_num_relays(hdev)
  if numch <= 0 or numch > 8 : fail("Bad number of channels, can be 1-8")
  return numch, hdev

def closeDev(lib, hdev):
  lib.usb_relay_device_close(hdev)
  return None

def enumDevs(lib):
  devids = []
  enuminfo = lib.usb_relay_device_enumerate()
  while enuminfo :
    idstrp = lib.usb_relay_device_get_id_string(enuminfo)
    idstr = charpToString(idstrp)
    assert len(idstr) == 5
    if not idstr in devids : devids.append(idstr)
    else : print("Warning! found duplicate ID=" + idstr)
    enuminfo = lib.usb_relay_device_next_dev(enuminfo)
  return devids
  
def unloadLib(lib, hdev):
  if hdev: closeDev(lib, hdev)
  lib.dll.usb_relay_exit()
  lib.dll = None
  
def toggleSwitch(lib, hdev, num=1):
  status = lib.usb_relay_device_get_status_bitmap(hdev, num)
  if status == 0:
    lib.usb_relay_device_open_one_relay_channel(hdev, num)
  else:
    lib.usb_relay_device_close_one_relay_channel(hdev, num)
  return lib.usb_relay_device_get_status_bitmap(hdev, num)

def onSwitch(lib, hdev, time=1):
  status = toggleSwitch(lib, hdev)
  if status != 0:
    print('Switch On', bool(status))
    sleep(time)
    status = toggleSwitch(lib, hdev)