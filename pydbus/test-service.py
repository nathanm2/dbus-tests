#!/usr/bin/env python3

import time

from gi.repository import GLib
from pydbus import SessionBus
from pydbus.generic import signal

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

        <method name='VariantResponse'>
          <!-- Sends back a variant response. -->
          <arg type='b' name='double' direction='in'/>
          <arg type='v' name='result' direction='out'/>
        </method>

        <method name='SendSignal'>
          <!-- Sends back a variant response. -->
          <arg type='s' name='name' direction='in'/>
          <arg type='s' name='value' direction='in'/>
        </method>

        <signal name="S1">
          <!-- Signal 1 -->
          <arg name="value1" type="s"/>
        </signal>

        <signal name="S2">
          <!-- Signal 2 -->
          <arg name="value1" type="s"/>
        </signal>

        <property name="StrProp" type="s" access="readwrite"/>
        <property name="IntProp" type="i" access="readwrite"/>
        <property name="BoolProp" type="b" access="readwrite"/>

      </interface>
    </node>
   """
    def __init__(self):
        self._str_prop = ""
        self._int_prop = 0
        self._bool_prop = False

    @property
    def StrProp(self):
        return self._str_prop

    @StrProp.setter
    def StrProp(self, value):
        self._str_prop = value

    @property
    def IntProp(self):
        return self._int_prop

    @IntProp.setter
    def IntProp(self, value):
        self._int_prop = value

    @property
    def BoolProp(self):
        return self._bool_prop

    @BoolProp.setter
    def BoolProp(self, value):
        self._bool_prop = value

    def EchoString(self, string):
        print("EchoString: {}".format(string))
        return string

    def Wait(self, timeout):
        print("Wait: {}".format(timeout))
        time.sleep(timeout)
        print("Wait done.")

    def VariantResponse(self, double):
        print("VariantResponse: {}".format(double))
        if double:
            return GLib.Variant("(bs)", (double, "some string"))
        else:
            return GLib.Variant("(b)", (double,))

    IfaceName = "com.wdc.TestService1"
    S1 = signal()
    S2 = signal()

    def SendSignal(self, name, value):
        if name == "S1":
            self.S1(value)
        else:
            self.S2(value)

def main():
    loop = GLib.MainLoop()
    bus = SessionBus()
    service = TestService()

    print("Publishing service")
    bus.publish("com.wdc.TestService1", service)
    loop.run()

if __name__ == "__main__":
    main()

