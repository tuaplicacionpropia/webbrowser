#!/usr/bin/env python2.7
#coding:utf-8

import os
import time
import datetime
import hjson
import numpy as np
import codecs
import shutil

#click problem
#https://stackoverflow.com/questions/11908249/debugging-element-is-not-clickable-at-point-error
#https://peter.sh/experiments/chromium-command-line-switches/#disable-popup-blocking
#http://toolsqa.com/selenium-webdriver/how-to-download-files-using-selenium/
#http://allselenium.info/file-downloads-python-selenium-webdriver/
#https://peter.sh/experiments/chromium-command-line-switches/#disable-popup-blocking
#https://stackoverflow.com/questions/23530399/chrome-web-driver-download-files
#https://stackoverflow.com/questions/18439851/how-can-i-download-a-file-on-a-click-event-using-selenium
#https://stackoverflow.com/questions/32205245/need-the-chrome-equivalent-of-these-firefox-browser-profile-settings-in-seleni

#Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36

'''
https://www.lectulandia.com/
OK: http://lelibros.online/
https://www.fiuxy.bz/
https://gratismas.org/
http://internetculture.ovh/
https://ebookmundo.org/
https://www.epublibre.org/
'''



def preSimilar (text):
  result = text
  result = result.upper()
  result = result.replace(u"Á", u"A")
  result = result.replace(u"É", u"E")
  result = result.replace(u"Í", u"I")
  result = result.replace(u"Ó", u"O")
  result = result.replace(u"Ú", u"U")
  result = result.replace(u"Ä", u"A")
  result = result.replace(u"Ë", u"E")
  result = result.replace(u"Ï", u"I")
  result = result.replace(u"Ö", u"O")
  result = result.replace(u"Ü", u"U")
  return result

def reduceSimilarTo (src, target):
  result = src
  wordsSrc = src.split(" ")
  #print("wordsSrc= "+ str(wordsSrc))
  wordsTarget = target.split(" ")
  #print("wordsTarget= "+ str(wordsTarget))
  if len(wordsSrc) > len(wordsTarget):
    maxd = None
    word = None
    for wordSrc in wordsSrc:
      minDistance = None
      for wordTarget in wordsTarget:
        distance = levenshtein(wordSrc, wordTarget)
        #print("distancia = " + str(distance) + " entre " + wordSrc + " y " + wordTarget)
        if minDistance is None or distance < minDistance:
          minDistance = distance

      if maxd is None or minDistance > maxd:
        word = wordSrc
        maxd = minDistance
    if word:
      #print("palabra elegida para eliminar = " + word)
      result = ""
      for wordSrc in wordsSrc:
        if word != wordSrc:
          result += " " if len(result) > 0 else ""
          result += wordSrc
      result = reduceSimilarTo(result, target)
  result = preSimilar(result)
  return result
  
def myLevenshtein (text, search):
  result = 0
  search = preSimilar(search)
  text = preSimilar(text)
  text = reduceSimilarTo(text, search)
  #print("comparing " + text + " with " + search)
  result = levenshtein(text, search)
  #print("distance =  " + str(result))
  return result

def levenshtein(seq1, seq2):  
  size_x = len(seq1) + 1
  size_y = len(seq2) + 1
  matrix = np.zeros ((size_x, size_y))
  for x in xrange(size_x):
    matrix [x, 0] = x
  for y in xrange(size_y):
    matrix [0, y] = y

  for x in xrange(1, size_x):
    for y in xrange(1, size_y):
      if seq1[x-1] == seq2[y-1]:
        matrix [x,y] = min(
            matrix[x-1, y] + 1,
            matrix[x-1, y-1],
            matrix[x, y-1] + 1
        )
      else:
        matrix [x,y] = min(
            matrix[x-1,y] + 1,
            matrix[x-1,y-1] + 1,
            matrix[x,y-1] + 1
        )
  #print (matrix)
  return matrix[size_x - 1, size_y - 1]

def loadDataFolder (date):
  result = None
  home = os.path.expanduser("~")
  foldername1 = "browser"

  if type(date) == type("") or type(date) == type(u""):
    date = datetime.datetime.strptime(date, '%d/%m/%Y')

  foldername2 = datetime.datetime.strftime(date, '%Y%m%d')
    
  folder1 = os.path.join(home, foldername1)
  if not os.path.exists(folder1):
    os.makedirs(folder1)
  folder2 = os.path.join(folder1, foldername2)
  
  result = folder2
  return result

