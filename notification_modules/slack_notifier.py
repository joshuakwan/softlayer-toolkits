import json
import logging

from notifier import Notifier
from pyslack import SlackClient


class SlackNotifier(Notifier):
    def __init__(self, token, channel):
        self.slack = SlackClient(token)
        self.channel = channel

    def post_message(self, bot_name='SoftLayer Nofitier', as_user=True, **kwargs):
        type = kwargs.get('type')
        account = kwargs.get('account')
        update = kwargs.get('update')
        update_date = kwargs.get('update_date')
        href = kwargs.get('href')
        id = kwargs.get('id')
        color = kwargs.get('color')

        attachments = dict()
        attachments['thumb_url'] = 'https://pbs.twimg.com/profile_images/969317315/CLEAN_sl-logo_400x400.jpg'
        attachments['color'] = kwargs.get('color')

        attachments['title'] = 'Notification of UPDATE: %s %s under %s' % (
            type, id, account)
        attachments['title_link'] = href
        attachments['text'] = 'Update Date: %s\nUpdate Content:%s' % (
            update_date, update)

        logging.debug('Slack message: %s' % str(attachments))
        self.slack.chat_post_message(self.channel,
                                     '',
                                     username=bot_name,
                                     as_user=as_user,
                                     attachments=json.JSONEncoder().encode([attachments]))
