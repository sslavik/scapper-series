from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import json
#Mongo
from dotenv import dotenv_values
from pymongo import MongoClient

#ENV Values
env = dotenv_values('.env')

xpathSeries = '//article[@class="TPost B"]/a'
xpathSeasons = '//div[@class="Title"]/a'
xpathMaxPages = '(//a[@class="page-link"])[last()]'
xpathEpisodes = '//td[@class="MvTbPly"]/a'
xpathButtonOptions = '(//button[@class="bstd Button"]/i[@class="fa-chevron-down"])'
xpathButtonFirstOption = '(//button[@class="bstd Button"]/i[@class="fa-chevron-down"])[position() = 1]'
xpathFirstListOptions = '((//button[@class="bstd Button on"])[position() = 1]//div[@class="Button sgty"])[position() = 1]'
xpathListOptions = '((//button[@class="bstd Button on"])//div[@class="Button sgty"])'
xpathIframeVideo = '//div[@class="Video on"]/iframe'
xpathTitleEpisode = '//h1[@class="Title"]'
xpathButtonLangText = '//button[@class="bstd Button on"]/span'
xpathLastPageOfSeries = '(//div[@class="nav-links"]/a)[last()]'
xpathCurrentPageNum = '//div[@class="nav-links"]/a[@class="page-numbers current"]'

DOMAIN_OF_PAGE = "pelisflix.one"
TIMEOUT = 10
f = open('pelisflix'+datetime.today().strftime('%Y-%m-%d%H-%M-%S')+'.csv', 'x')
driver = webdriver.Chrome()
driver.get("https://pelisflix.one/series-online/")
urlsOfSeries = []
urlsOfSeasons = []
urlsOfEpisodes = []
currentPage = 0
lastPage = 0
languageText = ""
lastSerie = ""
lastSeason = ""
lastEpisode = ""
lastOption = ""

# Methods

# This method waits all the elements an expected Locator

def checkForActualPage():
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[0])

# Save the info in config case of FAIL

def saveDataInConfig():
    with open('config.json', 'r') as f:
        config = json.load(f)

    #edit the data
    config['lastEpisode'] = lastEpisode
    config['lastSeason'] = lastSeason
    config['lastSerie'] = lastSerie
    config['lastOption'] = lastOption

    #write it back to the file
    with open('config.json', 'w') as f:
        json.dump(config, f)

def finishIfTheLastEpisodeInList(currentSeason, currentEpisode):
    if (currentPage == lastPage and currentSeason == lastSeason and currentEpisode == lastEpisode):
        with open('config.json', 'r') as f:
            config = json.load(f)

        #edit the data
        config['lastEpisode'] = ""
        config['lastSeason'] = ""
        config['lastSerie'] = ""
        config['lastOption'] = ""

        #write it back to the file
        with open('config.json', 'w') as f:
            json.dump(config, f)

def waitForAllElements(locator, timeout=None):
    WebDriverWait(driver, timeout if timeout != None else TIMEOUT).until(
        EC.presence_of_all_elements_located(locator))


def waitForElement(locator):
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located(locator))



def getIFrameUrl():
    waitForElement((By.XPATH, xpathIframeVideo))
    titleElm = driver.find_element(By.XPATH, xpathTitleEpisode)
    videoFrame = driver.find_element(By.XPATH, xpathIframeVideo)
    f.write(titleElm.text + ', ' + languageText + ', ' + videoFrame.get_attribute('src')+'\n')
    f.flush()


def goToEpisode(url):
    driver.get(url)

    WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, xpathButtonOptions)))
    btnsLng = driver.find_elements(By.XPATH, xpathButtonOptions)
    for btn in btnsLng:
        btn.click()

        time.sleep(3)

        checkForActualPage()

        languageText = driver.find_element(By.XPATH, xpathButtonLangText).text


        WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, xpathListOptions)))
        btnsLngOpt = driver.find_elements(By.XPATH, xpathListOptions)

        for btnOpt in btnsLngOpt:
            btnOpt.click()

            time.sleep(3)

            checkForActualPage() 

            getIFrameUrl()
            
            #Save the last Episode
            saveDataInConfig()

            #Before end the For we need to reopen de List

            btn.click()

            time.sleep(3)

            checkForActualPage()


    time.sleep(3)


def goToSeason(url):
    driver.get(url)
    waitForAllElements((By.XPATH, xpathEpisodes))
    listEpisodes = driver.find_elements(By.XPATH, xpathEpisodes)

    urlsOfEpisodes.clear()

    for elm in listEpisodes:
        urlsOfEpisodes.append(elm.get_attribute('href'))

    for episode in urlsOfEpisodes:
        lastEpisode = episode
        goToEpisode(episode)
        saveDataInConfig()



def goToSerie(url):
    driver.get(url)
    waitForAllElements((By.XPATH, xpathSeasons))
    seasons = driver.find_elements(By.XPATH, xpathSeasons)

    urlsOfSeasons.clear()

    for elm in seasons:
        urlsOfSeasons.append(elm.get_attribute('href'))

    for season in urlsOfSeasons:
        lastSeason = season
        goToSeason(season)
        saveDataInConfig()


try:
    waitForAllElements((By.XPATH, xpathSeries))

    lastPageElm = driver.find_element(By.XPATH, xpathLastPageOfSeries)
    lastPage = lastPageElm.text

    listSeries = driver.find_elements(By.XPATH, xpathSeries)
    maxPages = driver.find_element(
        By.XPATH, xpathMaxPages).get_attribute('href')
    for elm in listSeries:
        urlsOfSeries.append(elm.get_attribute("href"))

    for serie in urlsOfSeries:
        lastSerie = serie
        currentPageElm = driver.find_element(By.XPATH, xpathCurrentPageNum)
        currentPage = currentPageElm.text
        goToSerie(serie)
        saveDataInConfig()

except:
    saveDataInConfig()

finally:
    #TODO Close driver after Exception or Try, uncommet it
    #driver.close()
    f.close()
