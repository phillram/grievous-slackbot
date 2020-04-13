# _______________________________________________________________
# Importing requirements 
# _______________________________________________________________
import os, logging, certifi
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, request
import ssl as ssl_lib
from collections import defaultdict 


# _______________________________________________________________
# Initializing everything
# _______________________________________________________________

# Initialize a Flask app to host the events adapter
app = Flask(__name__)

# Initialize a connection to Slack events
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], '/slack/events', app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# Initialize the words that Greivous bot will listen for
word_list = defaultdict(list)



# _______________________________________________________________
# These allow Flask to listen whenver a user does a slash 
# command.
# _______________________________________________________________

# For '/hellothere' command. Shows the user the proper
#  answer whenever you're greeted.
# Slack should automatically enlarge the gif
@app.route('/slack/hellothere', methods=['POST'])
def hello_there():
    return('https://media.giphy.com/media/7JC7bCJJGj44aBwB8p/giphy.gif')


# For '/watch' command. Adds the given words to the watchlist.
# This takes in the word provided by the user, saves it, and then
# tells the user what they are currently watching
@app.route('/slack/watch', methods=['POST'])
def add_to_watchlist():
    phrase = request.form['text']
    user_id = request.form['user_id']
    # print('The user is: >' + user_id + '< The phrase is >' + phrase + '<')

    # Adds the word to the requesters list
    word_list[user_id].append(phrase.lower())
    return('Phrase added. Your current list is: ' + str(word_list[user_id])[1:-1])

# For '/dontwatch' command. Removes the given words to the watchlist.
# This takes in the word provided by the user, removes it, and then
# tells the user what they are currently watching
@app.route('/slack/dontwatch', methods=['POST'])
def remove_from_watchlist():
    phrase = request.form['text']
    user_id = request.form['user_id']
    # print('The user is: >' + user_id + '< The phrase is >' + phrase + '<')

    # Tries to remove the phrase they said. Will return an error
    # message if unable to do so
    try:
        word_list[user_id].remove(phrase.lower())
    except:
        return('You aren\'t watching anything yet. \n Add some with /watch')

    # Checks if the user has any phrases left. And, will display
    # if they have more
    if not word_list[user_id]:
        return('Phrase removed. Your current list is empty')
    else:
        return('Phrase removed. Your current list is: ' + str(word_list[user_id])[1:-1])

# For '/watchlist' command. Displays the current watchlist.
@app.route('/slack/watchlist', methods=['POST'])
def show_watchlist():
    user_id = request.form['user_id']
    
    # Checks if the user is watching for any phrases. If not then return 
    # an error message
    if not word_list[user_id]:
        return('You aren\'t watching anything yet. \n Add some with /watch')
    else:
        return('Your current watchlist is: ' + str(word_list[user_id])[1:-1])


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

    # This looks through all the values in word_list in order to match
    # against the word_list values
    # It then finds the user who added the word, and messages them
    for key, value in word_list.items():
        # print('\n\n\n\nyou are in the loop')
        # print('key is: ' + str(key) + ' And value is: ' + str(value))
        # print('>>> text is: ' + text)
        
        # Checking if the word exists in the word_list
        if any(word in text.lower() for word in value):

            # Opens a DM with to the requesting user and saves the channel ID
            response = slack_web_client.im_open( user = key)
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