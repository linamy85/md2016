
# coding: utf-8

# In[ ]:

import pandas as pd

import wbdata
import datetime

import iso3166
import requests
from bs4 import BeautifulSoup

import sys
sys.path.append('../other/')

import connect

# In[63]:

### Connect to database
con = connect.connector()


# In[14]:

### Web scraper for collecting featured indicators
url = 'http://data.worldbank.org/indicator?tab=featured'
response = requests.get(url)
html = response.content
soup = BeautifulSoup(html, "lxml")


# In[61]:

### Collect indicatorID
indicatorID = []
all_links = soup.find_all("a")
for link in all_links:
    hrefURL = link.get("href")
    if hrefURL != None and hrefURL.find('/indicator') != -1 and hrefURL.find('?view=chart') != -1:
		if(hrefURL[11:][:-11] != 'SM.POP.NETM'):
					indicatorID.append(hrefURL[11:][:-11]
        
print(len(indicatorID))


# In[62]:

### Collect CountryID
countryDict = iso3166.countries_by_alpha3
countryID = [key for key, value in countryDict.items()]
print(len(countryID))


# In[ ]:

### Fetch data
data_date = (datetime.datetime(2005, 1, 1), datetime.datetime(2016, 1, 1))

## 1 country 1 indicator per fetching
## If we fetch multiple indicators at each time, 
## there may be errors and try&except may pass without storing any data

for countryStr in countryID:
    for key in indicatorID:
        value = key.replace('.','_')
        d = dict()
        d[key] = value
        try:
            df = wbdata.get_dataframe(d, country=countryStr, data_date=data_date, convert_date=True)
            df = df.dropna()
        except:
            continue
        
        try:
            dfname="df."+str(value)
            countryStr_tmp = "'"+countryStr+"'";
            valueStr_tmp = "'"+str(value).replace('_', '.')+"'";
            code = '''for i in range(len('''+dfname+''')): y=int(str(df.index[i])[:4]); v='''+dfname+'''[i]; con.execute("INSERT INTO hua (tag, year, country, category, value, property) VALUES ('''+valueStr_tmp+''', '%d', '''+countryStr_tmp+''', 'CATEGORY', '%f', 'float');" % (y, v)); print('''+valueStr_tmp+''', y, '''+countryStr_tmp+''')'''
                        
            exec(code)
            
        except:
            pass
        
print("Done.")

