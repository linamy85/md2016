
from __future__ import print_function

from Feature import Feature
import sys
import math
import argparse

def evaluate(ans, res):
    total = 0.0
    for i in range(len(ans)):
        total += math.fabs(ans[i] - res[i])
    return total

def baseline(feature, year):
    N_country = len(feature.country_index)

    source = [0 for i in range(N_country)] 
    target = [0 for i in range(N_country)] 

    sql = "SELECT source, sum(value) FROM migration "\
            "WHERE year = %d GROUP BY source;" % args.year
    feature.cursor.execute(sql)
    for country, val in feature.cursor.fetchall():
        if country in feature.country_index:
            print ("#", feature.country_index[country], country, val)
            source[feature.country_index[country]] = float(val)

    sql = "SELECT target, sum(value) FROM migration "\
            "WHERE year = %d GROUP BY target;" % args.year
    feature.cursor.execute(sql)
    for country, val in feature.cursor.fetchall():
        if country in feature.country_index:
            print ("#", feature.country_index[country], country, val)
            target[feature.country_index[country]] = float(val)

    ans = [0 for i in range(N_country * N_country)]

    SRC_SUM = 0
    for val in source:
        SRC_SUM += val

    # Calculating migrants from proportion.
    idx = 0
    for i in range(N_country): # target[i]
        SUM = SRC_SUM - source[i]
        for j in range(N_country): # source[j]
            if i == j:
                idx += 1
                continue
            ans[idx] = target[i] * (source[j] / SUM)
            idx += 1

    return ans


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Baseline method for MD final project.'
    )
    parser.add_argument('--year', '-y', help='Year to test',
                        dest='year', type=int, required=True)
    parser.add_argument('--node-threshold', '-n', help='Node features # threshold',
                        dest='node_threshold', type=int, default=150)
    parser.add_argument('--migration-threshold', '-m',
                        help='Migrants non-zero # threshold',
                        dest='migrat_threshold', type=int, default=40)

    args = parser.parse_args(sys.argv[1:])

    feature = Feature(args.node_threshold, args.migrat_threshold)

    ans = baseline(feature, args.year)

    # Getting real answer.
    real = feature.getValidation(args.year)
    real_ans = []
    for tar, iy in feature.country_index.items():
        for src, ix in feature.country_index.items():
            real_ans.append(real[(src, tar)])


    error = evaluate(real_ans, ans)
    print ("Baseline error:", error)
    print ("Ans: ", real_ans[:N_country])
    print ("Base:", ans[:N_country])



