#!/usr/bin/env python3

from gi.repository import Gio, GLib
import argparse

def echo(bus, args):
    ret = bus.call_sync("com.wdc.TestService1", "/com/wdc/TestService1",
            "com.wdc.TestService1", "EchoString", GLib.Variant("(s)", (args.str,)),
            GLib.VariantType.new("(s)"), 0, -1, None).unpack()
    print(ret[0])

def wait(bus, args):
    ret = bus.call_sync("com.wdc.TestService1", "/com/wdc/TestService1",
            "com.wdc.TestService1", "Wait", GLib.Variant("(t)", (args.timeout,)),
            GLib.VariantType.new("()"), 0, -1, None).unpack()

def main():
    parser = argparse.ArgumentParser(description="test service client")
    sub = parser.add_subparsers(title='subcommands', dest='subcommand')

    echo_parser = sub.add_parser("echo", help="echo a string")
    echo_parser.add_argument("str", help="String to be echoed")
    echo_parser.set_defaults(func=echo)

    wait_parser = sub.add_parser("wait", help="simulate a long running command")
    wait_parser.add_argument("timeout", type=int, help="Amount of time to wait.")
    wait_parser.set_defaults(func=wait)

    args = parser.parse_args()

    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    args.func(bus, args)

if __name__ == "__main__":
    main()
