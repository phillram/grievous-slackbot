# _______________________________________________________________
# Importing requirements 
# _______________________________________________________________
import os, logging, certifi
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, request
# from flask_sqlalchemy import SQLAlchemy
import ssl as ssl_lib

# _______________________________________________________________
# Initializing everything
# _______________________________________________________________

# Initialize a Flask app to host the events adapter
app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///keywords.db'
# db = SQLAlchemy(app)

# # Initialize the flask database
# class Keywords(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     slack_user_id = db.Column(db.String(25), nullable = False)
#     slack_keyword = db.Column(db.String(100), nullable = False)

#     def __repr__(self):
#         return '<Task %r>' % self.id

# Initialize a connection to Slack events
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], '/slack/events', app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# The words that Grievous bot will listen for
users = []
phrases_list = []


# _______________________________________________________________
# These allow Flask to listen whenver a user does a slash 
# command.
# _______________________________________________________________

# For '/hellothere' command. Shows the user the proper
#  answer whenever you're greeted.
# Slack should automatically enlarge the gif
@app.route('/slack/hellothere', methods=['POST'])
def hello_there():
    data = request.get_data()
    print(data)
    return('https://media.giphy.com/media/7JC7bCJJGj44aBwB8p/giphy.gif')


# For '/watch' command. Adds the given words to the watchlist.
# This takes in the word provided by the user, saves it, and then
# tells the user what they are currently watching
@app.route('/slack/watch', methods=['POST'])
def add_to_watchlist():
    phrase = request.form['text']
    # print('>>> The given phrase is: ' + phrase)

    phrases_list.append(phrase.lower())
    return('Phrase added. Your current list is: ' + str(phrases_list)[1:-1])


# For '/dontwatch' command. Removes the given words to the watchlist.
# This takes in the word provided by the user, removes it, and then
# tells the user what they are currently watching
@app.route('/slack/dontwatch', methods=['POST'])
def remove_from_watchlist():
    phrase = request.form['text']
    # print('>>> The given phrase is: ' + phrase)

    phrases_list.remove(phrase.lower())
    if not phrases_list:
        return('Phrase removed. Your current list is empty')
    else:
        return('Phrase removed. Your current list is: ' + str(phrases_list)[1:-1])


# For '/watchlist' command. Displays the current watchlist.
@app.route('/slack/watchlist', methods=['POST'])
def show_watchlist():
    if not phrases_list:
        return('You aren\'t watching anything yet. \n Add some with /watch')
    else:
        return('You are currently watching for: ' + str(phrases_list)[1:-1])


# _______________________________________________________________
# Message events in Slack will trigger this section
# The messages will be checked to see if they contain the keywords
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

    # Checks if the message contains any of the words from the phrases_list list
    # then sends the user a DM with a link to the message
    if any(word in text.lower() for word in phrases_list):

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



# _______________________________________________________________
# Start Grievous bot and run flask on port 5066
# _______________________________________________________________
if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(port=5066)