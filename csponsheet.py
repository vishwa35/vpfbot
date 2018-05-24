import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, timedelta
from dateutil.parser import parse

def getCSPONUpdate():
  # client / auth
  scope = ['https://spreadsheets.google.com/feeds',
  'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
  client = gspread.authorize(creds)

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
  wlCol = cspon.find("Win/Loss Date").col

  # gets first 200 rows of contacts
  saleStatuses = cspon.range(baseR, baseC, baseR + 200, baseC)

  # dictionaries to track relevant cases
  ip = {}
  ipcount = 0
  l = {}
  w = {}
  c = {}

  lastWeek = date.today() - timedelta(7)
  fiveDays = date.today() - timedelta(5)

  # check all 200 statuses for: IP, W, L, C
  for s in saleStatuses:
    if s.value == "IP":
      ipcount += 1
      try:
        lastEmail = parse(cspon.cell(s.row, lastEmailCol).value).date()
        if lastEmail <= fiveDays:
          ip[cspon.cell(s.row, companyCol).value] = {"director": cspon.cell(s.row, directorCol).value, "date": lastEmail}
      except ValueError:
        print "IP -- No last email date for {}, {}".format(s.row, s.col)

    if s.value == "W" or s.value == "L" or s.value == "C" :
      try:
        nDate = parse(cspon.cell(s.row, wlCol).value).date()
        if s.value == "W" and nDate >= lastWeek:
          w[cspon.cell(s.row, companyCol).value] = {"director": cspon.cell(s.row, directorCol).value, "date": nDate}
        elif s.value == "L" and nDate >= lastWeek:
          l[cspon.cell(s.row, companyCol).value] = {"director": cspon.cell(s.row, directorCol).value, "date": nDate}
        elif s.value == "C" and nDate >= lastWeek:
          c[cspon.cell(s.row, companyCol).value] = {"director": cspon.cell(s.row, directorCol).value, "date": nDate}
      except ValueError:
        print "W/L/C -- No date for {}, {}".format(s.row, s.col)

  return ipcount, ip, l, w, c
