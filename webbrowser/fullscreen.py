#!/usr/bin/env python2.7
#coding:utf-8
from betbrowser import BetBrowser
import sys

class Fullscreen(BetBrowser):

  def __init__ (self, starturl, saveFile):
    super(Fullscreen, self).__init__()
    self.openUrl(starturl)
    self.saveFile = saveFile

  def doBet (self):
    result = None

    saveFile = self.saveFile
    if saveFile is None:
      saveFile = '/media/jmramoss/ALMACEN/bettenis/fullscreen.jpg'
    self.maximize().wait(10).fullscreenshot(saveFile)

if __name__ == '__main__':
  saveFile = None
  if len(sys.argv) > 2:
    saveFile = sys.argv[2]
  print(Fullscreen(sys.argv[1], saveFile).bet())
