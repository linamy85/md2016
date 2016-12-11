with open("cv/test.txt", "r+") as f:
    testline = f.readlines()
    f.seek(0, 0)
    f.truncate()
    for i in range(len(testline)):
        tmp = testline[i].split(" ")
        user, item = int(tmp[0]), int(tmp[1])
        f.write(tmp[0]+" "+tmp[1]+" "+str("hi")+"\n")
