
import sys


file1 = open(sys.argv[1], "r")
output = []
outfile = "config_sort_db.txt"
while 1:
    line =  file1.readline()
    output.append(line)
    if not line:
        break
file1.close()
output2 = sorted(output)
#print output2
file2 = open(outfile, "w+")
for tmp in output2:
    file2.write(tmp)
file2.close()
