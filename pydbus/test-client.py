#!/usr/bin/env python3

from pydbus import SessionBus
import argparse

ENDPOINT = "com.wdc.TestService1"
SERVICE_PATH = "/com/wdc/TestService1"

def echo(service, args):
    print("{}".format(service.EchoString(args.str)))

def wait(service, args):
    service.Wait(args.timeout)

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

    bus = SessionBus()
    service = bus.get(ENDPOINT, SERVICE_PATH)

    args.func(service, args)

if __name__ == "__main__":
    main()
