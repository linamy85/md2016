import math
import pandas as pd
import connect
import pycountry
import os

MATCH_FILE = "migration_country.match"

countries = {}

if __name__ == '__main__':
    origin = []
    con = connect.connector()
    data = pd.read_excel(
        './UN_MigrantStockByOriginAndDestination_2015.xlsx', "Table 16")
    for index, row in data.iterrows():
        if index < 13:
            continue
        if index == 13: # Country origin list
            print "Get to country origin row."
            origin = row

            if os.path.isfile(MATCH_FILE):
                with open(MATCH_FILE, "r") as file:
                    line = file.readline().decode('utf8')
                    while line:
                        code = ""
                        if line[0] != ' ':  # Not empty country code.
                            code = line.split()[0] 
                        country = line[len(code)+1:-1]
                        countries[country] = code
                        line = file.readline().decode('utf8')

            else: # If matching file not exists.
                # Gets data from pycountry codule
                for country in pycountry.countries:
                    countries[country.name] = country.alpha_3
                # Gets data from user input
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
                        file.write(("%s %s\n" % (code, country)).encode('utf8'))
                print "Write country matching file done."

            # Transfers origin country to country code.
            # print countries.items()[:10]
            for idx in range(len(origin)):
                if pd.isnull(origin[idx]):
                    continue
                origin[idx] = countries[origin[idx]]
            continue

        country = row[1]
        if country in countries:
            if countries[country] == "":
                continue
        elif raw_input("Record country %s?" % country) != "":
            continue

        if country not in countries:
            countries[country] = raw_input("ISO 3code for '%s':" % country)

        # Inserts data.
        for idx in range(5, len(row)):
            if origin[idx] == "":
                continue
            val = row[idx]
            if math.isnan(val):
                val = 0
            try:
                con.execute(
                    "INSERT INTO migration (source, target, year, value) " 
                    "VALUES ('%s', '%s', 2015, %d);"
                    % (origin[idx], countries[country],  int(val))
                )
            except Exception as e:
                print "(%s => %s) @ year 2015 has existed." % (
                    origin[idx], countries[country])
                print e
