import logging
import SoftLayer
import time
from dateutil import parser
from datetime import tzinfo, timedelta, datetime
import os
from notification_modules.slack_notifier import SlackNotifier

ZERO = timedelta(0)


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


class SoftLayerNotifier(object):
    def __init__(self, **kwargs):
        self.updated_contents = dict()
        self.sl_events = dict()
        self.sl_tickets = dict()

        self.sl_client = SoftLayer.create_client_from_env(username=kwargs.get('sl_user'),
                                                          api_key=kwargs.get('sl_apikey'))

        self.interval = kwargs.get('interval')

        self.notifier = None
        if kwargs.get('notifier') == 'slack':
            slack_token = kwargs.get('additonal_args').slack_token
            slack_channel = kwargs.get('additonal_args').slack_channel

            if slack_token is None:
                slack_token = os.environ.get('SLACK_TOKEN')
            if slack_channel is None:
                slack_channel = os.environ.get('SLACK_CHANNEL')

            logging.debug('Initiate a SlackNotifier with parameters: slack_channel=%s' % (slack_channel))
            self.notifier = SlackNotifier(slack_token, slack_channel)

        self.start()

    def start(self):
        # TODO to implement the quit function
        while True:
            self._handle_updates()
            time.sleep(self.interval * 60)

    def _handle_updates(self):
        active_events = self._get_active_events()
        active_tickets = self._get_active_tickets()

        # generate update contents for events
        updated_events, closed_events = self._get_updates(self.sl_events, active_events)

        # update self.sl_events
        self.sl_events = active_events

        # publish the updates
        for event in updated_events:
            self.notifier.post_message(event)
        for event in closed_events:
            self.notifier.post_message(event)

        # generate update contents for tickets
        updated_tickets, closed_tickets = self._get_updates(self.sl_tickets, active_tickets)

        # update self.sl_tickets
        self.sl_tickets = active_tickets

        # publish the updates
        for event in updated_tickets:
            self.notifier.post_message(event)
        for event in closed_tickets:
            self.notifier.post_message(event)

    def _get_updates(self, objects_earlier, objects_now):
        updated_objects = []
        closed_objects = []

        # TODO generate the two arrays

        return closed_objects, updated_objects

    def _get_customer_name(self):
        return self.sl_client['Account'].getMasterUser().get('companyName')

    def _get_active_events(self):
        events = self.sl_client['Notification_Occurrence_Event'].getAllObjects()

        active_events = []
        for event in events:
            end_date = event['endDate']
            if end_date != '':
                end = parser.parse(end_date)
                now = datetime.now(UTC())
                if (end - now).total_seconds() > 0:
                    event['href'] = 'https://control.softlayer.com/support/event/details/%s' % event['systemTicketId']
                    active_events.append(event)

        return active_events

    def _get_active_tickets(self):
        active_tickets = []

        # TODO get active tickets

        return active_tickets
