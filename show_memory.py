#$language = "Python"
#$interface = "1.0"

import inspect
import os, re, time

connectString = None #"/telnet 90.0.0.101 23"
hostname = "Switch"
username = "admin"
password = "admin"

output="test.csv"

debug_file="D://debug.log"

crt.Screen.Synchronous = False
crt.Screen.IgnoreEscape = False

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
        

class CBdcomVty():
    def __init__(self, hostname = None, username = None, password = None, connenctString = None):
        self.hostname = "Switch"
        self.username = "admin"
        self.password = "admin"
        self.connString = "/serial com3"
        
        self.hostname = hostname
        self.username = username
        self.password = password
        self.connString = connenctString
        
        self.timeout = 30
        
    def sendCmd(self, cmd):
        if (cmd != "" and cmd[len(cmd)-1] == "\n"):
            cmd = cmd[0:len(cmd)-1]
        
        if cmd != "":
            crt.Screen.Send(cmd)
            crt.Screen.WaitForStrings(cmd, self.timeout)
            
        crt.Screen.Send("\n")
        crt.Screen.WaitForStrings("\n", self.timeout)
        
    def keepLogin(self, exitDiagnose = False):
        if not crt.Session.Connected:
            crt.Session.ConnectInTab(self.connString, False, True)
        
        origin_syn = crt.Screen.Synchronous
        crt.Screen.Synchronous = True
        self.sendCmd("\n")
        
        loginSuccess = False
        
        waitStrings = list()
        waitStrings.append("Username:")
        waitStrings.append("Password:")
        waitStrings.append(self.hostname + ">")
        waitStrings.append(self.hostname + "#")
        waitStrings.append(self.hostname + "_config")
        waitStrings.append(self.hostname + "(D)#")
        waitStrings.append(" --More-- ")
        
        while not loginSuccess:            
            r = crt.Screen.WaitForStrings(waitStrings, self.timeout)
            
            if r == 0:          # Timeout
                self.sendCmd("")
            elif r == 1:        # Username:
                self.sendCmd(self.username)
            elif r == 2:        # Password:
                crt.Screen.Send(self.password + "\n")
            elif r == 3:        # Switch>
                self.sendCmd("enable")
            elif r == 4:        # Switch#
                loginSuccess = True
            elif r == 5:        # Switch_config...
                self.sendCmd("exit")
                self.sendCmd("")
            elif r == 6:        # Switch(D)#
                if exitDiagnose:
                    self.sendCmd("no diag")
                else:
                    loginSuccess = True
            elif r == 7:        #   --More--
                crt.Screen.Send("q\n")
                
        crt.Screen.Synchronous = origin_syn
            
    def showToEnd(self, exitDiagnose = False):
        end = False

        waitStrings = list()
        waitStrings.append(" --More-- ")
        waitStrings.append(self.hostname + ">")
        waitStrings.append(self.hostname + "#")
        waitStrings.append(self.hostname + "_config")
        waitStrings.append(self.hostname + "(D)#")

        while not end:
            str = crt.Screen.ReadString(waitStrings, self.timeout)

            str_new = ""
            for i in range(0, len(str)):
                if str[i] != "\b":
                    str_new += str[i]
                else:
                    if len(str_new) == 0 or str_new[len(str_new)-1] == "\b":
                        str_new += str[i]
                    else:
                        str_new = str_new[0:len(str_new)-1]
            str = str_new
            
            for i in range(0, len(str)):
                if str[i] != "\b":
                    break
            
            self.output_buffer = self.output_buffer[0:len(self.output_buffer)-i] + str[i:]

            r = crt.Screen.MatchIndex
            if r == 1:          #   --More--  
                self.output_buffer = self.output_buffer + waitStrings[r - 1]
                crt.Screen.Send(" ")
            else:
                end = True
        
        self.keepLogin(exitDiagnose)
        
    def show(self, cmd, toEnd = True, exitDiagnose = False):
        self.keepLogin(exitDiagnose)
        
        origin_syn = crt.Screen.Synchronous
        crt.Screen.Synchronous = True
        crt.Screen.IgnoreEscape = True
        self.output_buffer = ""
        self.sendCmd(cmd)
        if toEnd:
            self.showToEnd(exitDiagnose)
            
        crt.Screen.Synchronous = origin_syn
        crt.Screen.IgnoreEscape = False
        
        self.output_buffer = re.sub(r'\r\n', "\n", self.output_buffer)   
        return self.output_buffer

        

        
Debugger.output("===============Start==============") 
Debugger.output("os.getcwd=%s"%os.getcwd())
Debugger.output("Date=%s"%time.strftime("%Y-%m-%d %H:%M:%S"))

vty = CBdcomVty(hostname, username, password, connectString)
vty.sendCmd("\n")
detail = vty.show("show memory region detail")
Debugger.output("region detail: %s"%detail)
dozen = re.findall(r'(\d+) BASE|/\s*(\d+)\)\]', detail)
regions = list()
for t in dozen:
    for e in t:
        if e != '':
            regions.append(int(e))
Debugger.output(regions)  

regionParser = re.compile(r'Buffer: (0x[a-f0-9]{8})\((\d+)\)   alloc at (0x[a-f0-9]{8})')

for region in regions:
    detail = vty.show("show memory region " + str(region))
    dozen = regionParser.findall(detail)
    for t in dozen:
        addr = int(t[2], 16)
        size = int(t[1])
        CAllocPoint(addr).addRecord(size)
        
detail = vty.show("show memory heap detail")
dozen = re.findall(r'([a-f0-9]{8}): size (\d+)\s+alloc at ([a-f0-9]{8})', detail)
for t in dozen:
    addr = int(t[2], 16)
    size = int(t[1])
    CAllocPoint(addr).addRecord(size)

CAllocPoint.printStatistic()
Debugger.output("===============End==============\n\n")   

