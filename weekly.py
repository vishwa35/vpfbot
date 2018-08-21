import os
import json
import schedule
import time
import logging
from datetime import date, datetime, timedelta
from slackclient import SlackClient

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, tools
from oauth2client import client as oauth_client

from csponsheet import getCSPONUpdate
from fundsheet import getRDFundUpdate, getPFundUpdate

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
        + ''.join([" - {} | <@{}> | {}\n\n".format(k, MENTIONS[sc[k]["director"]], (sc[k]["date"]).strftime("%m/%d")) for k in sc]))
  if len(w) > 0:
    wstr = ("*Wins* :trophy:- _YAY! Good news :) Remember to see these all the way through!_\n"
        + ''.join([" - {} | <@{}> | {}\n\n".format(k, MENTIONS[w[k]["director"]], (w[k]["date"]).strftime("%m/%d")) for k in w]))
  if len(l) > 0:
    lstr = ("*Losses* :no_entry_sign:- _It happens. Please remember to fill out insights from this contact in the sheet. Onwards!_\n"
        + ''.join([" - {} | <@{}> | {}\n\n".format(k, MENTIONS[l[k]["director"]], (l[k]["date"]).strftime("%m/%d")) for k in l]))
  if len(ip) > 0:
    ipstr = ("*{} In Progress* :hourglass_flowing_sand:- _{} | {} | {}_ - _Good stuff. Remember to keep following up._\n".format(ipcount, "Company", "@director", "Last Contacted Date")
        + "> Only those overdue for followup (5 days) are listed here. See the sheet for details\n"
        + ''.join([" - {} | <@{}> | {}\n".format(k, MENTIONS[ip[k]["director"]], (ip[k]["date"]).strftime("%m/%d")) for k in ip]))
  if len(c) > 0:
    cstr = ("*{} In Call Stage* :slack_call:- _{} | {} | {}_ - _Good Luck!_\n".format(ccount, "Company", "@director", "Date")
        + ''.join([" - {} | <@{}> | {}\n".format(k, MENTIONS[c[k]["director"]], (c[k]["date"]).strftime("%m/%d")) for k in c]))

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
    channel='#cspon-f18',
    # channel='#slackbot-test',
    text=allText
  )

  if updateMsg['ok'] is not True:
    logging.error(updateMsg)
  else:
    logging.debug(updateMsg)

def sendFundUpdate(gclient, slack_client):
  heading = (":moneybag: *Fund Updates*: {} - {}\n\n".format((date.today() - timedelta(7)).strftime("%m/%d/%y"), date.today().strftime("%m/%d/%y")))

  cashVal, stockVal, accountVal, percent, absolute = getRDFundUpdate(gclient)
  fname = "_Raza Dhanani Fund:_ "
  sign = '+' if absolute >= 0 else '-'
  chstr = "*{}{}% | {}${}* (since last week)\n".format(sign, round(abs(percent), 2), sign, round(abs(absolute), 2))
  cstr = "```Cash Value: ${}\n".format(round(cashVal, 2))
  sstr = "Stock Value: ${}\n".format(round(stockVal, 2))
  astr = "Total Account Value: ${}```\n".format(round(accountVal, 2))

  rdText = fname + chstr + cstr + sstr + astr

  cashVal, stockVal, accountVal, percent, absolute = getPFundUpdate(gclient)
  fname = "_Phoenician Fund:_ "
  sign = '+' if absolute >= 0 else '-'
  chstr = "*{}{}% | {}${}* (since last week)\n".format(sign, round(abs(percent), 2), sign, round(abs(absolute), 2))
  cstr = "```Cash Value: ${}\n".format(round(cashVal, 2))
  sstr = "Stock Value: ${}\n".format(round(stockVal, 2))
  astr = "Total Account Value: ${}```\n".format(round(accountVal, 2))

  pfText = fname + chstr + cstr + sstr + astr

  auxstr = ":information_source: See the pinned sheets for details!"
  allText = heading + rdText + pfText + auxstr

  # print allText
  updateMsg = slack_client.api_call(
    "chat.postMessage",
    channel='#the-fund',
    # channel='#slackbot-test',
    text=allText
  )

  if updateMsg['ok'] is not True:
    logging.error(updateMsg)
  else:
    logging.debug(updateMsg)

