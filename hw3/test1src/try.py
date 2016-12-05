from threading import Thread

class Hello:
    def __init__ (self):
        self.r = [1,2,3]

    def run (self, ty, p):
        for i in self.r:
            print i
        for i in ty:
            print i
        print p

    def hi (self):
        ty = [5,6,7]

        thr = Thread(target = self.run, args = (ty, 12, ))
        print "Start now."
        thr.start()
        thr.join()


hello = Hello()
hello.hi()
