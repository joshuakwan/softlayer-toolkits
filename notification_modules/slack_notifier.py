from pyslack import SlackClient
from notifier import Notifier
import json


class SlackNotifier(Notifier):
    def __init__(self, token, channel):
        self.slack = SlackClient(token)
        self.channel = channel

    def post_message(self, data, bot_name='SoftLayer Nofitier', as_user=True):
        attachments = dict()
        attachments['thumb_url'] = 'https://pbs.twimg.com/profile_images/969317315/CLEAN_sl-logo_400x400.jpg'
        attachments['color'] = '#439FE0'

        attachments['title'] = 'Notification of UPDATE: %s %s under %s' % (
            data.get('type'), data.get('id'), data.get('account'))
        attachments['title_link'] = data.get('href')
        attachments['text'] = 'Update Date: %s\nUpdate Content:%s' % (
            data.get('update_date'), data.get('update_content'))

        self.log.debug('Slack message: %s' % str(attachments))
        self.slack.chat_post_message(self.channel,
                                     '',
                                     username=bot_name,
                                     as_user=as_user,
                                     attachments=json.JSONEncoder().encode([attachments]))
