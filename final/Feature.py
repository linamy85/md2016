from __future__ import print_function

import pymysql
import sklearn

"""
Example usage 1:
    
from Feature import Feature

###     Parameters to adjust    ###
# node_threshold :: limit the lower bound of node features
# migration_threshold :: limit the lower bound of number of migration(in+out),
#       For each country, if migration to another country A > 0, then add 1.
#       If migration from another country B > 0, then add 1 too.
#       And the total count of a country should > migration_threshold.

f = Feature(node_threshold=180, migration_threshold=50)

X, Y, _, __ = f.getYearFeatures(2015)  # The last two objects returned is useless.

###      Meaning of X and Y     ###
# for i in len(world's country pairs):
#   # let index i ==> (x -> y)
#   X[i] = [[features(x)], [features(y)], [features(x->y)]]
#   Y[i] = immegrants from pair_x to pair_y
"""

"""
Example usage 2:

from Feature import Feature

###     Parameters to adjust    ###
# node_threshold, migration_threshold :: same as `Example usage 1`.
# set_unknown :: split features array & values from original answer X & Y.

f = Feature(node_threshold=180, migration_threshold=50, set_unknown='USA,POL')

# X & UX has same format as `Example usage 1`, so do Y & UY.
X, Y, UX, UY = f.getYearFeatures(2015)
"""

NODE_TABLE = ['node', 'hua']
LINK_TABLE = ['link', 'trade']

