
import connect

countries = {}

with open("country.match", "r") as file:
  line = file.readline()
  while line:
    countries[ line[4:-1] ] = line[:3]
    line = file.readline()

con = connect.connector()

# Updates country code in database
for name in countries:
  print con.execute(
    "UPDATE node SET node.country=\"" + countries[name] + "\" " +
    "WHERE node.country=\"" + name + "\" AND category = \"culture\";"
  )

