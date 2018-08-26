# vpfbot

Feel free to star or fork if you find this useful! A bunch of automation/slack integrations to make my time as VP of Finance for [GT AKPsi](https://www.gtakpsi.com/) a little more convenient.

## Scheduled Messages: `weekly.py`

### constructing a weekly update message based on a Google Sheet

CSPON Updates: [a week ago] - [yesterday]

**Sales Closed** - _HELL YEA! Congrats!_
- Company | @director | Date

**Wins** - _YAY! Good news :) Remember to see these all the way through!_
- Company | @director | Date

**Losses** - _It happens. Please remember to fill out insights from this contact in the sheet. Onwards!_
- Company | @director | Date

**In Progress** - _Company | @director | Last Contacted Date_ - _Good work. Remember to keep following up._
> Only those overdue for followup (5 days) are listed here. See the sheet for details

- Company | @director | Date

Total in progress emails: XX

**Calls Scheduled** - _Company | @director | Date_ - _Good Luck!_

- Company | @director | Date

Total calls scheduled: XX

### weekly updates on our fund status

##### [TODO] add special projects fund status

Raza-Dhanani Fund Updates: [a week ago] - [yesterday]

Since last week: +/-X% | +/-$XX.XX

**Cash Value**: $XXX.XX

**Stock Value**: $XXX.XX

**Total Account Value**: $XXX.XX

> (See the pinned sheet for details!)

## Scripts

### Dues and A/R Notifications: `slack_balances.py`
When supplied a mapping of slack UID to amount owed and access to the Gmail connected to the receiver's (VPF) venmo account, this script will send out messaged like the following:

Time for Fall 2018 Dues! :flying_money_with_wings: You currently owe *$290.00*-- please venmo :venmo: @gtakpsi, pay via check, or pay on chapterspot.com (+3% transaction fee). Due August 30!
> Note: If you venmo, you should receive a confirmation message within 30 (or so) minutes! If you think there is an error, please slack @vishwa. If you would like a payment plan, please fill out this form: https://goo.gl/forms/loremipsum

## Externally Triggered Messages

### Venmo Payments
When a Venmo Payment is made to the account (not fulfillment of a request, but just a payment) the listener on the inbox will trigger an confirmation message to the mapped slack UID based on the payer's name listed on Venmo. A mapping of name to slack UID must be supplied. The message includes the email ID from gmail for debugging purposes and in the case of repeats; currently, whenever an email fitting the criteria is found, a new label is applied and its removed from the inbox. Sample message:

Received a Venmo payment of $290.00. (ID: 1655ab6514eea8da)

### [TODO] for new applications for special projects funding

### [TODO] @vpf dues
Responds in DM with how much your current A/R is based on chapterspot (feasible?)

### [TODO] @vpf budget
Returns a link to the current budget

### [TODO] @vpf venmo request @handle
Adds row to venmo request sheet with handle and name