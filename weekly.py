import os
import json
import schedule
import time
import logging
from datetime import date, timedelta
from slackclient import SlackClient

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from csponsheet import getCSPONUpdate
from fundsheet import getRDFundUpdate

logging.basicConfig(level=logging.DEBUG)
# set MENTIONS env var with the following format
# json of the form '{'name': '<uid>'}' where name is your label for the person
# get uid via GET from users.list in slack api
# mentions = '{'@username': 'UXXXXXXXX'}'

def sendCSPONUpdate(gclient, slack_client):
  ipcount, ip, l, w, sc, ccount, c = getCSPONUpdate(gclient)
  ipstr, lstr, wstr, scstr, cstr = '','','','',''

  if len(sc) > 0:
    scstr = ("*Sales Closed* :white_check_mark:- _HELL YEA! Congrats!_\n"
        + ''.join([" - {} | <@{}> | {}\n\n".format(k, MENTIONS[sc[k]["director"]], sc[k]["date"].strftime("%m/%d")) for k in sc]))
  if len(w) > 0:
    wstr = ("*Wins* :trophy:- _YAY! Good news :) Remember to see these all the way through!_\n"
        + ''.join([" - {} | <@{}> | {}\n\n".format(k, MENTIONS[w[k]["director"]], w[k]["date"].strftime("%m/%d")) for k in w]))
  if len(l) > 0:
    lstr = ("*Losses* :no_entry_sign:- _It happens. Please remember to fill out insights from this contact in the sheet. Onwards!_\n"
        + ''.join([" - {} | <@{}> | {}\n\n".format(k, MENTIONS[l[k]["director"]], l[k]["date"].strftime("%m/%d")) for k in l]))
  if len(ip) > 0:
    ipstr = ("*{} In Progress* :hourglass_flowing_sand:- _{} | {} | {}_ - _Good work. Remember to keep following up._\n".format(ipcount, "Company", "@director", "Last Contacted Date")
        + "> Only those overdue for followup (5 days) are listed here. See the sheet for details\n"
        + ''.join([" - {} | <@{}> | {}\n".format(k, MENTIONS[ip[k]["director"]], ip[k]["date"].strftime("%m/%d")) for k in ip]))
  if len(c) > 0:
    cstr = ("*{} Calls Scheduled* :slack_call:- _{} | {} | {}_ - _Good Luck!_\n".format(ccount, "Company", "@director", "Date")
        + ''.join([" - {} | <@{}> | {}\n".format(k, MENTIONS[c[k]["director"]], c[k]["date"].strftime("%m/%d")) for k in c]))

  # ipstr = ipstr + "Total in progress emails: {}\n".format(ipcount)
  # cstr = cstr + "Total calls scheduled: {}\n".format(ccount)

  updates = scstr + wstr + lstr + ipstr + cstr
  if len(updates) is 0:
    updates = "None!"

  allText = (":information_source: *CSPON Updates*: {} - {}\n\n".format((date.today() - timedelta(8)).strftime("%m/%d/%y"), (date.today() - timedelta(1)).strftime("%m/%d/%y"))
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

def sendRDFundUpdate(gclient, slack_client):
  cashVal, stockVal, accountVal, percent, absolute = getRDFundUpdate(gclient)

  heading = (":moneybag: *Fund Updates*: {} - {}\n\n".format((date.today() - timedelta(7)).strftime("%m/%d/%y"), date.today().strftime("%m/%d/%y")))

  sign = '+' if absolute >= 0 else '-'
  chstr = "Since last week: *{}{}% | {}${}*\n".format(sign, round(abs(percent), 2), sign, round(abs(absolute), 2))
  cstr = "```Cash Value: ${}\n".format(round(cashVal, 2))
  sstr = "Stock Value: ${}\n".format(round(stockVal, 2))
  astr = "Total Account Value: ${}```\n".format(round(accountVal, 2))
  auxstr = ":information_source: See the pinned sheet for details!"

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
  # print os.environ['MENTIONS']
  MENTIONS = json.loads(os.environ['MENTIONS'])
  slack_client = SlackClient(SLACK_BOT_TOKEN)
  logging.debug("authorized slack client")

  scope = ['https://spreadsheets.google.com/feeds',
  'https://www.googleapis.com/auth/drive']
  js = json.loads(os.environ['GDRIVE_SECRET'].replace("\n", "\\n"))
  with open('secret.json', 'w') as d:
    json.dump(js, d)
  creds = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scope)
  client = gspread.authorize(creds)
  os.remove('secret.json')
  logging.debug("authorized to google")

  # # For testing
  schedule.every(60).seconds.do(lambda: sendCSPONUpdate(client, slack_client))
  schedule.every(60).seconds.do(lambda: sendRDFundUpdate(client, slack_client))

  # schedule.every().monday.at("18:15").do(lambda: sendCSPONUpdate(client, slack_client))
  # schedule.every().friday.at("16:01").do(lambda: sendRDFundUpdate(client, slack_client))
  logging.info("entering run loop")

  while True:
    if creds.access_token_expired:
      client.login()  # refreshes the token
    schedule.run_pending()
    # time.sleep(600)
    time.sleep(5)
