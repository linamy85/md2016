import connect
import pycountry

countries = {}
for country in pycountry.countries:
    countries[country.name] = country.alpha_3

    # codes = [countries.get(country, 'Unknown code') for country in input_countries]
con = connect.connector()

list = con.execute("SELECT country FROM node WHERE category = \"culture\" GROUP BY country;")

for country in list:
    if country[0] in countries:
        code = countries[country[0]]
        print country[0], " --- ", code
    else:
        code = raw_input(">> Alpha3 for "+country[0]+" is: ")
        print country[0], " --- ", code
        countries[country[0]] = code

with open("country.match", "w") as file:
    for country in list:
        file.write("%s %s\n" % (countries[country[0]], country[0]))
