#!/usr/bin/env python3
import datetime as dt
import numpy as np
import pandas as pd
import requests
from lxml import etree
import pickle

# The data from the Treasury website is more up-to-date, but the data from FRED
# goes back further.

yc_url = 'http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData'

yc_request = requests.get(yc_url).content

yc_xml_raw = etree.XML(yc_request)

entries = yc_xml_raw.getchildren()

# Strip out entries with no children - these do not have useful data:
entries = [x for x in entries if x.getchildren() != []]

subentries = [x.getchildren()[-1].getchildren()[0].getchildren()
              for x in entries]

# Initialize dictionary:
yields = {'Date': [],
          "1month": [], "2month": [], "3month": [], "6month": [],
          "1year": [], "2year": [], "3year": [], "5year": [],
          "7year": [], "10year": [], "20year": [], "30year": []}

# Exploit the structure for these subentries to get yield values and dates:
for x in subentries:
    yields['Date'].append(x[1].text)
    yields['1month'].append(x[2].text)
    yields['2month'].append(x[3].text)
    yields['3month'].append(x[4].text)
    yields['6month'].append(x[5].text)
    yields['1year'].append(x[6].text)
    yields['2year'].append(x[7].text)
    yields['3year'].append(x[8].text)
    yields['5year'].append(x[9].text)
    yields['7year'].append(x[10].text)
    yields['10year'].append(x[11].text)
    yields['20year'].append(x[12].text)
    yields['30year'].append(x[13].text)

# Turn dates into datetime objects:
yields['Date'] = [dt.date(int(x[:10].split('-')[0]),
                          int(x[:10].split('-')[1]),
                          int(x[:10].split('-')[2])) for x in yields['Date']]

# Turn 'None' strings into null values and numbers into floats:
for key in yields.keys():
    if key != 'Date':
        yields[key] = np.array(yields[key], dtype='float')

df = pd.DataFrame(yields)

df.index = df.Date
# df = df.drop(columns=['Date'])
df = df.drop(axis=1, labels=['Date'])
df = df.sort_index()

with open('yc.pickle', 'wb') as f:
    pickle.dump(df, f)
