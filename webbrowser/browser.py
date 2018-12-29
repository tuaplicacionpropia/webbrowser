#!/usr/bin/env python2.7
#coding:utf-8

import re
import autopy
import requests
import shutil
import os
import time
import sys
import clipboard
import rarfile

from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import pyscreenshot
import cv2
import tempfile

#click problem
#https://stackoverflow.com/questions/11908249/debugging-element-is-not-clickable-at-point-error
#https://peter.sh/experiments/chromium-command-line-switches/#disable-popup-blocking
#http://toolsqa.com/selenium-webdriver/how-to-download-files-using-selenium/
#http://allselenium.info/file-downloads-python-selenium-webdriver/
#https://peter.sh/experiments/chromium-command-line-switches/#disable-popup-blocking
#https://stackoverflow.com/questions/23530399/chrome-web-driver-download-files
#https://stackoverflow.com/questions/18439851/how-can-i-download-a-file-on-a-click-event-using-selenium
#https://stackoverflow.com/questions/32205245/need-the-chrome-equivalent-of-these-firefox-browser-profile-settings-in-seleni

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
    self.params = {}

  def openUrl (self, start=None, autoSave=None, downloadDir=None, profile=None):
    firefoxDriverPath = '/home/jmramoss/selenium/chromedriver'
    chromeDriverPath = '/home/jmramoss/selenium/geckodriver'
    
    checkFirefox = False
    checkChrome = False
    if os.path.isfile(firefoxDriverPath):
      checkFirefox = True
    elif os.path.isfile(chromeDriverPath):
      checkChrome = True
    
    if checkFirefox:
      self.openFirefox(start, autoSave, downloadDir, profile)
    elif checkChrome:
      self.openChrome(start, autoSave, downloadDir)

    return self

  def openFirefox (self, start=None, autoSave=None, downloadDir=None, profile=None):
    driverPath = '/media/jmramoss/ALMACEN/bettenis/geckodriver'
    
    if downloadDir is None:
      downloadDir = tempfile.mkdtemp(prefix='.download_')

    options = None
    options = FirefoxOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--ignore-certificate-errors')
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
    
    fp = None
    if profile != None:
      #profile = '/home/jmramoss/.mozilla/firefox/wp4th1of.default'
      fp = webdriver.FirefoxProfile(profile)

    if fp != None and (autoSave != None or downloadDir != None):
      fp.set_preference("browser.download.folderList", 2)
      fp.set_preference("browser.download.manager.showWhenStarting", False)
      if downloadDir != None:
        # downloadDir = '/home/jmramoss/Descargas/mocks'
        fp.set_preference("browser.download.dir", downloadDir)
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
      driver.set_page_load_timeout(30)
      try:
        driver.get(start)
      except:
        print("timeout")

    if downloadDir != None:
      self.set_param("browser.download.dir", downloadDir)
    
    return self

  def openChrome (self, start=None, autoSave=None, downloadDir=None):
    driver_path = '/media/jmramoss/ALMACEN/bettenis/chromedriver'
    os.environ["webdriver.chrome.driver"] = driver_path

    if downloadDir is None:
      downloadDir = tempfile.mkdtemp(prefix='.download_')

    options = ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--ignore-certificate-errors')

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
      driver.set_page_load_timeout(30)
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
    print("numWindows = " + str(result))
    return result

  def closeLastWindow (self):
    numWindows = self.getNumWindows()
    self.closeWindow(numWindows - 1)
    return self

  def closeTab (self):
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

  def _element (self, element):
    result = None
    result = element
    if type(element) == type(""):
      result = self.driver.find_element_by_xpath(element)
    return result

  def debugHtml (self, element):
    element = self._element(element)
    html = element.get_attribute('innerHTML')
    html = u' '.join((html)).encode('utf-8').strip()
    print(str(html))
    return self

  def attr (self, element, name):
    result = None
    element = None
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
    element = self._element(element)
    self.driver.execute_script("arguments[0].scrollIntoView();", element)

  #http://internetculture.ovh/assets/biblioteca/Bevilacqua2.epub
  def downloadUrl(self, url, filename=None):
    result = None
    #url = element.get_attribute("href")
    print("downloading url = " + url)
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


  def fullscreenshot(self, target=None):
    print("Starting chrome full page screenshot workaround ...")


    total_width = self.driver.execute_script("return document.body.offsetWidth")
    total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = self.driver.execute_script("return document.body.clientWidth")
    viewport_height = self.driver.execute_script("return window.innerHeight")
    print("Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height,viewport_width,viewport_height))
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

        print("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
        rectangles.append((ii, i, top_width,top_height))

        ii = ii + viewport_width

      i = i + viewport_height

    stitched_image = Image.new('RGB', (total_width, total_height))
    previous = None
    part = 0

    for rectangle in rectangles:
      if not previous is None:
        self.driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
        print("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
        time.sleep(0.2)

      file_name = "part_{0}.png".format(part)
      print("Capturing {0} ...".format(file_name))

      self.driver.get_screenshot_as_file(file_name)
      screenshot = Image.open(file_name)

      if rectangle[1] + viewport_height > total_height:
        offset = (rectangle[0], total_height - viewport_height)
      else:
        offset = (rectangle[0], rectangle[1])

      print("Adding to stitched image with offset ({0}, {1})".format(offset[0],offset[1]))
      stitched_image.paste(screenshot, offset)

      del screenshot
      os.remove(file_name)
      part = part + 1
      previous = rectangle

    stitched_image.save(target)
    print("Finishing chrome full page screenshot workaround...")
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
    print("cmd = " + str(cmd))
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
      print('screenshot = ' + str(baseImg))
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
      print("topLeft = " + str(topLeft) + " botRight = " + str(botRight))
    return self

  def getDriver (self):
    return self.driver

  def click (self, element):
    element = self._element(element)
    element.click()
    self.wait(2)
    return self

  def clickVirtual (self, element):
    element = self._element(element)
    actions = ActionChains(self.driver)
    actions.move_to_element(element)
    actions.click()
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
    self.searchRectangle('/home/jmramoss/selenium/option_save_file.png')
    self.searchRectangle('/home/jmramoss/selenium/save_dialog.png')
    return self

  def selectFirstWindow (self):
    self.driver.switch_to.window(self.driver.window_handles[0])
    return self

  def wait (self, seconds=5):
    time.sleep(seconds)
    return self

