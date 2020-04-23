# grievous-slackbot
This slackbot will alert you whenever any user mentions a phrase or word you have set up.
It will also let you know the proper way to return a "Hello There" greeting.


## Usage
The bot currently has four slash commands: `watch`, `dontwatch`, `watchlist`, and `hellothere`.
After installation and setup, your users be able to use the commands as follows: 

| Command | Value to Input | Description |
| ------ | ------ | ------ |
| /watch | Anything | Adds a word to the bot's list. If the word is spoken then you'll be informed |
| /dontwatch | An item from your list | Removes a word from the bot's list. You'll no longer be notified when it's spoken | 
| /watchlist | N/A | The bot will tell you what words you're currently monitoring. |
| /hellothere | N/A | The bot will let you know the proper greeting after someone says "Hello There" |



### Creating the Slack bot
Let's walk through how to create a bot and add the functionality!

We will first need to create the but on Slack's website in order for you to generate the bot and keys. 

 - Ensure you're logged into a Slack workspace
 - Navigate to [Slack's bot creation](https://api.slack.com/apps?new_app=1)
 - Type in an App Name and select your development workspace
![Adding bot to Workspace](link-to-image)
 - Scroll down the page and you'll see the *App Credentials* section.
 ![App Credentials](link-to-image)
 - Save the the `Signing Secret`. We weill be using this shortly.
 - Now, on the left side click the option for `OAuth & Permissions`. Scroll down to the `Scopes` section. Add the `channels:history`, `chat:write`, `commands`,  `im:write`, `users:read` permissions.
 ![Scopes used](link-to-image)
 
 - Now, on the left side click the option for `Install App`
 - Here you'll see a button to `Install App to Workspace`. Click on it and you'll the bot will request permissions to be installed. 
![Installing to workspace](link-to-image)
- Accept the permissions and you'll be given an OAuth token. Save this as we will use this in the next section.
![OAuth Token](link-to-image)
- Now that we have those keys. Let's start our server!



### Installation and starting the service
Now that we have our authorization keys, let's start up the service that the bot will listen to.

- Ensure you have [docker installed](https://docs.docker.com/get-docker/)
- Clone this repository locally by opening your terminal. Then moving to a directory of your choice:
```
cd ~/folder
```

- Then we clone this Github repository locally:
```
git clone https://github.com/phillram/grievous-slackbot.git
```

- Now let's move to that directory:
```
cd ~/folder/grievous-slackbot
```

- Now we can start up the service the bot will listen to. In your terminal we can use the dockerfile to set our options and start up the service. You'll need to use input your Slack bot keys from the prerequisites above.
- The docker options:
| Option | Value to Input |
| ------ | ------ |
| signing_secret | SLACK_SIGNING_SECRET from above |
| bot_token | SLACK_BOT_TOKEN from above |
| port | Any port you wish (optional) |


- Now let's add our options and build our docker app, and call it `grievous`:

```
docker build -t grievous . --build-arg signing_secret=SLACK_SIGNING_SECRET --build-arg bot_token=SLACK_BOT_TOKEN
```

- Wait until that builds and completes.
- Afterwards, let's start it up:

```sh
docker run grievous
```
- Wait for it to complete. 
- When it's ready you'll see the console waiting on:

> [<NgrokTunnel: "http://991aed92.ngrok.io" -> "http://localhost:5000">,
> <NgrokTunnel: "https://991aed92.ngrok.io" -> "http://localhost:5000">]
> Serving Flask app "app" (lazy loading)
> Environment: production
> WARNING: This is a development server. Do not use it in a production deployment.
> Use a production WSGI server instead.
> Debug mode: off
> Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

- The bot is now up and running. `Take note of the Ngrok URL started!`. In this case it's `https://991aed92.ngrok.io`. We will be using that to complete the bot setup. 
- *Note*: The Ngrok URL will change every time you start the service



### Adding slash command functionality
Perfect! Now that our service is set up, let's point the Slack bot to our Ngrok instance. This will allow it to actually run his commands.

 - Navigate to [your Slack Apps](https://api.slack.com/apps), and then select the app you just made.
 - Click on the `Slash Commands` menu on the left side to start adding commands.
 - Click `Create New Command` 
![Creating a new slash command](link-to-image)

- In this menu we will add our command, the URL, and descriptions for each of the four commands. Be sure to save at the bottom right.
- I will use my Ngrok service from above (`https://991aed92.ngrok.io`) for this example. *Please be sure to replace it with your own*.

| Command | Request URL | Description | Usage Hint |
| ------ | ------ | ------ | ------ |
| /watch | https://991aed92.ngrok.io/slack/watch | Add to the watchlist | What am I looking for? |
| /dontwatch | https://991aed92.ngrok.io/slack/dontwatch | Remove from the watchlist | Ignore this word |
| /watchlist | https://991aed92.ngrok.io/slack/watchlist | Displays what words you're watching | What am I looking for? |
| /hellothere | https://991aed92.ngrok.io/slack/hellothere | A greeting from Grievous |  |

![Completed watch command](link-to-image)


- For the final piece, we want to make sure that the bot can read the chat messages. It would then message you when the words you set up are found.
- Click on `Event Subsciptions` on the menu. Toggle the option to `On`.
- Add the request URL. This would be the same as your Ngrok above but with `/slack/events` as a suffix.
- Click the dropdown option for `Subscribe to bot events`, click `Add Bot User Event`, and then add `message.channels`. Click Save in the bottom right.
![Adding Events](link-to-image)
- Congrats! The bot should now be active and respond to the slash commands you've set up!



### Recieving DMs
Slack only authorizes bots to read channels that they are currently members of. So we'll just have to invite the bot using the normal `/invite` command.

- Go to your Slack workspace and navigate to the channel you wish to listen to
- Type `/invite grievous` (or whatever you've named the bot), then press enter.

Now feel free to try it out as much as you'd like!



### To be added
- Implement OAuth so that users won't have to manually make the bot everytime. Currently, it's quite a bit of hassle and that's just a bit much.
- Make it more docker-compose friendly.
- Add testing assertations. 
- Don't allow users to add blank words.
- Don't allow users to add the same word multiple times.