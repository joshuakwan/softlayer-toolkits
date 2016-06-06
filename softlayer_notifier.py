import logging
import os
import time
import pickle
from datetime import tzinfo, timedelta, datetime

import SoftLayer
from dateutil import parser

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

        self.data_filename_prefix = kwargs.get('sl_user')
        self._deserialize_data()

        self.customer_name = self._get_customer_name()
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
        while True:
            self._handle_updates()
            self._serialize_data()
            time.sleep(self.interval * 60)

    def _serialize_data(self):
        with open(self.data_filename_prefix + '_events', 'w') as f:
            f.write(pickle.dumps(self.sl_events))
        with open(self.data_filename_prefix + '_tickets', 'w') as f:
            f.write(pickle.dumps(self.sl_tickets))

    def _deserialize_data(self):
        filename_event = self.data_filename_prefix + '_events'
        if os.path.exists(filename_event):
            with open(filename_event, 'r') as f:
                self.sl_events = pickle.loads(f.read())
        filename_ticket = self.data_filename_prefix + '_tickets'
        if os.path.exists(filename_ticket):
            with open(filename_ticket, 'r') as f:
                self.sl_tickets = pickle.loads(f.read())

    def _handle_updates(self):
        active_events = self._get_active_events()
        active_tickets = self._get_active_tickets()

        # generate update contents for events
        new_events, updated_events, closed_events = self._get_updates(self.sl_events, active_events)

        # update self.sl_events
        self.sl_events = active_events

        # publish the updates
        for id in new_events.keys():
            self._publish_update(id, 'Event', 'good', self.customer_name)
        for id in updated_events.keys():
            self._publish_update(id, 'Event', '#439FE0', self.customer_name)
        for id in closed_events.keys():
            self._publish_update(id, 'Event', 'danger', self.customer_name)

        # generate update contents for tickets
        new_tickets, updated_tickets, closed_tickets = self._get_updates(self.sl_tickets, active_tickets)

        # update self.sl_tickets
        self.sl_tickets = active_tickets

        # publish the updates
        for id in new_tickets.keys():
            if 'MONITORING' in new_tickets[id]['title']:
                continue
            self._publish_update(id, 'Ticket', 'good', self.customer_name)
        for id in updated_tickets.keys():
            if 'MONITORING' in updated_tickets[id]['title']:
                continue
            self._publish_update(id, 'Ticket', '#439FE0', self.customer_name)
        for id in closed_tickets.keys():
            if 'MONITORING' in closed_tickets[id]['title']:
                continue
            self._publish_update(id, 'Ticket', 'danger', self.customer_name)

    def _publish_update(self, id, type, color, account):
        if type == 'Ticket':
            sl_service_key = 'Ticket'
            base_href = 'https://control.softlayer.com/support/tickets/%s'
            update_key = 'entry'
        elif type == 'Event':
            sl_service_key = 'Notification_Occurrence_Event'
            base_href = 'https://control.softlayer.com/support/event/details/%s'
            update_key = 'contents'

        update = self.sl_client[sl_service_key].getLastUpdate(id=id)
        update_date = update['createDate']
        href = base_href % id
        self.notifier.post_message(id=id, update=update[update_key], update_date=update_date, href=href, type=type,
                                   color=color, account=account)

    def _get_updates(self, objects_earlier, objects_now):
        new_objects = dict()
        updated_objects = dict()
        closed_objects = dict()

        for i in [id for id in objects_now.keys() if id not in objects_earlier.keys()]:
            new_objects[i] = objects_now[i]

        for i in [id for id in objects_earlier.keys() if id not in objects_now.keys()]:
            closed_objects[i] = objects_earlier[i]

        # Iterate thru open tickets to see if there are new updates
        for id in objects_now.keys():
            if id not in new_objects.keys() and objects_earlier.get(id) != objects_now.get(id):
                updated_objects[id] = objects_now[id]

        return new_objects, updated_objects, closed_objects

    def _get_customer_name(self):
        return self.sl_client['Account'].getMasterUser().get('companyName')

    def _get_active_events(self):
        events = self.sl_client['Notification_Occurrence_Event'].getAllObjects()

        active_events = dict()
        for event in events:
            end_date = event['endDate']
            if end_date != '':
                end = parser.parse(end_date)
                now = datetime.now(UTC())
                if (end - now).total_seconds() > 0:
                    event['href'] = 'https://control.softlayer.com/support/event/details/%s' % event['systemTicketId']
                    active_events[event['id']] = event

        return active_events

    def _get_active_tickets(self):
        active_tickets = dict()
        for ticket in self.sl_client['Account'].getOpenTickets():
            active_tickets[ticket['id']] = ticket
        return active_tickets
