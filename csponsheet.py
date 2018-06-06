import os, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, timedelta
from dateutil.parser import parse

def getCSPONUpdate(client):
  # # client / auth
  # scope = ['https://spreadsheets.google.com/feeds',
  # 'https://www.googleapis.com/auth/drive']
  # js = json.loads(os.environ['GDRIVE_SECRET'].replace("\n", "\\n"))
  # with open('client_secret.json', 'w') as d:
  #   json.dump(js, d)
  # creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
  # os.remove('client_secret.json')
  # client = gspread.authorize(creds)

  # Get CSpon Sheet
  cspon = client.open("2018-19 Contacts").sheet1

  # corner to start from
  base = cspon.find("Sale Status")
  baseR, baseC = base.row + 1, base.col

  # Get other relevant col numbers
  directorCol = cspon.find("Director In Charge").col
  companyCol = cspon.find("Company").col
  initialEmailCol = cspon.find("Initial Email Date").col
  lastEmailCol = cspon.find("Last Email Date").col
  eventCol = cspon.find("Target Event?").col
  wlCol = cspon.find("Win/Loss/Close/Call Date").col

  # gets first 200 rows of contacts
  saleStatuses = cspon.range(baseR, baseC, baseR + 200, baseC)

  # dictionaries to track relevant cases
  ip = {}
  ipcount = 0
  ccount = 0
  l = {}
  w = {}
  sc = {}
  c = {}

  lastWeek = date.today() - timedelta(7)
  fiveDays = date.today() - timedelta(5)

  # check all 200 statuses for: IP, W, L, C
  for s in saleStatuses:
    if s.value != None and s.value != '':
      row = cspon.row_values(s.row)
    if s.value == "IP":
      ipcount += 1
      try:
        lastEmail = parse(row[lastEmailCol - 1]).date()
        if lastEmail <= fiveDays:
          ip[row[companyCol - 1]] = {"director": row[directorCol - 1], "date": lastEmail}
      except ValueError:
        print "IP -- No last email date for {}, {}".format(s.row, s.col)
      except IndexError:
        print "IP -- No last email date for {}, {}".format(s.row, s.col)
    elif s.value == "C":
      ccount += 1
      try:
        nDate = parse(row[wlCol - 1]).date()
      except ValueError:
        print "C -- No date for {}, {}".format(s.row, s.col)
        nDate = "no date"
      except IndexError:
        print "C -- No date for {}, {}".format(s.row, s.col)
        nDate = "no date"
      c[row[companyCol - 1]] = {"director": row[directorCol - 1], "date": nDate}

    elif s.value == "W" or s.value == "L" or s.value == "SC" :
      try:
        nDate = parse(row[wlCol - 1]).date()
        if s.value == "W" and nDate >= lastWeek:
          w[row[companyCol - 1]] = {"director": row[directorCol - 1], "date": nDate}
        elif s.value == "L" and nDate >= lastWeek:
          l[row[companyCol - 1]] = {"director": row[directorCol - 1], "date": nDate}
        elif s.value == "SC" and nDate >= lastWeek:
          sc[row[companyCol - 1]] = {"director": row[directorCol - 1], "date": nDate}
      except ValueError:
        print "W/L/SC -- No date for {}, {}".format(s.row, s.col)
      except IndexError:
        print "W/L/SC -- No date for {}, {}".format(s.row, s.col)


  return ipcount, ip, l, w, sc, ccount, c

# for testing
# print getCSPONUpdate()