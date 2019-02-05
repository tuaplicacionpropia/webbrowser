#!/usr/bin/env python2.7
#coding:utf-8

import re
import autopy
import requests
import shutil
import os
import stat
import time
import sys
import clipboard
import rarfile
import tarfile
import zipfile
import codecs
import hjson
import numpy as np
import datetime
import utils
import subprocess


from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import pyscreenshot
import cv2
import tempfile

BROWSER_TIMEOUT = 30
BROWSER_MINIMIZE = False

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


class Browser(object):

  def __init__ (self, driver=None):
    self.driver = driver
    self.pivots = list()
    self.params = {}
    self.currentPage = None
    self.__iDownloadDir__ = None

  def __download_file__(self, url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
      for chunk in r.iter_content(chunk_size=1024): 
        if chunk: # filter out keep-alive new chunks
          f.write(chunk)
          #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


  def installFirefoxDriver (self):
    #https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz
    firefoxUrlDriver = "https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz"
    fileDriver = self.__download_file__(firefoxUrlDriver)

    userHome = os.path.expanduser("~")

    tf = tarfile.open(fileDriver)
    tf.extractall(path=userHome)

    realDriver = userHome + "/geckodriver"
    st = os.stat(realDriver)
    os.chmod(realDriver, st.st_mode | stat.S_IEXEC)

    pass

  def installChromeDriver (self):
    #https://chromedriver.storage.googleapis.com/2.45/chromedriver_linux64.zip
    urlDriver = "https://chromedriver.storage.googleapis.com/2.45/chromedriver_linux64.zip"
    fileDriver = self.__download_file__(urlDriver)

    userHome = os.path.expanduser("~")

    tf = zipfile.ZipFile(fileDriver)
    tf.extractall(path=userHome)

    realDriver = userHome + "/chromedriver"
    st = os.stat(realDriver)
    os.chmod(realDriver, st.st_mode | stat.S_IEXEC)

    pass

  def __getDriverFirefox (self, download=False):
    result = None
    userHome = os.path.expanduser("~")
    driverPath = userHome + '/geckodriver'
    if not os.path.isfile(driverPath) and download:
      self.installFirefoxDriver()
    if os.path.isfile(driverPath):
      result = driverPath
    return result

  def __getDriverChrome (self, download=False):
    result = None
    userHome = os.path.expanduser("~")
    driverPath = userHome + '/chromedriver'
    if not os.path.isfile(driverPath) and download:
      self.installChromeDriver()
    if os.path.isfile(driverPath):
      result = driverPath
    return result

  def pushPivot (self, pivot):
    self.pivots.append(pivot)
    
  def popPivot (self):
    self.pivots.pop()

  def openUrl (self, start=None, autoSave=None, downloadDir=None, profile=None, waitUntilLoad=True, headless=False, runFirefox=False, runChrome=False):
    if self.driver is None:
      userHome = os.path.expanduser("~")

      chromeDriverPath = userHome + '/chromedriver'
      firefoxDriverPath = userHome + '/geckodriver'
    
      checkFirefox = False
      checkChrome = False
      if os.path.isfile(chromeDriverPath):
        checkChrome = True
      elif os.path.isfile(firefoxDriverPath):
        checkFirefox = True

      if not checkChrome and not checkFirefox:
        driverPath = self.__getDriverChrome(download=True)
        if os.path.isfile(driverPath):
          checkChrome = True
        else:
          driverPath = self.__getDriverFirefox(download=True)
          if os.path.isfile(driverPath):
            checkFirefox = True

      if runChrome:    
        if checkChrome:
          self.openChrome(start, autoSave, downloadDir, headless=headless)
      elif runFirefox:
        if checkFirefox:
          self.openFirefox(start, autoSave, downloadDir, profile, headless=headless)
      else:
        if checkChrome:
          self.openChrome(start, autoSave, downloadDir, headless=headless)
        elif checkFirefox:
          self.openFirefox(start, autoSave, downloadDir, profile, headless=headless)
    else:
      if BROWSER_MINIMIZE:
        self.driver.minimize_window()
      self.driver.get(start)

    if waitUntilLoad:
      self.waitUntilFirstLoad()

    return self

  #https://support.mozilla.org/es/questions/1066799
  #about:config
  #  browser.link.open_newwindow.restriction
  #     0
  def openFirefox (self, start=None, autoSave=None, downloadDir=None, profile=None, headless=False):
    driverPath = self.__getDriverFirefox(download=True)
    
    #if downloadDir is None:
    #  downloadDir = tempfile.mkdtemp(prefix='.download_')

    options = None
    options = FirefoxOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--marionette')
    if headless:
      options.add_argument("-headless")
    '''
    if autoSave != None or downloadDir != None:
      options.set_preference("browser.download.folderList",2)
      options.set_preference("browser.download.manager.showWhenStarting", False)
      #("specificationLevel", 1)
      if downloadDir != None:
        # downloadDir = '/home/jmramoss/Descargas/mocks'
        options.set_preference("browser.download.dir", downloadDir)
      if autoSave != None:
        #autoSave = 'application/zip, application/epub+zip'
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", autoSave)
      #options.set_preference("http.response.timeout", 5)
      #options.set_preference("dom.max_script_run_time", 5)        
    '''

    self.__iDownloadDir__ = tempfile.mkdtemp(prefix='.download_')
    os.rmdir(self.__iDownloadDir__)
    iDownloadDir = self.__iDownloadDir__

    if downloadDir is not None:
      self.changeDownloadDir(downloadDir)
    else:
      self.changeDownloadDir(self.getDefaultDownloadDir())

    #if downloadDir != None:
    self.set_param("browser.download.dir", iDownloadDir)
    

    fp = None
    if profile != None:
      #profile = '/home/jmramoss/.mozilla/firefox/wp4th1of.default'
      fp = webdriver.FirefoxProfile(profile)
    else:
      #fp = webdriver.FirefoxProfile()
      fp = webdriver.FirefoxProfile('/home/jmramoss/.mozilla/firefox/wp4th1of.default')

    #fp = webdriver.FirefoxProfile('/home/jmramoss/.mozilla/firefox/wp4th1of.default')
    fp.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36")

    #fp.DEFAULT_PREFERENCES['frozen']["browser.link.open_newwindow.restriction"] = "0"
    #fp.set_preference("browser.link.open_newwindow.restriction", "0")

    #profile
    #/home/jmramoss/.mozilla/firefox/wp4th1of.default


    #Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36
    #Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0

    if fp != None and (autoSave != None or downloadDir != None):
      fp.set_preference("browser.download.folderList", 2)
      fp.set_preference("browser.download.manager.showWhenStarting", False)
      #if downloadDir != None:
        # downloadDir = '/home/jmramoss/Descargas/mocks'
      fp.set_preference("browser.download.dir", iDownloadDir)
      if autoSave != None:
        #autoSave = 'application/zip, application/epub+zip'
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", autoSave)
    
    params = {'executable_path': driverPath}
    if fp != None:
      params['firefox_profile'] = fp
    if options != None:
      params['firefox_options'] = options
    driver = webdriver.Firefox(**params)
    self.driver = driver
    
    if start != None:
      driver.set_page_load_timeout(BROWSER_TIMEOUT)
      try:
        if BROWSER_MINIMIZE:
          driver.minimize_window()
        driver.get(start)
      except:
        pass
        #print(u"timeout")

    return self

  def changeDownloadDir (self, downloadDir):
    #print("__iDownloadDir__ = " + self.__iDownloadDir__)
    #print("downloadDir = " + downloadDir)
    iDownloadDir = self.__iDownloadDir__
    if os.path.islink(iDownloadDir):
      os.remove(iDownloadDir)
    subprocess.call(['ln', '-s', downloadDir, iDownloadDir])

    #self.driver.set_preference("download.default_directory", downloadDir)
    #self.prefs["download.default_directory"] = downloadDir
    #self.options.add_experimental_option("prefs",self.prefs)

  def getDefaultDownloadDir (self):
    result = None
    home = os.path.expanduser("~")
    result = os.path.join(home, 'Descargas')
    return result

  def openChrome (self, start=None, autoSave=None, downloadDir=None, headless=False):
    driver_path = self.__getDriverChrome(download=True)

    os.environ["webdriver.chrome.driver"] = driver_path

    self.__iDownloadDir__ = tempfile.mkdtemp(prefix='.download_')
    os.rmdir(self.__iDownloadDir__)
    iDownloadDir = self.__iDownloadDir__

    self.changeDownloadDir(self.getDefaultDownloadDir())

    #if downloadDir is None:
    #  downloadDir = tempfile.mkdtemp(prefix='.download_')

    options = ChromeOptions()
    if headless:
      options.add_argument("--headless")
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36")

    prefs = {"download.default_directory": iDownloadDir}
    options.add_experimental_option("prefs",prefs)

    if downloadDir != None:
      self.changeDownloadDir(downloadDir)

    if False and (autoSave != None or downloadDir != None):
      options.add_option("browser.download.folderList",2)
      options.add_option("browser.download.manager.showWhenStarting", False)
      if downloadDir != None:
        # downloadDir = '/home/jmramoss/Descargas/mocks'
        options.add_option("browser.download.dir", downloadDir)
      if autoSave != None:
        #autoSave = 'application/zip, application/epub+zip'
        options.add_option("browser.helperApps.neverAsk.saveToDisk", autoSave)

    params = {'executable_path': driver_path}
    if options != None:
      params['chrome_options'] = options

    driver = webdriver.Chrome(**params)
    self.driver = driver

    if start != None:
      driver.set_page_load_timeout(BROWSER_TIMEOUT)
      if BROWSER_MINIMIZE:
        driver.minimize_window()
      driver.get(start)

    if downloadDir != None:
      self.set_param("browser.download.dir", downloadDir)
      
    return self

  #url = 'https://descargarlo.com/gmas.php?id=17952'
  def openRealChrome (self, url, maxLoadTimeSeconds=30):
    #os.system("rm -rfv /home/jmramoss/.config/google-chrome/miProfile")
    #os.system("mkdir -p /home/jmramoss/.config/google-chrome/miProfile")
    #os.system("cp -avr /home/jmramoss/.config/google-chrome/copy_Profile/* /home/jmramoss/.config/google-chrome/miProfile")
    #os.system("cp -avr /home/jmramoss/.config/google-chrome/Default/* /home/jmramoss/.config/google-chrome/miProfile")
    #exit(0)

    #os.system("google-chrome --profile-directory=miProfile https://descargarlo.com/gmas.php?id=17952")
    #os.system("google-chrome https://descargarlo.com/gmas.php?id=17952")
    #os.system("google-chrome --incognito https://descargarlo.com/gmas.php?id=17952")
    cmd = 'google-chrome --new-window ' + url + ' &'
    os.system(cmd)
    time.sleep(maxLoadTimeSeconds)
    return self

  def realClickMouse (self, x, y, waitSeconds=5):
    autopy.mouse.smooth_move(x, y)
    autopy.mouse.click(autopy.mouse.LEFT_BUTTON)
    time.sleep(waitSeconds)
    return self

  def realCloseTab (self, waitSeconds=5):
    autopy.key.tap('w', autopy.key.MOD_CONTROL)
    time.sleep(waitSeconds)
    return self

  def realSelectText (self, x0, y0, x1, y1, waitSeconds=None):
    result = None
    autopy.mouse.smooth_move(x0, y0)
    autopy.mouse.toggle(True, autopy.mouse.LEFT_BUTTON)
    autopy.mouse.smooth_move(x1, y1)
    autopy.mouse.toggle(False, autopy.mouse.LEFT_BUTTON)
    autopy.key.tap('c', autopy.key.MOD_CONTROL)
    result = clipboard.paste()
    if waitSeconds:
      time.sleep(waitSeconds)
    return result

  def solveGoogleReChaptcha (self):
    result = True
    self.realClickMouse(871, 614, 5)
    self.realClickMouse(1011, 689, 5)
    result = self.realSelectText(85, 432, 85, 932, 5)
    return result

  def set_param (self, key, value):
    self.params[key] = value
    return self

  def get_param (self, key):
    return self.params[key] if key in self.params else None

  def selectLastDownload (self, folder=None):
    result = None
    if folder == None:
      folder = '/home/jmramoss/Descargas'
    files = self.sorted_dir(folder)
    result = files[0] if len(files) > 0 else None
    if result != None:
      result = os.path.join(folder, result)
    return result

  def _do_close_alert (self):
    try:
      alert = self.driver.switch_to_alert()
      #print "Aler text:" + alert.text
      alert.accept()
      #print "Alert detected, accept it"
      return True
    except:
      #print "No alert here"
      return False

  def selectFrame (self, element):
    frame = self._element(element)
    self.driver.switch_to_frame(frame)
    return self

  def selectDefaultFrame (self):
    self.driver.switch_to_default_content()
    return self

  def getNumWindows (self):
    result = 0
    result = len(self.driver.window_handles)
    #print(u"numWindows = " + str(result))
    return result

  def closeLastWindow (self):
    numWindows = self.getNumWindows()
    self.closeWindow(numWindows - 1)
    return self

  def hideWindow (self):
    self.driver.set_window_position(-200, 0)

  def showWindow (self):
    self.driver.set_window_position(0, 0)

  def closeTab (self):
    #elem = self.driver.find_element_by_tag_name("body")
    #elem.send_keys(Keys.CONTROL+"w")
    ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('w').key_up(Keys.CONTROL).perform()
    self.wait(2)
    return self
    
  #def bodyCloseTab (self):
  #  element = self._element('//body')
  #  element.send_keys(Keys.CONTROL + 'w')
  #  self.wait(5)
    
  def closeWindow (self, index):
    self.driver.switch_to.window(self.driver.window_handles[index])
    while self._do_close_alert() == True:
      self._do_close_alert()
    try:
      self.driver.close()
    except:
      pass
    self.wait(2)
    numWindows = self.getNumWindows()
    if numWindows > 0:
      newIndex = index - 1
      if newIndex < 0:
        newIndex = 0
      self.driver.switch_to.window(self.driver.window_handles[newIndex])
      self.wait(2)
    else:
      self.close()
    return self

  def close (self):
    if self.driver:
      self.driver.quit()
    return self

  def saveAsContext (self, element):
    actionChains = ActionChains(self.driver)
    element = self._element(element)
    actionChains.context_click(element).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.RETURN).perform();
    return self

  def saveAs (self, element):
    self.maximize()
    try:
      self.click(element)
    except:
      self.clickVirtual(element)
    self.realClickMouse(771, 597)
    self.realClickMouse(1211, 700)
    return self

  def sorted_dir(self, folder):
    def getmtime(name):
      path = os.path.join(folder, name)
      return os.path.getmtime(path)

    return sorted(os.listdir(folder), key=getmtime, reverse=True)

  def download (self, element, target):
    self.saveAs(element)
    downloadDir = self.get_param("browser.download.dir")
    if downloadDir != None:
      #print("downloadDir = " + downloadDir)
      files = self.sorted_dir(downloadDir)
      #print("files = " + str(files))
      if len(files) > 0:
        srcFile = os.path.join(downloadDir, files[0])
        os.rename(srcFile, target)
    return self

  def collect (self, element, attrib):
    result = []
    elements = self.driver.find_elements_by_xpath(element)
    #print("collection '" + element + "' len = " + str(len(elements)))
    for element in elements:
      item = element.get_attribute(attrib)
      result.append(item)
    return result

  def processItems (self, element, fn):
    elements = self.driver.find_elements_by_xpath(element)
    #print("collection '" + element + "' len = " + str(len(elements)))
    for element in elements:
      args = [self, element]
      fn(*args)

  def get_text (self, element):
    result = ""
    array = self.collect(element, "innerText")
    for item in array:
      result += item
    return result

  def extractUrlsFromText (self, text):
    result = []
    pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(pattern, text)
    fixUrls = []
    for url in urls:
      idx = url.find('<')
      if idx >= 0:
        url = url[0:idx]
      fixUrls.append(url)
    result.extend(fixUrls)
    return result

  def extractUrls (self, element):
    result = []
    array = self.collect(element, "innerHTML")
    #print("HTML = " + str(array))
    for item in array:
      fixUrls = self.extractUrlsFromText(item)
      result.extend(fixUrls)
    return result

  def exists (self, element):
    result = False
    try:
      element = self._element(element)
      if element != None:
        result = True
    except:
      result = False
    return result

  def tryElement (self, element):
    result = None
    try:
      result = self._element(element)
    except:
      result = None
    return result

  def _element (self, element):
    result = None
    ref, element = self._refFind(element)
    result = element
    if type(element) == type("") or type(element) == type(u""):
      result = ref.find_element_by_xpath(element)
    return result

  def debugHtml (self, element):
    element = self._element(element)
    html = element.get_attribute('innerHTML')
    html = u' '.join((html)).encode('utf-8').strip()
    print(str(html))
    return self

  def attr (self, element, name):
    result = None
    try:
      element = self._element(element)
    except:
      element = None
    if element is not None:
      result = element.get_attribute(name)
    return result

  def debugHtml2 (self, element):
    element = self._element(element)
    html = element.get_attribute('innerHTML')
    #html = u' '.join((html)).encode('utf-8').strip()
    print(str(html))
    return self

  #http://internetculture.ovh/assets/biblioteca/Bevilacqua2.epub
  def downloadHref(self, element, filename=None):
    result = None
    element = self._element(element)
    url = element.get_attribute("href")
    result = self.downloadUrl(url, filename)
    return result

  def scrollTo (self, element):
    #element = self._element(element)
    #self.driver.execute_script("arguments[0].scrollIntoView();", element)
    domelement = self._element(element)
    js = ""
    numTry = 5
    while numTry > 0:
      try:
        numTry -= 1
        self.driver.execute_script("arguments[0]." + js + "scrollIntoView();", domelement)
        break
      except:
        js += "parentNode."
    return self

  #http://internetculture.ovh/assets/biblioteca/Bevilacqua2.epub
  def downloadUrl(self, url, filename=None):
    result = None
    #url = element.get_attribute("href")
    #print(u"downloading url = " + url)
    target = filename
    if filename == None:
      filename = url[url.rfind('/')+1:]
      target = '/home/jmramoss/' + filename
    #print('downloading ' + url)
    response = requests.get(url, stream=True)
    outfile = open(target, 'wb')
    shutil.copyfileobj(response.raw, outfile)
    outfile.close()
    del response
    result = target
    return result

  def back (self):
    self.driver.back()
    return self
 
  def forward (self):
    self.driver.forward()
    return self
 
  def refresh (self): 
    self.driver.refresh()
    return self

  def maximize (self):
    self.driver.maximize_window()
    return self

  def minimize (self):
    self.driver.minimize_window()
    return self

  def goTo (self, url):
    self.driver.get(url)
    return self

