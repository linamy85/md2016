# This file is the module for all potential functions.
# Author: Amy Lin

HASH_N = 1000000

from utils import *

class Potential:
    def __init__ (self, directory):
        # Reads file.
        self.userN = read_user_file(directory)
        print(directory, " #user = ", self.userN)  # test

        self.friends = read_relation_file(directory, self.userN)
        print(directory, " friends of user #3995", self.friends[3995])  # test

        self.owned, self.messages, self.category = read_message_file(
            directory, self.userN)
        print(directory, " meta of item #104", self.messages[104])  # test

    # @param y :: (user, item)
    def fp (self, y):
        pop = 0
        for c in self.messages[y[1]][1]:
            print( y[1], "in cate ", c, " => ", self.category[c][0])
            pop += self.category[c][0]
        return (
            len(self.friends[y[0]]),                # user friendship
            int(y[0] in self.messages[y[1]][0]),    # item ownership
            pop                                     # category popularity
        )

    def gp (self, y1, y2):
        same_user = (y1[0] == y2[0])
        y1_own = y1[0] in self.messages[y1[1]][0]
        y2_own = y2[0] in self.messages[y2[1]][0]

        # owner identification
        oi = same_user and y1_own and y2_own

        # friend identification
        fi = same_user and bool(
            (self.messages[y1[1]][0] & self.messages[y2[1]][0]) & \
            (self.friends[y1[0]])
        )

        # owner friend
        of = (y1[1] == y2[1]) and ((
                y1_own and (y2[0] in self.friends[y1[0]])   # u(y2) is friend
            ) or (
                y2_own and (y1[0] in self.friends[y2[0]])   # u(y1) is friend
            ))
        
        # Co - category
        cc = same_user and (y1_own or y2_own) and \
                bool(  # same cate
                    self.messages[y1[1]][1] & self.messages[y2[1]][1]
                ) 
        if oi or fi or of or cc:
            return (oi, fi, of, cc)
        return None

    # @param famousN : to take pre-Nth active user in the network
    # @param mult    : take pre-(N * link)th active user in following case:
    #                   1. item's owner & friend
    #                   2. item's category's owner
    def baseline_layer2(self, famousN=20, mult=20):
        ans = []
        
        sort_key = (lambda u: len(self.friends[u]) + len(self.owned[u]))

        # for all user ranking.
        # sort by #friend + #own_items
        ranking = sorted(
            list(range(self.userN)),
            key=sort_key,
            reverse=True
        )
        
        for item in range(len(self.messages)):
            get = self.messages[item][2] * mult
            
            if get == 0:
                ans.append(frozenset())
                continue

            users = frozenset(ranking[:famousN])

            us = self.messages[item][0]
            for u in self.messages[item][0]:
                us = us | self.friends[u]
            users = users | frozenset(
                sorted(list(us), key=sort_key, reverse=True)[:get]
            )
            
            us = set()
            for c in self.messages[item][1]:
                us = us | self.category[c][1]
            users = users | frozenset(
                sorted(list(us), key=sort_key, reverse=True)[:get]
            )
           
            ans.append(users)
            if item % 1000 == 0:
                print("Baseline: ", 100 * item / len(self.messages))
                
        return ans
    
    def layer2(self):
        ans = []
        for item in range(len(self.messages)):
            ans.append(set())

            for u in self.messages[item][0]:
                ans[item] = ans[item] | self.friends[u]
            
            for c in self.messages[item][1]:
                ans[item] = ans[item] | self.category[c][1]
        return ans


    # nodes: list(set) :: nodes[item_id] = set(users to make node y)
    # links: dict(g)   :: links[(hash_y1, hash_y2)] = 8*g3 + 4*g2 + 2*g1 + 1*g0
    def layer2_node_link(self, famousN=20, mult=20):
        nodes = self.baseline_layer2(famousN, mult)

        ans = dict()
        for user in range(self.userN):

            # owner identification
            for i1 in self.owned[user]:
                # (user, i1) not node.
                if user not in nodes[i1]:
                    continue
                hash1 = user * HASH_N + i1

                for i2 in self.owned[user]:
                    # (user, i2) not node.
                    if user not in nodes[i2]:
                        continue
                    hash2 = user * HASH_N + i2

                    pair = (hash1, hash2) if (hash1 < hash2) else (hash2, hash1)
                    if (i1 != i2) and (pair not in ans):
                        g = self.gp((user, i1), (user, i2))
                        if not g[0]:
                            print("Error: owner identification")
                            return None
                        ans[pair] = 8*g[3] + 4*g[2] + 2*g[1] + g[0]
            
            # friend identification
            for friend in self.friends[user]:
                for i1 in self.owned[friend]:
                    # (user, i1) not node.
                    if user not in nodes[i1]:
                        continue
                    hash1 = user * HASH_N + i1

                    for i2 in self.owned[friend]:
                        # (user, i2) not node.
                        if user not in nodes[i2]:
                            continue
                        hash2 = user * HASH_N + i2

                        pair = (hash1, hash2) if (hash1 < hash2) else (hash2, hash1)
                        if (i1 != i2) and (pair not in ans):
                            g = self.gp((user, i1), (user, i2))
                            ans[pair] = 8*g[3] + 4*g[2] + 2*g[1] + g[0]
            
            # CO-category
            for item in self.owned[user]:
                if user not in nodes[item]:
                    continue
                hash1 = user * HASH_N + item

                for cate in self.messages[item][1]:
                    for co in self.category[cate][2]:
                        if user not in nodes[co]:
                            continue
                        hash2 = user * HASH_N + co

                        pair = (hash1, hash2) if (hash1 < hash2) else (hash2, hash1)
                        if (co != item) and (pair not in ans):
                            g = self.gp((user, item), (user, co))
                            ans[pair] = 8*g[3] + 4*g[2] + 2*g[1] + g[0]
                            
            if not (user % 1000):
                print((75 * user / self.userN), "% completed.")

        # Owner friendship
        itemN = len(self.messages)
        for item in range(itemN):
            for user in self.messages[item][0]:
                if user not in nodes[item]:
                    continue
                hash1 = user * HASH_N + item

                for friend in self.friends[user]:
                    if friend not in nodes[item]:
                        continue
                    hash2 = friend * HASH_N + item

                    pair = (hash1, hash2) if (hash1 < hash2) else (hash2, hash1)
                    if (pair not in ans):
                        g = self.gp((user, item), (friend, item))
                        ans[pair] = 8*g[3] + 4*g[2] + 2*g[1] + g[0]
            if not (item % 1000):
                print((75 + 25 * item / itemN), "% completed.")

        print("100% completed.")

        return nodes, ans
