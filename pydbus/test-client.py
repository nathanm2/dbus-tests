#!/usr/bin/env python3

from gi.repository import GLib
from pydbus import SessionBus
import argparse

ENDPOINT = "com.wdc.TestService1"
SERVICE_PATH = "/com/wdc/TestService1"

def echo(service, args):
    print("{}".format(service.EchoString(args.str)))

def wait(service, args):
    service.Wait(args.timeout)

def variant(service, args):
    reply = service.VariantResponse(args.double)
    print(reply)

def send_signal(service, args):
    service.SendSignal(args.name, args.value)

def listen_signal(service, args):
    bus = service._bus
    callback = lambda sender, object, iface, signal, params: print("{} {}".format(signal, params))
    bus.subscribe(sender=ENDPOINT, iface=ENDPOINT, signal=args.name, object=SERVICE_PATH,
            arg0=args.value, signal_fired=callback)
    loop = GLib.MainLoop()
    loop.run()

def main():
    parser = argparse.ArgumentParser(description="test service client")
    sub = parser.add_subparsers(title='subcommands', dest='subcommand')

    echo_parser = sub.add_parser("echo", help="echo a string")
    echo_parser.add_argument("str", help="String to be echoed")
    echo_parser.set_defaults(func=echo)

    wait_parser = sub.add_parser("wait", help="simulate a long running command")
    wait_parser.add_argument("timeout", type=int, help="Amount of time to wait.")
    wait_parser.set_defaults(func=wait)

    variant_parser = sub.add_parser("variant", help="returns a variant response")
    variant_parser.add_argument("--double", "-d", action='store_true')
    variant_parser.set_defaults(func=variant)

    send_signal_parser = sub.add_parser("signal", help="send a signal")
    send_signal_parser.add_argument("name", help="Signal name", choices=["S1", "S2"])
    send_signal_parser.add_argument("value", help="Signal value")
    send_signal_parser.set_defaults(func=send_signal)

    listen_parser = sub.add_parser("listen", help="wait for a signal")
    listen_parser.add_argument("--name", "-n", help="Signal name")
    listen_parser.add_argument("--value", "-v", help="Signal value")
    listen_parser.set_defaults(func=listen_signal)

    args = parser.parse_args()

    bus = SessionBus()
    service = bus.get(ENDPOINT, SERVICE_PATH)

    args.func(service, args)

if __name__ == "__main__":
    main()
