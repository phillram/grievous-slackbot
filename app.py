# Importing requirements 
# _______________________________________________________________
import os, logging, certifi
# import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import ssl as ssl_lib
# import certifi
# from onboarding_tutorial import OnboardingTutorial

# Initializing everything
# _______________________________________________________________
# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], '/slack/events', app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# The words that Grievous bot will listen for
phrases = ['zoop', 'zeep', 'mirage']


# Message events will trigger when a user types in a message
# _______________________________________________________________
@slack_events_adapter.on('message')
def message(payload):
    
    # Stores information about the message
    event = payload.get('event', {})
    
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    timestamp = event.get('ts')
    # print('>>> channel_id is: ' + channel_id)
    # print('>>> user_id is: ' + user_id)
    # print('>>> text is: ' + text)
    # print('>>> timestamp is: ' + str(timestamp))

    # Checks if the message contains any of the words from the phrases list
    if text.lower() in phrases:

        # Opens a DM with user and saves the channel ID
        response = slack_web_client.im_open( user = user_id)
        dm_channel = response['channel']['id']
        # print('>>> im_channel is: ' + str(im_channel))
        
        # Uses the user ID to pull the display name
        # of the user that triggered the bot
        response = slack_web_client.users_info(user = user_id)
        triggering_users_name = response['user']['profile']['display_name']

        # Uses the timestamp to generate a link to the message
        response = slack_web_client.chat_getPermalink(channel = channel_id, message_ts = timestamp)
        message_link = response['permalink']
        # print('>>> message_link is: ' + str(message_link))

        # Sends the message to the IM channel above
        slack_web_client.chat_postMessage(
            channel = dm_channel,
            text = triggering_users_name + ' mentioned your keyword! \n' + message_link
        )

# Start Grievous bot and run flask on port 5066
# _______________________________________________________________
if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(port=5066)