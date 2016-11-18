# This file does things important but not so important.
# eg. read files...
# Author: Amy Lin

import os
import sys

# Returns number of users.
def read_user_file (dir):
    userN = 0
    user_file = os.path.join(dir, "user.txt")
    with open(user_file, 'r') as file:
        line = file.readline()
        while line:
            userN = int(line)
            line = file.readline()
    return userN + 1

# Returns list of user's friends (set). => [set(friend)]
def read_relation_file (dir, userN):
    list = []
    for u in range(userN):
        list.append(set())

    relation_file = os.path.join(dir, "relation.txt")
    with open(relation_file, 'r') as file:
        line = file.readline()
        while line:
            fr, to = map(int, line.split())
            list[fr].add(to)
            # list[to].add(fr)
            line = file.readline()

    return list

# Returns 2 things:
# 1. [set(owner), set(cate), link] of item
# 2. [#item, set(owner)] of category :: number of items in the category.
def read_message_file (dir, userN):
    messages = []
    category = []
    owned = []
    for u in range(userN):
        owned.append(set())

    max_item = 0
    max_cate = 0 

    # read the max of msg & category to create list instead of dictionary.
    # (since dictionary will be access pretty much times, and hash > index)
    message_file = os.path.join(dir, "message.txt")
    with open(message_file, 'r') as file:
        line = file.readline()
        while line:
            user, item, cate, link = map(int, line.split())
            max_item = max(max_item, item)
            max_cate = max(max_cate, cate)
            line = file.readline()

        # Done getting max number
        file.seek(0)

        for i in range(max_item + 1):
            messages.append([set(), set(), link])

        for c in range(max_cate + 1):
            category.append([0, set(), set()])

        print("Max item = ", max_item, " ; Max category = ", max_cate)
        sys.stdout.flush()
            
        count = 0
        line = file.readline()
        print(">>> ", line)
        while line:
            if not (count % 10000):
                print("Message.txt ... ", line)
            user, item, cate, link = map(int, line.split())
            owned[user].add(item)

            messages[item][0].add(user)
            messages[item][1].add(cate)
            messages[item][2] = link

            category[cate][0] += 1
            category[cate][1].add(user)
            category[cate][2].add(item)
            line = file.readline()
            count += 1

    return owned, messages, category 

# return hashed_y
def hash_y(uID, rmax, rID):            
	return (uID * rmax + rID)

# return (uID, rID)
def hash_y_inv(rmax, hash_y):
	return (hash_y / rmax, hash_y % rmax)
        

