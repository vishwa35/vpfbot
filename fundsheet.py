import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, timedelta
from dateutil.parser import parse
import re

def getRDFundUpdate(client):
  # # client / auth
  # scope = ['https://spreadsheets.google.com/feeds',
  # 'https://www.googleapis.com/auth/drive']
  # creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
  # client = gspread.authorize(creds)

  # Get Fund Sheets
  rdspreadsheet = client.open("Raza-Dhanani Fund - 03/2017 onwards")
  fund = rdspreadsheet.sheet1
  week2week = rdspreadsheet.get_worksheet(1)

  # corner to start from
  row = fund.find("TOTAL").row
  col = fund.find(" Unrealized Gain ($) ").col

  # gets stats on RD fund from sheet
  gain = fund.cell(row + 1, col).value
  cashVal = fund.cell(row + 2, col).value
  capitalInvested = fund.cell(row + 3, col).value

  values = [gain, cashVal, capitalInvested]
  values = tuple([float(re.sub('[^0-9.]', '', val)) for val in values])

  gain, cashVal, capitalInvested = values
  stockVal = capitalInvested + gain
  accountVal = cashVal + stockVal


  # record new values
  week2week.append_row([str(date.today()), cashVal, stockVal, accountVal])

  # compute change from past week
  lastRow = week2week.row_count
  totalCol = week2week.find("Total Portfolio Value").col
  lastWeek = float(re.sub('[^0-9.]', '', week2week.cell(lastRow, totalCol).value))

  percent = 100*(accountVal - lastWeek)/lastWeek
  absolute = accountVal - lastWeek

  return cashVal, stockVal, accountVal, percent, absolute