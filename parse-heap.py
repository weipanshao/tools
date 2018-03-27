#$language = "Python"
#$interface = "1.0"

import inspect
import sys, os, re, time
debug_file="D://debug.log"
output = "output9.csv"

class CAllocPoint(object):

    __instance = dict()

    def __new__(cls, *args, **kwd):
        if not args[0] in cls.__instance.keys():
            cls.__instance[args[0]] = object.__new__(cls, *args, **kwd)
        return cls.__instance[args[0]]

    def __init__(self, addr):
        if not hasattr(self, "records"):
            self.records = dict()
        return

    def addRecord(self, size):
        if not size in self.records:
            self.records[size] = 0
        self.records[size] = self.records[size]+1

    def totalSize(self):
        s = 0
        for size in self.records:
            s = s + size * self.records[size]
        return s

    def totalCount(self):
        c = 0
        for size in self.records:
            c = c + self.records[size]
        return c

    def maxSize(self):
        return max(self.records.keys())

    def maxSizeCount(self):
        return self.records[self.maxSize()]

    @staticmethod
    def compareKey(a, b):
        inst1 = CAllocPoint.__instance[a]
        inst2 = CAllocPoint.__instance[b]
        return inst1.totalSize() - inst2.totalSize()

    @staticmethod
    def descSort():
        l = list(CAllocPoint.__instance)
        l.sort(CAllocPoint.compareKey, None, True)
        return l

    @staticmethod
    def printStatistic():
        l = CAllocPoint.descSort()
        fd = open(output, "w+")
        fd.write("address,total size,alloc count,max size,count of max size,\n")
        for addr in l:
            inst = CAllocPoint.__instance[addr]
            fd.write("0x%08x,%d,%d,%d,%d,\n"%(addr, inst.totalSize(), inst.totalCount(), inst.maxSize(), inst.maxSizeCount()))
        fd.close()

class Debugger():
    @staticmethod
    def output(s):
        frame = inspect.currentframe()
        
        fd = open(debug_file, "a+")
        info = inspect.getframeinfo(frame.f_back) #filename, lineno, function, code_context, index
        timestr = str(time.time())#time.strftime("%Y-%m-%d %H:%M:%S")
        fd.write("[%s][Line %d]"%(timestr, frame.f_back.f_lineno) + str(s) + "\n")
        fd.close()
        

        
Debugger.output("===============Start==============") 
Debugger.output("os.getcwd=%s"%os.getcwd())
Debugger.output("Date=%s"%time.strftime("%Y-%m-%d %H:%M:%S"))

fd = open(sys.argv[1], "r")

info = fd.read()

fd.close()

#fout = open("test-out.txt", "w")
#fout.write(info)
#fout.close()

dozen = re.findall(r'0x[0-9a-f]{8}'+'\('+'[0-9]{2,4}'+'\)'+'   alloc at 0x[0-9a-f]{8}', info)
#dozen = re.findall(r"0x[a-f0-9]{8}: size (\d+)\s+ alloc at 0x([a-f0-9]{8})", info)
#print info
#print dozen

for t in dozen:
    #print t
    addr = int(t.split("x")[2], 16)
    size = int(t.split(")")[0].split("(")[1])
    #print size,addr
    CAllocPoint(addr).addRecord(size)

CAllocPoint.printStatistic()

Debugger.output("===============End==============\n\n")   

