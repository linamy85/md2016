import pandas as pd
import connect
import pycountry
import os

MATCH_FILE = "migration_country.match"

countries = {}

if __name__ == '__main__':
    origin = []
    con = connect.connector()
    data = pd.read_excel('./UN_MigrantStockByOriginAndDestination_2015.xlsx')
    for index, row in data.iterrows():
        if index < 13:
            continue
        if index == 13: # Country origin list
            origin = row

            if os.path.isfile(MATCH_FILE):
                with open(MATCH_FILE, "r") as file:
                    line = file.readline()
                    while line:
                        code = line.split()[0]
                        country = line[len(code)+1:]
                        countries[country] = code
                        line = file.readline()

            else: # If matching file not exists.
                for country in pycountry.countries:
                    countries[country.name] = country.alpha_3
                    for country in row[5:]:
                        if country not in countries:
                            code = raw_input(
                                "ISO 3code for country %s: (empty for not using)" 
                                % country
                            )
                            countries[country] = code

                # Write code
                with open(MATCH_FILE, "w") as file:
                    for country, code in countries.items():
                        file.write("%s %s\n" % (code, country))
                print "Write country matching file done."
            continue

        country = row[1]
        if (country in countries and countries[country] == "") or (raw_input("Record country %s?" % country) != ""):
            continue
        if country not in countries:
            countries[country] = raw_input("ISO 3code for '%s':" % country)

        # Inserts data.
        for idx in range(5, len(row)):
            con.execute(
                "INSERT INTO valid (source, target, year, value) " 
                "VALUES ('%s', '%s', 2015, %d);"
                % (origin[idx], country,  row[idx]))

