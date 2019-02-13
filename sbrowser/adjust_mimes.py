#!/usr/bin/env python2.7
#coding:utf-8

def main():
  fp = open('/home/jmramoss/Descargas/mimes.txt', 'r')
  line = fp.readline()
  cnt = 1
  listmimes = list()
  while line:
    idx = line.find("\t")
    line = line if idx < 0 else line[idx+1:]
    line = line.replace("\n", "")
    if line not in listmimes:
      listmimes.append(line)
    print("Line {}: {}".format(cnt, line.strip()))
    line = fp.readline()
    cnt += 1
  fp.close()
  listmimes.sort()
  print(str(listmimes))
  print(len(listmimes))
  resultStr = ""
  resultStr += "    mimeType = \"\"" + "\n"
  length = len(listmimes)
  for idx in range(0, length, 4):
    resultStr += "    mimeType += \""
    resultStr += listmimes[idx+0] + ", " if idx+0 < length else ""
    resultStr += listmimes[idx+1] + ", " if idx+1 < length else ""
    resultStr += listmimes[idx+2] + ", " if idx+2 < length else ""
    resultStr += listmimes[idx+3] + ", " if idx+3 < length else ""
    resultStr += "\"" + "\n"
  print(resultStr)
  
    
if True and __name__ == '__main__':
  main()

