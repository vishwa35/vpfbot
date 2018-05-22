from flask import Flask, request, make_response, Response
import json
from collections import defaultdict
from tokens import SLACK_BOT_TOKEN, SLACK_VERIFICATION_TOKEN
from slackclient import SlackClient
from csponsheet import getUpdates
from datetime import date, timedelta
from weekly import *

slack_client = SlackClient(SLACK_BOT_TOKEN)
app = Flask(__name__)

#TODO: Add checks for all responses from slack api calls

def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)

# @app.route("/slack/actions", methods=["POST"])
# def actions():

  form_json = json.loads(request.form["payload"])
  callback_id = form_json['callback_id']
  verify_slack_token(form_json["token"])

  # do something here from interactive component

  return make_response("", 200)

# @app.route("/slack/cspon", methods=["POST"])
# def cspon():
#   result = sendCSPONUpdate()
#   return make_response("", 200)

# @app.route("/slack/venmo", methods=["POST"])
# def venmo():
  # return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
  app.run()