import sys

file = open("memory.txt")
total = 0
total_used = 0
while 1:
    line = file.readline()
    if not line:
        break
    size = int(line.split()[2])
    used = int(line.split()[4])
    num = int(line.split()[8])

    #print "Size:%d num:%d total_mem:%d"%(size,num,size*num)
    print size,num,size*used,size*num
    total += size*num
    total_used += size*used
print total_used,total
