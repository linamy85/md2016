# This file is the module for all potential functions.
# Author: Amy Lin

from utils import *

class Potential:
    def __init__ (self, directory):
        # Reads file.
        userN = read_user_file(directory)
        print directory, " #user = ", userN  # test

        self.friends = read_relation_file(directory, userN)
        print directory, " friends of user #3995", self.friends[3995]  # test

        self.messages, self.category = read_message_file(directory)
        print directory, " meta of item #104", self.messages[104]  # test

    # @param y :: (user, item)
    def fp (self, y):
        pop = 0
        for c in self.messages[y[1]][1]:
            print y[1], "in cate ", c, " => ", self.category[c][0]
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
        oi = int(same_user and y1_own and y2_own)

        # friend identification
        fi = int(
            same_user and \
            bool((self.messages[y1[1]][0] & self.messages[y2[1]][0]) & \
             (self.friends[y1[0]]))
        )

        # owner friend
        of = int(
            (y1[1] == y2[1]) and ((
                y1_own and (y2[0] in self.friends[y1[0]])   # u(y2) is friend
            ) or (
                y2_own and (y1[0] in self.friends[y2[0]])   # u(y1) is friend
            ))
        )
        
        # Co - category
        cc = int(
            same_user and (y1_own or y2_own) and \
            bool(self.messages[y1[1]][1] & self.messages[y2[1]][1]) # same cate
        )
        
        return (oi, fi, of, cc)

    
    def layer2(self):
        ans = []
        for item in range(len(self.messages)):
            ans.append(set())

            for u in self.messages[item][0]:
                ans[item] = ans[item] | self.friends[u]
            
            for c in self.messages[item][1]:
                ans[item] = ans[item] | self.category[c][1]
        return ans




