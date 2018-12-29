#!/usr/bin/env python2.7
#coding:utf-8

from browser import Browser
import rarfile

'''
https://www.lectulandia.com/
OK: http://lelibros.online/
https://www.fiuxy.bz/
https://gratismas.org/
http://internetculture.ovh/
https://ebookmundo.org/
https://www.epublibre.org/
'''

class BetBrowser(Browser):

  def __init__ (self):
    super(BetBrowser, self).__init__()

  def selectEpubImages (self, folder):
    result = []
    for ifile in os.listdir(folder):
      path = os.path.join(folder, ifile)
      if (os.path.isfile(path)):
        if path.endswith(".epub") or path.endswith(".jpg"):
          result.append(path)
      else:
        selectedFiles = self.selectEpubImages(path)
        result.extend(selectedFiles)
      print(">>> " + str(ifile))
    return result

  def removeAds (self):
    while self.getNumWindows() > 1:
      self.wait(5).realCloseTab()
    return self

  def extractFile (self, addr):
    result = None
    tmpdir = tempfile.mkdtemp(prefix='.tmp_')
    rf = rarfile.RarFile(addr)
    rf.extractall(path=tmpdir)
    result = tmpdir
    return result

  def bet (self):
    result = None

    result = self.doBet()
    
    self.close()
    return result
    
  def doBet (self):
    pass
