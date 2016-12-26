import pandas as pd
import connect

import wbdata
import datetime

# Connect to database
con = connect.connector()

# Get countries, indicators
countries = wbdata.get_country(display=False)
indicators = wbdata.get_indicator(display=False)

# Collect CountryID
countryID = []
for i in range(len(countries)):
    countryID.append(countries[i]['id'])

# Collect indicatorID
indicatorID = []
for i in range(1000, len(indicators)):
    indicatorID.append(indicators[i]['id'])

# Make indDict for fetching data
indDict = dict()
for indStr in indicatorID:
    indDict[indStr] = indStr.replace('.','_')

# fetch data
data_date = (datetime.datetime(2005, 1, 1), datetime.datetime(2016, 1, 1))
for countryStr in countryID:
    for key, value in indDict.items():
        d = dict()
        d[key] = value
        try:
            df = wbdata.get_dataframe(d, country=countryStr, data_date=data_date, convert_date=True)
            df = df.dropna()
        #except (TypeError, ValueError):
        except:
            #print('failed and continue')
            continue
        
        try:
            dfname="df."+str(value)
            countryStr_tmp = "'"+countryStr+"'";
            valueStr_tmp = "'"+str(value).replace('_', '.')+"'";
            code = '''for i in range(len('''+dfname+''')): y=int(str(df.index[i])[:4]); v='''+dfname+'''[i]; con.execute("INSERT INTO hua (tag, year, country, category, value, property) VALUES ('''+valueStr_tmp+''', '%d', '''+countryStr_tmp+''', 'CATEGORY', '%f', 'float');" % (y, v)); print('''+valueStr_tmp+''', y, '''+countryStr_tmp+''')'''
                        
            #code = "for i in range(len("+dfname+")): y=str(df.index[i])[:4]; v="+dfname+"[i]; con.execute('INSERT INTO hua (tag, year, country, category, value, property) VALUES ('TAGGY', '%d', '%s', '%s', '%f', 'float');' % (y,"+countryStr+", "+str(value)+", v))"
            exec(code)
            #for i in range(len(df.IC_BUS_EASE_XQ)):
                #con.execute("INSERT INTO hua (tag, year, country, category, value, property) VALUES ('TAGGY', '%d', '%s', '%s', '%f', 'float');" % (y, countryStr, str(value), v))
        #except (AttributeError, IndexError):
        except:
            pass
        
print("Done.")