class Feature:
    def __init__(self, node_threshold=150, migration_threshold=40,
                 set_unknown=''):
        self.db = pymysql.connect("localhost", "root", "fighting", "md")
        self.cursor = self.db.cursor()
        
        # Sets unknown country list.
        unknowns_list = set_unknown.split(',')

        # Randomly take 2015 for filtering.
        countries = self.filterCountry(2010, node_threshold, migration_threshold)
        print ("Found", len(countries), "/", 
               self.getColumnNumber("country", NODE_TABLE), "country left.")
        print (list(countries.items())[:5])

        self.country_index = self.toIndex(countries)
        print ("Done indexing all countries")

        self.unknowns = dict()
        for country in unknowns_list:
            if country in self.country_index:
                self.unknowns[country] = self.country_index[country]
            else:
                print ("Didn't find country:", country, ", kick out of unknowns.")
        
        print ("Final unknowns:", self.unknowns)

        self.node_index = self.toIndex(self.getColumnCount('tag', NODE_TABLE))
        self.link_index = self.toIndex(self.getColumnCount('tag', LINK_TABLE))

        print ("Found", len(self.node_index), "nodes: ", list(self.node_index.items())[0])
        print ("Found", len(self.link_index), "links: ", list(self.link_index.items())[0])


    # Country (source, target) pair to feature
    def getYearFeatures(self, year):
        # Gets all validation data.
        validation = self.getValidation(year)
        node_avg = self.getFeatureAvg(year, self.node_index, NODE_TABLE)
        link_avg = self.getFeatureAvg(year, self.link_index, LINK_TABLE)
        print ("Get node & link features average done.")
        print (node_avg[:5])

        # Gets all features for countries in given year
        allnodes = dict()
        for country, idx in self.country_index.items():
            allnodes[country] = self.getNodeFeature(country, year, node_avg)
            print ("#", idx, "-", country, ".", end="\t")
        
        print ("\nDictioned countries features.")
        
        X = []
        Y = []
        UX = []
        UY = []
        for src, idx_src in self.country_index.items():
            tar_features = self.getLinkSrcFeature(src, year)

            for tar, idx_tar in self.country_index.items():
                if (src, tar) in validation:
                    X.append(
                        self.indexPairFeature(
                            src, tar, tar_features[tar], allnodes, link_avg)
                    )
                    Y.append(validation[(src, tar)])
            # print ("source #", idx_src, src, "done.")
        print ("All pairs indexing done.")

        if standard:
            self.standardizeX(X)

        return X, Y


    # Retrieves validation data
    def getValidation(self, year):
        ans = dict()
        sql = "SELECT source, target, value from migration WHERE year = %d" % year
        self.cursor.execute(sql)
        #print list(cursor.fetchall())[:5]
        for t in self.cursor.fetchall():
            ans[(t[0], t[1])] = t[2]
        return ans


    # Retrieves features of given country, which is indexed.
    def getNodeFeature(self, country, year, node_avg):
        ans = node_avg[:]
        
        for table in NODE_TABLE:
            sql = "SELECT value, tag FROM %s "\
                  "WHERE country='%s' AND ( year=0 OR year=%d );"\
                    % (table, country, year)
            self.cursor.execute(sql)
            for val, tag in self.cursor.fetchall():
                ans[self.node_index[tag]] = float(val)
        return ans


    # Gets all links feature for the source
    def getLinkSrcFeature(self, src, year):
        ans = dict([(c, []) for c in self.country_index.keys()])

        for table in LINK_TABLE:
            sql = "SELECT country2, value, tag FROM %s " \
                  "WHERE country1='%s' AND (year=0 OR year=%d);" \
                    % (table, src, year)
            self.cursor.execute(sql)
            for tar, val, tag in self.cursor.fetchall():
                if tar in self.country_index:
                    ans[tar].append((val, tag))

        return ans

    #####################################
    #           Basic methods           #
    #####################################

    # name      :: column name
    # tables    :: list of targets table
    def getColumnCount(self, name, tables):
        ans = dict()
        for table in tables:
            sql = "SELECT %s, COUNT(1) from %s GROUP BY %s;" % (name, table, name)
            self.cursor.execute(sql)
            for key, c in self.cursor.fetchall():
                ans.setdefault(key, 0)
                ans[key] += c
        return ans

    def getFeatureAvg(self, year, feature_index, tables):
        ans = [0 for i in range(len(feature_index))]

        for table in tables:
            sql = "SELECT tag, AVG(CAST(value AS DECIMAL(16,6))) FROM %s "\
                  "WHERE year = 0 OR year = %d GROUP BY tag;" % (table, year)
            self.cursor.execute(sql)
            all = self.cursor.fetchall()
            print ("Average in table", table, ":", all[:5])
            for tag, avg in all:
                if tag in feature_index:
                    ans[ feature_index[tag] ] = float(avg)
        return ans


    # Indexes all keys in countdict.
    def toIndex(self, countdict):
        index = 0
        ans = dict()
        for key in countdict.keys():
            ans[key] = index
            index += 1
        return ans

    def getColumnNumber(self, name, tables):
        ans = set()
        subsql = ["SELECT %s from %s" % (name, table) for table in tables]
        sql = "SELECT count(%s) from (%s) as a;" % (name, " union ".join(subsql))
        print (sql)
        self.cursor.execute(sql)
        return self.cursor.fetchall()[0][0]


    # Indexes all features of given pair (src, tar).
    def indexPairFeature(self, src, tar, srctarfs, allnodes, link_avg):
        # part 1: source country
        # part 2: target country
        # part 3: pair relationship
        ans = []
        
        ans.append(allnodes[src])
        ans.append(allnodes[tar])
        
        link_f = link_avg[:]
        
        for val, tag in srctarfs:
            link_f[self.link_index[tag]] = float(val)
        
        ans.append(link_f)
        
        return ans

    # Filters country by immegrants/emigrant number.
    def filterCountry(self, year, node_threshold, migration_threshold):
        ans = {}
        # Retrieves countries over node_threshold.
        subsql = []
        for table in NODE_TABLE:
            subsql.append("(SELECT country, count(1) as num FROM %s "\
                          "WHERE year = 0 OR year = %d GROUP BY country)"\
                          % (table, year))
        sql = "SELECT country FROM ( %s ) as a GROUP BY country "\
                "having sum(num) > %d;" \
                % (" union all ".join(subsql), node_threshold)
        print (sql)
        self.cursor.execute(sql)
        for country in self.cursor.fetchall():
            ans[country[0]] = 0
        print (ans)

        # Retrieves countries over migration number.
        for dir in ['source', 'target']:
            sql = "SELECT %s, count(*) as num from migration "\
                  "WHERE value > 0 and year = %d GROUP BY %s;" \
                  % (dir, year, dir)
            print (sql)
            self.cursor.execute(sql)
            for country, count in self.cursor.fetchall():
                if country in ans:
                    ans[country] += count
                # else:
                    # print ("'%s' with lots migration but less node data!", country)

        for country, count in list(ans.items()):
            if count < migration_threshold:
                print ("'%s' has bad migration: %d, kicked out!" % (country, count))
                ans.pop(country, None)
        return ans
