import os
import json
import schedule
import time
import logging
from datetime import date, timedelta
from slackclient import SlackClient

from csponsheet import getCSPONUpdate
from fundsheet import getRDFundUpdate

logging.basicConfig(level=logging.DEBUG)
# set MENTIONS env var with the following format
# json of the form '{'name': '<uid>'}' where name is your label for the person
# get uid via GET from users.list in slack api
# mentions = '{'@username': 'UXXXXXXXX'}'

def sendCSPONUpdate():
  ipcount, ip, l, w, c = getCSPONUpdate()
  ipstr, lstr, wstr, cstr = '','','',''

  if len(c) > 0:
    cstr = ("*Sales Closed* - _HELL YEA! Congrats!_\n"
        + ''.join([" - {} | {} | {}\n\n".format(k, MENTIONS[c[k]["director"]], c[k]["date"]) for k in c]))
  if len(w) > 0:
    wstr = ("*Wins* - _YAY! Good news :) Remember to see these all the way through!_\n"
        + ''.join([" - {} | {} | {}\n\n".format(k, MENTIONS[w[k]["director"]], w[k]["date"]) for k in w]))
  if len(l) > 0:
    lstr = ("*Losses* - _It happens. Please remember to fill out insights from this contact in the sheet. Onwards!_\n"
        + ''.join([" - {} | {} | {}\n\n".format(k, MENTIONS[l[k]["director"]], l[k]["date"]) for k in l]))
  if len(ip) > 0:
    ipstr = ("*In Progress* - _{} | {} | {}_ - _Good work. Remember to keep following up._\n".format("Company", "@director", "Last Contacted Date")
        + "> Only thoese overdue for followup (5 days) are listed here. See the sheet for details\n"
        + ''.join([" - {} | {} | {}\n".format(k, MENTIONS[ip[k]["director"]], ip[k]["date"]) for k in ip]))

  ipstr = ipstr + "Total in progress emails: {}\n".format(ipcount)

  updates = cstr + wstr + lstr + ipstr
  if len(updates) is 0:
    updates = "None!"

  allText = ("*CSPON Updates*: {} - {}\n\n".format(date.today() - timedelta(8), date.today() - timedelta(1))
              + updates)

  # print allText
  updateMsg = slack_client.api_call(
    "chat.postMessage",
    channel='#slackbot-test',
    text=allText
  )

  if updateMsg['ok'] is not True:
    logging.error(updateMsg)
  else:
    logging.debug(updateMsg)

def sendRDFundUpdate():
  cashVal, stockVal, accountVal, percent, absolute = getRDFundUpdate()

  heading = ("*Fund Updates*: {} - {}\n\n".format(date.today() - timedelta(8), date.today() - timedelta(1)))

  sign = '+' if absolute >= 0 else '-'
  chstr = "Since last week: *{}{}% | {}${}*\n".format(sign, round(abs(percent), 2), sign, round(abs(absolute), 2))
  cstr = "```Cash Value: ${}\n".format(round(cashVal, 2))
  sstr = "Stock Value: ${}\n".format(round(stockVal, 2))
  astr = "Total Account Value: ${}```\n".format(round(accountVal, 2))
  auxstr = "(See the pinned sheet for details!)"

  allText = heading + chstr + cstr + sstr + astr + auxstr

  # print allText
  updateMsg = slack_client.api_call(
    "chat.postMessage",
    channel='#slackbot-test',
    text=allText
  )

  if updateMsg['ok'] is not True:
    logging.error(updateMsg)
  else:
    logging.debug(updateMsg)

if __name__ == "__main__":
  SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
  SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
  MENTIONS = json.loads(os.environ['MENTIONS'])
  slack_client = SlackClient(SLACK_BOT_TOKEN)

  # # For testing
  schedule.every(30).seconds.do(sendCSPONUpdate)
  # schedule.every(30).seconds.do(sendRDFundUpdate)

  schedule.every().tuesday.at("09:15").do(sendCSPONUpdate)
  schedule.every().friday.at("16:01").do(sendRDFundUpdate)

  while True:
    schedule.run_pending()
    # time.sleep(600)
    time.sleep(5)