def savedata (name, data, date=None):
  result = None
  home = os.path.expanduser("~")
  foldername1 = "browser"

  if type(date) == type("") or type(date) == type(u""):
    date = datetime.datetime.strptime(date, '%d/%m/%Y')
      
  foldername2 = ""
  if date:
    foldername2 = datetime.datetime.strftime(date, '%Y%m%d')
  else:
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    monthText = datetime.datetime.strftime(tomorrow, '%b')
    tomorrowText = datetime.datetime.strftime(tomorrow, '%Y%m%d')
    #foldername2 = "20180902"
    foldername2 = tomorrowText
   
  folder1 = os.path.join(home, foldername1)
  if not os.path.exists(folder1):
    os.makedirs(folder1)
  folder2 = os.path.join(folder1, foldername2)
  if not os.path.exists(folder2):
    os.makedirs(folder2)
  path = os.path.join(folder2, name) + ".hjson"
   
  #fp = codecs.open(path, mode='w', encoding='utf-8')
  #print("saving on " + path)
  #hjson.dump(data, fp)
  saveObj(path, data)
  #print u'saving data on ' + path
    
  result = path
  return result

#'%Y-%m-%d' -> '%d/%m/%Y'
def date2NormalFormat (date):
  result = None
  odate = datetime.datetime.strptime(date, '%Y-%m-%d')
  result = datetime.datetime.strftime(odate, '%d/%m/%Y')
  return result

def parseDateSpanishFormat (date):
  result = None
  result = datetime.datetime.strptime(date, '%d/%m/%Y')
  return result

def formatDateSpanishFormat (date):
  result = None
  result = datetime.datetime.strftime(date, '%d/%m/%Y')
  return result



def makeGroups (lst, sizeGroup=5):
  result = list()
  numSize = len(lst)
  idx = 0
  group = None
  for item in lst:
    newItem = (item, idx, numSize)
    idx += 1
    if group is None or len(group) >= sizeGroup:
      group = list()
      result.append(group)
    group.append(newItem)
  #print("num groups = " + str(len(result)))
  #print("groups = " + str(result))
  return result

def listDirectories (path):
  result = None
  result = [os.path.join(path, o) for o in os.listdir(path) if os.path.isdir(os.path.join(path,o))]
  return result

def containsDirectory (path, name):
  result = False
  for o in os.listdir(path):
    if os.path.isdir(os.path.join(path,o)):
      if name == o:
        result = True
        break
  return result

def getLastModification (path):
  result = None
  stat = os.stat(path)
  ctime = None
  try:
    ctime = stat.st_birthtime
  except:
    ctime = stat.st_mtime
  result = datetime.datetime.fromtimestamp(ctime)
  return result
  
def getLastModificationAgo (path):
  result = None
  mdate = getLastModification(path)
  now = datetime.datetime.now()
  result = (now-mdate).total_seconds()
  return result


#2017-08-18
def checkDateGT (date1, date2):
  result = False
  edate1 = datetime.datetime.strptime(date1, '%Y-%m-%d')
  edate2 = datetime.datetime.strptime(date2, '%Y-%m-%d')
  result = True if edate1 > edate2 else False
  return result

def noEmpty (array):
  result = False
  if array is not None and len(array) > 0:
    result = True
  return result

def defaultBackupObjPath (path):
  result = None
  #result = path + '.bak'
  dirname = os.path.dirname(path)
  basename = os.path.basename(path)
  newname = '.bak' + basename
  result = os.path.join(dirname, newname)
  return result

def loadObj (path):
  result = None
  try:
    fp = codecs.open(path, mode='r', encoding='utf-8')
    result = hjson.load(fp)
    #print("loaded " + path)
  except:
    newpath = defaultBackupObjPath(path)
    if os.path.exists(newpath):
      fp = codecs.open(newpath, mode='r', encoding='utf-8')
      result = hjson.load(fp)
      #print("loaded " + newpath)
      shutil.copyfile(newpath, path)
  return result

def backupObj (path):
  if os.path.exists(path):
    canLoad = False
    try:
      hjson.load(codecs.open(path, mode='r', encoding='utf-8'))
      canLoad = True
    except:
      canLoad = False
    if canLoad:
      newpath = defaultBackupObjPath(path)
      shutil.copyfile(path, newpath)

def touchFile (path):
  os.remove(path)
  open(path, 'a').close()

def saveObj (path, obj):
  backupObj(path)
  fp = codecs.open(path, mode='w', encoding='utf-8')
  hjson.dump(obj, fp)
