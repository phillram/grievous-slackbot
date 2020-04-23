
FROM python:3

COPY requirements.txt /tmp
WORKDIR /tmp
RUN pip install -r requirements.txt

ARG signing_secret=0
ENV SLACK_SIGNING_SECRET=$signing_secret

ARG bot_token=0
ENV SLACK_BOT_TOKEN=$bot_token

ARG port=5000
ENV FLASK_PORT=$port

ARG use_heroku=False
ENV SLACK_BOT_HEROKU=$use_heroku

EXPOSE $FLASK_PORT

ADD app.py app.py
CMD [ "python", "./app.py" ]