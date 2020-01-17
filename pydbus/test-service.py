#!/usr/bin/env python3

import time

from gi.repository import GLib
from pydbus import SessionBus

class TestService():
    """
    <node>
      <interface name='com.wdc.TestService1'>

        <method name='EchoString'>
          <!-- Echoes back what you send to it. -->
          <arg type='s' name='string' direction='in'/>
          <arg type='s' name='output' direction='out'/>
        </method>

        <method name='Wait'>
          <!-- Appears to hang for the specified number of seconds. -->
          <arg type='t' name='timeout' direction='in'/>
        </method>
      </interface>
    </node>
   """
    def EchoString(self, string):
        print("EchoString: {}".format(string))
        return string

    def Wait(self, timeout):
        print("Wait: {}".format(timeout))
        time.sleep(timeout)
        print("Wait done.")

def main():
    loop = GLib.MainLoop()
    bus = SessionBus()
    service = TestService()

    print("Publishing service")
    bus.publish("com.wdc.TestService1", service)
    loop.run()

if __name__ == "__main__":
    main()