def checkGmailForVenmo(service, slackids, slack_client, lastchecked):
  paymentsLabel = 'Label_1'
  venmoSlackLabel = 'Label_830267486826221758'
  # Call the Gmail API
  logging.debug("Last Checked: {}".format(lastchecked))
  lastchecked = datetime.now()
  d = lastchecked.strftime('%Y/%m/%d')

  results = service.users().messages().list(userId='me', q='from:(venmo@venmo.com) AND "paid you" AND after:{} AND NOT label:venmo-slack '.format(d)).execute()
  messages = results.get('messages', [])
  for m in messages:
    # print m
    metadata = service.users().messages().get(userId='me', id=m['id'], format='metadata', metadataHeaders='Subject').execute()
    if venmoSlackLabel not in metadata['labelIds']:
      emailid = metadata["id"]
      subj = metadata["payload"]["headers"][0]["value"]
      splitstring = subj.split("paid you")
      splitstring = list(map(lambda x: x.rstrip().lstrip(), splitstring))
      if splitstring[0] in slackids.keys():
        uid = slackids[splitstring[0]]
        msg = "Received a Venmo payment of {}. (ID: {})".format(splitstring[1], emailid)
        openChannel = slack_client.api_call(
          "conversations.open",
          users=uid
        )
        sendMsg = slack_client.api_call(
          "chat.postMessage",
          channel=openChannel["channel"]["id"],
          text=msg
        )
        service.users().messages().modify(userId='me', id=m['id'], body={'removeLabelIds': ['INBOX'], 'addLabelIds': [paymentsLabel, venmoSlackLabel]}).execute()

        if sendMsg['ok'] is not True:
          logging.error(sendMsg)
        else:
          logging.debug(sendMsg)
  return lastchecked

def ListMessagesMatchingQuery(service, user_id, query=''):
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print 'An error occurred: %s' % error



if __name__ == "__main__":
  SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
  SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
  # print os.environ['MENTIONS']
  MENTIONS = json.loads(os.environ['MENTIONS'])
  slackids = json.loads(os.environ['NAME2SLACK'])
  slack_client = SlackClient(SLACK_BOT_TOKEN)
  logging.debug("authorized slack client")
  scope = ['https://spreadsheets.google.com/feeds',
  'https://www.googleapis.com/auth/drive']
  js = json.loads(os.environ['GDRIVE_SECRET'].replace("\n", "\\n"))
  with open('secret.json', 'w') as d:
    json.dump(js, d)
  creds = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scope)
  client = gspread.authorize(creds)

  # slackids = {}
  # with open('name2slack.json', 'rb') as afile:
  #   slackids = json.load(afile)

  os.remove('secret.json')

# copy paste quickstart

  SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
  store = file.Storage('token.json')
  creds = store.get()
  if not creds or creds.invalid:
    credentialsjson = json.loads(os.environ['CREDENTIALS'].replace("\n", "\\n"))
    with open('credentials.json', 'w') as d:
      json.dump(credentialsjson, d)
    flow = oauth_client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
    os.remove('credentials.json')
  service = build('gmail', 'v1', http=creds.authorize(Http()))

  logging.debug("authorized to google")

  LASTCHECKED = (datetime.today() - timedelta(days=1))
  LASTCHECKED = checkGmailForVenmo(service, slackids, slack_client, LASTCHECKED)
  # m = ListMessagesMatchingQuery(service, 'me', 'from:(venmo@venmo.com) "paid you" after:2018/8/20')
  # print m

  # # For testing
  # schedule.every(60).seconds.do(lambda: sendCSPONUpdate(client, slack_client))
  # schedule.every(60).seconds.do(lambda: sendFundUpdate(client, slack_client))

  # schedule.every().monday.at("13:15").do(lambda: sendCSPONUpdate(client, slack_client))
  schedule.every().friday.at("20:01").do(lambda: sendFundUpdate(client, slack_client))
  schedule.every(30).minutes.do(lambda: checkGmailForVenmo(service, slackids, slack_client, LASTCHECKED))
  logging.info("entering run loop")

  while True:
    if creds.access_token_expired:
      client.login()  # refreshes the token
    schedule.run_pending()
    time.sleep(600)
    # time.sleep(5)
