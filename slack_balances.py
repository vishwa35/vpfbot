import os
import csv
import json
import time
import logging
from datetime import date, timedelta
from slackclient import SlackClient

# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
  # MENTIONS = json.loads(os.environ['MENTIONS'])
  SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
  SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
  slack_client = SlackClient(SLACK_BOT_TOKEN)
  logging.debug("authorized slack client")

  slackids = {}
  with open('slackids.json', 'rb') as file:
    slackids = json.load(file)

  logging.info("entering run loop")

  with open('daybeforecogs.csv', 'rb') as csvfile:
    members = csv.reader(csvfile)
    for mem in members:
      if mem[2] == "Collegiate":
        print '\n'
        print mem
        if mem[3] == '0.00' or mem[3] == '0':

          # msg = "Apologies for the useless message. You currently owe nothing. Thanks for paying your dues on time!"
          # openChannel = slack_client.api_call(
          #   "conversations.open",
          #   users=slackids[mem[0]]
          # )
          # sendMsg = slack_client.api_call(
          #   "chat.postMessage",
          #   channel=openChannel["channel"]["id"],
          #   # channel='#slackbot-test',
          #   text=msg
          # )

          # if sendMsg['ok'] is not True:
          #   logging.error(sendMsg)
          # else:
          #   logging.debug(sendMsg)

          logging.info("Zero balance: {}".format(mem[1]))
        elif mem[0] in slackids.keys():
        # elif mem[0] == '859480' and mem[0] in slackids.keys():
          print "executing"
          uid = slackids[mem[0]]
          amt = mem[3]
          firstduesmsg = "Time for Fall 2018 Dues! :flying_money_with_wings: You currently owe *${}*-- please venmo :venmo: @gtakpsi, pay via check, or pay on chapterspot.com (+3% transaction fee). Due August 30!\n>Note: If you venmo, you should receive a confirmation message within 30 (or so) minutes! If you think there is an error, please slack @vishwa. If you would like a payment plan, please fill out this form: https://goo.gl/forms/MXbsr1FnMu5obJQM2".format(amt)
          # dayofmsg = "Fall 2018 Dues are due *TODAY*! :flying_money_with_wings: You currently owe *${}*-- please venmo :venmo: @gtakpsi, pay via check, or pay on chapterspot.com (+3% transaction fee).\n>Note: If you venmo, you should receive a confirmation message within 30 (or so) minutes! If you think there is an error, please slack @vishwa. If you would like a payment plan, please fill out this form: https://goo.gl/forms/MXbsr1FnMu5obJQM2".format(amt)
          # msg = "Time for Fall 2018 Dues! :flying_money_with_wings: You currently owe ${}-- please venmo :venmo: @gtakpsi, pay via check, or pay on chapterspot.com (+3% transaction fee). Due August 30!".format(amt)
          # msgAR = "Time for Fall 2018 A/R! :flying_money_with_wings: You currently owe ${}-- please venmo :venmo: @gtakpsi, pay via check, or pay on chapterspot.com (+3% transaction fee). Due November 29 (COGS!)!\n>Note: If you venmo, you should receive a confirmation message within 30 (or so) minutes! If you think there is an error, please slack @vishwa. If you would like a payment plan, please fill out this form: https://goo.gl/forms/MXbsr1FnMu5obJQM2".format(amt)
          # msgARv2 = "You have pending Fall 2018 A/R! :flying_money_with_wings: You currently owe ${}-- please venmo :venmo: @gtakpsi, pay via check, or pay on chapterspot.com (+3% transaction fee). Due November 29 (COGS!)!\n>Note: Credit has been given for everything remaining (credits are updated as of 1 hour ago), and Blue Sapphire Tshirts have been charged for.If you think there is an error, please check chapterspot and then slack @vishwa. If you would like a payment plan, please fill out this form: https://goo.gl/forms/MXbsr1FnMu5obJQM2".format(amt)
          msgARv3 = "You have pending Fall 2018 A/R, due *TOMORROW*! :flying_money_with_wings: You currently owe ${}-- please venmo :venmo: @gtakpsi, pay via check, or pay on chapterspot.com (+3% transaction fee). Due November 29 (COGS!)!\n>Note: All charges, credits and fines are updated. If you think there is an error, please check chapterspot and then slack @vishwa. If you would like a payment plan, please fill out this form: https://goo.gl/forms/MXbsr1FnMu5obJQM2".format(amt)
          
          # CHANGE THIS PER DAY
          msg = msgARv3

          openChannel = slack_client.api_call(
            "conversations.open",
            users=slackids[mem[0]]
          )
          sendMsg = slack_client.api_call(
            "chat.postMessage",
            channel=openChannel["channel"]["id"],
            # channel='#slackbot-test',
            text=msg
          )

          if sendMsg['ok'] is not True:
            logging.error(sendMsg)
          else:
            logging.debug(sendMsg)
        else:
          logging.warning(mem[0] + "not in slackids")

