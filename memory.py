import sys

file = open("memory.txt")
total = 0
while 1:
    line = file.readline()
    if not line:
        break
    size = int(line.split()[2])
    num = int(line.split()[8])
    
    #print "Size:{} num:{} total_mem:{}"%(size)%(num)%(size*num)
    print size,num,size*num
    total += size*num

print total
