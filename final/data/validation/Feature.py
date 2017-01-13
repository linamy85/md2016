import pymysql
import sklearn

"""
Example usage:
    
from Feature import Feature
f = Feature()

X, Y = f.getYearFeatures(2015)

###      Meaning of X and Y     ###
# for i in len(world's country pairs):
#   X[i] = features of the pair
#   Y[i] = immegrants from pair_x to pair_y
"""


class Feature:
    def __init__(self, country_threshold=1000):
        self.db = pymysql.connect("localhost", "root", "fighting", "md")
        self.cursor = self.db.cursor()

        countries = self.getColumnCount('country', ['node', 'hua'])
        countries = { 
            k: v for k, v in countries.iteritems() if v > country_threshold
        }
        print "Found", len(countries), "country."
        print countries.items()[:5]

        self.country_index = self.toIndex(countries)
        print "Done indexing all countries"

        self.node_index = self.toIndex(self.getColumnCount('tag', ['node', 'hua']))
        self.link_index = self.toIndex(self.getColumnCount('tag', ['link']))

        print "Found", len(self.node_index), "nodes: ", self.node_index.items()[0]
        print "Found", len(self.link_index), "links: ", self.link_index.items()[0]


    # Country (source, target) pair to feature
    def getYearFeatures(self, year):
        # Gets all validation data.
        validation = self.getValidation(year)

        # Gets all features for countries in given year
        allnodes = dict()
        for country, idx in self.country_index.items():
            allnodes[country] = self.getNodeFeature(country, year)
            print country, "feature done."
        
        print "Dictioned countries features."
        
        X = []
        Y = []
        for src, idx_src in self.country_index.items():
            tar_features = self.getLinkSrcFeature(src, year)

            for tar, idx_tar in self.country_index.items():
                if (src, tar) in validation:
                    X.append(
                        self.indexPairFeature(src, tar, tar_features[tar], allnodes)
                    )
                    Y.append(validation[(src, tar)])
            print "source #", idx_src, src, "done." 

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
    def getNodeFeature(self, country, year):
        ans = [0 for i in range(len(self.node_index))]
        
        for table in ['node', 'hua']:
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

        sql = "SELECT country2, value, tag FROM link " \
              "WHERE country1='%s' AND (year=0 OR year=%d);" % (src, year)
        self.cursor.execute(sql)
        for tar, val, tag in self.cursor.fetchall():
            if tar in self.country_index:
                ans[tar].append((val, tag))

        return ans

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


    # Indexes all keys in countdict.
    def toIndex(self, countdict):
        index = 0
        ans = dict()
        for key in countdict.iterkeys():
            ans[key] = index
            index += 1
        return ans


    # Indexes all features of given pair (src, tar).
    def indexPairFeature(self, src, tar, srctarfs, allnodes):
        # part 1: source country
        # part 2: target country
        # part 3: pair relationship
        ans = []
        
        ans += allnodes[src]
        ans += allnodes[tar]
        
        link_f = [0 for x in range(len(self.link_index))]
        
        for val, tag in srctarfs:
            link_f[self.link_index[tag]] = float(val)
        
        ans += link_f
        
        return ans





