#!/usr/bin/env python

import logging
import os
import signal
import sys
from argparse import ArgumentParser

from softlayer_notifier import SoftLayerNotifier


def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s: '
                               '%(message)s')


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nPress y to quit. (y/n)  ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)


parser = ArgumentParser()


def setup_parser():
    parser.add_argument(
        '--sl-user',
        help='SoftLayer Account Username',
        metavar='<sl user account>'
    )

    parser.add_argument(
        '--sl-apikey',
        help='SoftLayer Account API key',
        metavar='<sl api key>'
    )

    parser.add_argument(
        '--notify',
        default='slack',
        choices=['slack'],
        help='Set notification channel',
        metavar='<notification channel>'
    )

    parser.add_argument(
        '--slack-token',
        help='Slack Token',
        metavar='<slack token>'
    )

    parser.add_argument(
        '--slack-channel',
        help='Slack Channel',
        metavar='<slack channel>'
    )

    parser.add_argument(
        '--interval',
        default=1,
        help='Polling interval in minute, default is 1 min',
        metavar='<interval in minute>'
    )


def parse_args():
    return parser.parse_args()


if __name__ == '__main__':
    setup_logging()
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    setup_parser()
    args = parse_args()

    sl_user = args.sl_user
    sl_apikey = args.sl_apikey
    slack_token = args.slack_token
    slack_channel = args.slack_channel

    if sl_user is None:
        sl_user = os.environ.get('SL_USER')
    if sl_apikey is None:
        sl_apikey = os.environ.get('SL_APIKEY')

    logging.debug('Initiate a SoftLayerNotifier with parameters: sl_user=%s, notifier=%s,interval=%s' % (
        sl_user, args.notify, args.interval))
    notifier = SoftLayerNotifier(sl_user=sl_user, sl_apikey=sl_apikey,
                                 notifier=args.notify, interval=args.interval, additonal_args=args)
    notifier.start()
