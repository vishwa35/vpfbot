import schedule
import time
from datetime import date, timedelta
from slackclient import SlackClient

from tokens import SLACK_BOT_TOKEN, SLACK_VERIFICATION_TOKEN
from csponsheet import getCSPONUpdate

def sendCSPONUpdate():
  ip_count, ip, l, w, c = getCSPONUpdate()
  ipstr, lstr, wstr, cstr = '','','',''

  if len(c) > 0:
    cstr = ("*Sales Closed* - _HELL YEA! Congrats!_\n"
        + ''.join([" - {} | {} | {}\n\n".format(k, ip[k]["director"], ip[k]["date"]) for k in c]))
  if len(w) > 0:
    wstr = ("*Wins* - _YAY! Good news :) Remember to see these all the way through!_\n"
        + ''.join([" - {} | {} | {}\n\n".format(k, ip[k]["director"], ip[k]["date"]) for k in w]))
  if len(l) > 0:
    lstr = ("*Losses* - _It happens. Please remember to fill out insights from this contact in the sheet. Onwards!_\n"
        + ''.join([" - {} | {} | {}\n\n".format(k, ip[k]["director"], ip[k]["date"]) for k in l]))
  if len(ip) > 0:
    ipstr = ("*In Progress* - _{} | {} | {}_ - _Good work. Remember to keep following up._\n".format("Company", "@director", "Last Contacted Date")
        + "> Only thoese overdue for followup (5 days) are listed here. See the sheet for details\n"
        + ''.join([" - {} | {} | {}\n".format(k, ip[k]["director"], ip[k]["date"]) for k in ip])
        + "Total outstanding emails: {}\n".format(ip_count))

  updates = cstr + wstr + lstr + ipstr
  if len(updates) is 0:
    updates = "None!"

  allText = ("CSPON Updates for the week: *{} - {}*\n\n".format(date.today() - timedelta(8), date.today() - timedelta(1))
              + updates)

  print allText
  # updateMsg = slack_client.api_call(
  #   "chat.postMessage",
  #   channel='#cspon-f18',
  #   text=allText
  # )["message"]


if __name__ == "__main__":
  slack_client = SlackClient(SLACK_BOT_TOKEN)

  schedule.every(30).seconds.do(sendCSPONUpdate)
  # schedule.every().tuesday.at("09:15").do(sendCSPONUpdate)
  # schedule.every().friday.at("16:01").do(sendFundUpdate)
  while True:
    schedule.run_pending()
    time.sleep(5)