#  waitFor('//*[@id="search"]');

  def screenshot(self, target=None):
    result = None
    if target == None:
      target = "screenshot.png"
    self.driver.save_screenshot(target)
    result = target
    return result

  def scroll2Top (self):
    total_width = self.driver.execute_script("return document.body.offsetWidth")
    total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = self.driver.execute_script("return document.body.clientWidth")
    viewport_height = self.driver.execute_script("return window.innerHeight")
    #self.driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
    pass
  
  def scroll2Bottom (self):
    total_width = self.driver.execute_script("return document.body.offsetWidth")
    total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = self.driver.execute_script("return document.body.clientWidth")
    viewport_height = self.driver.execute_script("return window.innerHeight")
    #self.driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
    pass

  def scrollBy (self, x, y):
    result = None
    self.driver.execute_script("window.scrollBy({0}, {1})".format(x, y))
    scrollX = self.driver.execute_script("return window.scrollX")
    scrollY = self.driver.execute_script("return window.scrollY")
    result = [scrollX, scrollY]
    return result

  def scrollToBottomStepByStep (self, step=1000, wait=0.3):
    prevScroll = None
    numTry = 5
    for i in range(numTry):
      while True:
        scroll = self.scrollBy(0, step)
        gobreak = True
        gobreak = gobreak and prevScroll is not None
        gobreak = gobreak and scroll is not None
        gobreak = gobreak and prevScroll[1] == scroll[1]
        gobreak = gobreak and prevScroll[0] == scroll[0]
        if gobreak:
          break
        prevScroll = scroll
        self.wait(wait)
      self.wait(wait*10)


  def fullscreenshot(self, target=None):
    #print(u"Starting chrome full page screenshot workaround ...")

    #currentScrollLeft = self.driver.execute_script("return window.scrollLeft")
    #currentScrollTop = self.driver.execute_script("return window.scrollTop")

    self.driver.execute_script("window.scrollTo({0}, {1})".format(0, 0))

    total_width = self.driver.execute_script("return document.body.offsetWidth")
    total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = self.driver.execute_script("return document.body.clientWidth")
    viewport_height = self.driver.execute_script("return window.innerHeight")
    #print(u"Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height,viewport_width,viewport_height))
    rectangles = []

    i = 0
    while i < total_height:
      ii = 0
      top_height = i + viewport_height

      if top_height > total_height:
        top_height = total_height

      while ii < total_width:
        top_width = ii + viewport_width

        if top_width > total_width:
          top_width = total_width

        #print(u"Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
        rectangles.append((ii, i, top_width,top_height))

        ii = ii + viewport_width

      i = i + viewport_height

    stitched_image = Image.new('RGB', (total_width, total_height))
    previous = None
    part = 0

    for rectangle in rectangles:
      if not previous is None:
        self.driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
        #print(u"Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
        time.sleep(0.2)

      file_name = "part_{0}.png".format(part)
      #print(u"Capturing {0} ...".format(file_name))

      self.driver.get_screenshot_as_file(file_name)
      screenshot = Image.open(file_name)

      if rectangle[1] + viewport_height > total_height:
        offset = (rectangle[0], total_height - viewport_height)
      else:
        offset = (rectangle[0], rectangle[1])

      #print(u"Adding to stitched image with offset ({0}, {1})".format(offset[0],offset[1]))
      stitched_image.paste(screenshot, offset)

      del screenshot
      os.remove(file_name)
      part = part + 1
      previous = rectangle

    stitched_image.save(target)
    
    #self.driver.execute_script("window.scrollTo({0}, {1})".format(currentScrollLeft, currentScrollTop))
    self.driver.execute_script("window.scrollTo({0}, {1})".format(0, 0))
    
    #print(u"Finishing chrome full page screenshot workaround...")
    return True

  def setInput (self, element, value):
    element = self._element(element)
    if element.tag_name == "select":
      self._setSelectInput_(element, value)
    if element.tag_name == "select":
      self._setSelectInput_(element, value)
    elif element.tag_name == "input" and element.get_attribute("type") == "checkbox":
      self._setCheckbox(element, value)
    else:
      element.clear()
      element.send_keys(value)
    return self
    
  def _setSelectInput_ (self, element, value):
    options = element.find_elements_by_tag_name('option')
    for option in options:
      #print(option.text)
      if option.text.strip() == value:
        option.click()
        break
    return self

  def _setCheckbox (self, element, value):
    #element.set_attribute('checked', 'true' if value else 'false')
    cmd = "arguments[0].setAttribute('checked', '" + ('true' if value else 'false') + "')"
    #print(u"cmd = " + str(cmd))
    self.driver.execute_script(cmd, element)
    #driver.execute_script("arguments[0].setAttribute('value', arguments[1])", input, 'new value!');    
    return self

  #/home/jmramoss/selenium/option_save_file.png
  #/home/jmramoss/selenium/save_dialog.png
  def searchRectangle (self, pattern, baseImg=None):
    if baseImg == None:
      baseImg = os.path.join(tempfile.mkdtemp(prefix='.tmp_'), 'base.png')
      im = pyscreenshot.grab()
      im.save(baseImg)
      im.close()
      #print(u'screenshot = ' + str(baseImg))
    if True:
      # carga imagenes
      cvImgBase = cv2.imread(baseImg)
      cvImgPattern = cv2.imread(pattern)
      (patternHeight, patternWidth) = cvImgPattern.shape[:2]

      # encuentra el patron "No soy robot" en la captura de pantalla
      result = cv2.matchTemplate(cvImgBase, cvImgPattern, cv2.TM_CCOEFF)
      (_, _, minLoc, maxLoc) = cv2.minMaxLoc(result)
      topLeft = maxLoc
      botRight = (topLeft[0] + patternWidth, topLeft[1] + patternHeight)
      #autopy.mouse.smooth_move(topLeft[0], topLeft[1])
      #print(u"topLeft = " + str(topLeft) + u" botRight = " + str(botRight))
    return self

  def getDriver (self):
    return self.driver

  def openNewTab (self, url):
    #self.driver.send_keys(Keys.CONTROL + 'T')

    #body = self.driver.find_element_by_tag_name("body")

    self.driver.execute_script("window.open('');")

    #actions = ActionChains(self.driver)
    #actions.move_to_element(body)
    #actions.key_down(Keys.CONTROL)
    #actions.key_down('t')
    #actions.perform()
    #actions.key_up('t')
    #actions.key_up(Keys.CONTROL)

    self.selectWindow(len(self.driver.window_handles) - 1)
    if BROWSER_MINIMIZE:
      self.driver.minimize_window()
    self.driver.get(url)
    return self

  def clickNewWindow (self, element):
    domelement = self._element(element)
    self.wait(2)
    
    #last_height = self.driver.execute_script("return document.body.scrollHeight")
    #self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    self.driver.execute_script("arguments[0].scrollIntoView();", domelement)
    
    actions = ActionChains(self.driver)
    actions.move_to_element(domelement)
    actions.key_down(Keys.CONTROL)
    actions.click(domelement)
    actions.perform()
    self.wait(2)
    return self

  def showAllPageUrls (self):
    idx = 0
    for windows in self.driver.window_handles:
      #print(u"window idx = " + str(idx) + u" url = " + self.driver.current_url)
      idx += 1

  def getCurrentUrl (self):
    return self.driver.current_url

  def selectNewWindow (self, index=0):
    another_window = list(set(self.driver.window_handles) - {self.driver.current_window_handle})[index]
    self.driver.switch_to.window(another_window);

  def selectWindow (self, index=0):
    another_window = self.driver.window_handles[index]
    self.driver.switch_to.window(another_window);

  def selectNewTab (self):
    #self.driver.switch_to_window(self.driver.window_handles[1]) #assuming new tab is at index 1
    self.driver.switch_to.window(self.driver.window_handles[1]) #assuming new tab is at index 1
    return self

  def selectFirstTab (self):
    #self.driver.switch_to_window(self.driver.window_handles[0])
    self.driver.switch_to.window(self.driver.window_handles[0])
    return self

  def processAll (self, element, fn, *args):
    elements = self.driver.find_elements_by_xpath(element)
    idx = 1
    length = len(elements)
    for item in elements:
      listArgs = list()
      listArgs.extend(args)
      listArgs.append(item)
      listArgs.append(idx)
      listArgs.append(length)
      fn(*listArgs)
      idx += 1
    return self

  def _refFind (self, element):
    result = [self.driver, element]
    if type(element) == type(""):
      #toPrint = u"find element " + element
      #toPrint = u' '.join((toPrint)).encode('utf-8').strip()
      #print(toPrint)
      ref = self.driver
      numPivots = len(self.pivots)
      if numPivots > 0:
        ref = self.pivots[numPivots-1]
        element = "." + element
        #print(u"find element from relative " + element)
      result = [ref, element]
    return result

  def findSimilar (self, elements, search, attrName='innerText'):
    result = None
    search = utils.preSimilar(search)
    items = self.listElements(elements)
    currentDistance = 0
    for item in items:
      text = self.attr(item, attrName)
      #self.debugHtml(item)
      #print("comparing " + search + " with " + attrName + " " + text + ".")
      text = utils.preSimilar(text)
      text = utils.reduceSimilarTo(text, search)
      distance = utils.levenshtein(text, search)
      #print("comparing " + search + " with " + text + ". Distance = " + str(distance))
      if result is None or distance < currentDistance:
        result = item
        currentDistance = distance
    return result

  def listElements (self, element):
    result = None
    ref, element = self._refFind(element)
    result = ref.find_elements_by_xpath(element)
    return result

  def clickAll (self, element):
    elements = self.listElements(element)
    for item in elements:
      self.click(item)
    return self

  def wait_for(self, condition_function, *args):
    start_time = time.time()
    waitTime = 60
    while time.time() < start_time + waitTime:
      if condition_function(*args):
        return True
      else:
        time.sleep(0.1)
    raise Exception('Timeout waiting for {}'.format(condition_function.__name__))


  def page_has_state_complete(self):
    page_state = self.driver.execute_script('return document.readyState;') 
    return page_state == 'complete'

  def page_has_loaded(self):
    result = False
    new_page = self.driver.find_element_by_tag_name('html')
    if new_page.id != self.currentPage.id:
      result = True
      self.currentPage = new_page
    return result


  @staticmethod
  def clearTmpDir (delayTime=300):
    if delayTime is None:
      delayTime = 300
    dir_path = tempfile.gettempdir() 
    #print("tmpDir = " + dir_path)
    directories = utils.listDirectories(dir_path)
    for entry in directories:
      oldDir = (utils.getLastModificationAgo(entry) > delayTime)
      toDelete = oldDir and (os.path.basename(entry).startswith("tmp") and utils.containsDirectory(entry, 'webdriver-py-profilecopy'))
      toDelete = toDelete or (oldDir and os.path.basename(entry).startswith("rust_mozprofile."))
      if toDelete and entry.startswith("/tmp/"):
        print("WARNING!!!!!!!!!!!!!!!!!!!!!!! deleting directory " + entry)
        shutil.rmtree(entry)

  def waitUntilLoad(self):
    self.wait_for(self.page_has_loaded)
    self.wait_for(self.page_has_state_complete)
    return self

  def page1_has_loaded(self):
    result = False
    new_page = self.driver.find_element_by_tag_name('html')
    if new_page.id is not None:
      result = True
      self.currentPage = new_page
    return result

  def waitUntilFirstLoad(self):
    #print("waiting")
    self.wait_for(self.page1_has_loaded)
    #print("loaded")
    self.wait_for(self.page_has_state_complete)
    #print("complete")
    return self

  def waitExists (self, element):
    #print("waiting " + element)
    self.wait_for(self.exists, element)
    #print("YA waiting " + element)
    return self

  def click (self, element, wait=True, scroll=True):
    domelement = self._element(element)
    if wait:
      self.wait(2)
    if scroll:
      js = ""
      numTry = 5
      while numTry > 0:
        try:
          numTry -= 1
          self.driver.execute_script("arguments[0]." + js + "scrollIntoView();", domelement)
          break
        except:
          js += "parentNode."
    if wait:
      self.wait(1)
    domelement.click()
    if wait:
      self.wait(2)
    return self

  def clickVirtual (self, element):
    element = self._element(element)
    self.driver.execute_script("arguments[0].scrollIntoView();", element)
    self.wait(1)
    actions = ActionChains(self.driver)
    actions.move_to_element(element)
    actions.click(element)
    actions.perform()
    self.wait(2)
    return self


  def sendKeys (self, element, keys):
    element = self._element(element)
    element.send_keys(keys)
    self.wait(2)
    return self

  def moveTo (self, element):
    element = self._element(element)
    ActionChains(self.driver).move_to_element(element).perform()
    self.wait(2)
    return self

  def browserKeys (self, keys):
    ActionChains(self.driver).send_keys(keys).perform()
    self.wait(2)
    return self

  def firstVisibleElement (self, xpath):
    result = None
    elements = self.driver.find_elements_by_xpath(xpath)
    for element in elements:
      if element.is_displayed():
        result = element
        break
    return result

  def clickSaveFile (self):
    userHome = os.path.expanduser("~")
    self.searchRectangle(userHome + '/option_save_file.png')
    self.searchRectangle(userHome + '/save_dialog.png')
    return self

  def selectFirstWindow (self):
    self.driver.switch_to.window(self.driver.window_handles[0])
    return self

  def wait (self, seconds=5):
    time.sleep(seconds)
    return self
