import pandas as pd
import connect

con = connect.connector()
######## Language distance ##########
# data = pd.io.stata.read_stata('./ling_web.dta')
# for index, row in data.iterrows():
    # con.execute("INSERT INTO link (tag, country1, country2, category, value, property) VALUES ('language', '%s', '%s', 'culture', '%f', 'float');" % (row['iso_o'], row['iso_d'], row['cle']))

####### Geometric distance ##########
# data = pd.io.stata.read_stata('./dist_cepii.dta')
# for index, row in data.iterrows():
    # con.execute("INSERT INTO link (tag, country1, country2, category, value, property) VALUES ('distance', '%s', '%s', 'geography', '%f', 'float');" % (row['iso_o'], row['iso_d'], row['dist']))

############# Climate ###############
# data = pd.read_csv('./climate.csv')
# for index, row in data.iterrows():
    # c = row['country']
    # con.execute("INSERT INTO node (tag, country, category, value, property) VALUES ('July temperature', '%s', 'climate', '%f', 'float'), ('Jan temperature', '%s', 'climate', '%f', 'float'), ('avg temperature', '%s', 'climate', '%f', 'float'), ('precipitation', '%s', 'climate', '%f', 'float');" % (c, row['July_temp'], c, row['Jan_temp'], c, row['avg_temp'], c, row['avg_water']))

############# Religion ##############
# data = pd.read_csv('./UNdata_Export_20161211_103941682.csv')
# count = dict()
# country_total = dict()

# for index, row in data.iterrows():
    # country = row['Country or Area'].translate(None, '\'()')
    # if country not in country_total:
        # count[country] = dict()
        # country_total[country] = 0
    
    # religion = row['Religion'].translate(None, '\'()')
    # if religion == 'Total':
        # continue

    # value = row['Value']
    # country_total[country] += value
    # if religion in count[country]:
        # count[country][religion] += value
    # else:
        # count[country][religion] = value
    # if index == 17430:
        # break
       
# for country, sum in count.items():
    # con.execute(
        # "INSERT INTO node "
        # "(tag, country, category, value, property) "
        # "VALUES %s;" % (
            # ", ".join(map(lambda x: 
                # "('religion - %s', '%s', 'culture', '%f', 'float')" 
                # % (x[0], country, x[1] / country_total[country])
                # , sum.items()))
        # )
    # )


print "Done."
