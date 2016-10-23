#!/usr/bin/env python

__author__      = "Taylor Cooper"
__copyright__   = "Copyright 2016, MistyWest"
__date___       = "2016.10.17"
__credits__ = ["Stackoverflow"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Taylor Cooper"
__email__ = "taylor@mistywest.com"
__status__ = "Proof of Concept"

"""scrapper.py: Scrape websites for profit.

This is an introductory paragraph that will explain things later if I feel like it

Example:
        Ask Taylor if you would like one of these:

Attributes:
    module_level_variable1 (int): Not certain what this would be used for.

Todo:
    * Make it work

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import string, time
import pickle
from BeautifulSoup import BeautifulSoup
import requests
import nltk
from stop_words import get_stop_words

class scrapedData(object): # Inherit object to be picklable

    def __init__(self, name, domain, words, companyDesc='', companyType='', companySize='', totalRevenueToDate=0,
                 wordQuality=5, URLs=[]):
        """  This is a class to store data scrapped from websites for pickling
        :param name:  string Name of company or word list
        :param name:  string for domain of site, for example 'dustfree.com'
        :param words: List of words (strings)
        :param companyDesc: String for describing company
        :param companyType: One of: ['Software','Hardware', 'Mixed', 'Lab']
        :param companySize: One of: ['Startup', 'Small', 'Medium', 'Large']
        :param totalRevenueToDate: Integer value of all business from this client (or group of clients)
        :param wordQuality: int [1-10] User estimate of the quality of data recovered
        :param URLs: List of urls (strings)
        :return: Nothing
        """

        # Variables, not checking any of this btw
        self.name = name
        self.domain = domain
        self.words = words
        self.companyDesc = companyDesc
        self.companyType = companyType
        self.companySize = companySize
        self.totalRevenueToDate = totalRevenueToDate
        self.wordQuality = wordQuality
        self.urls = URLs

class scrappyMcScraperson():

    def __init__(self):
        """ Initialize a class for scrapping target URLs for words of interest
        :return: nothing
        """

        self.ignoreChars = []
        self.ignoreWords = []
        self.stop_words = get_stop_words('en')

        # Lines all n these files must include an endline char
        with open('ignoreChars.txt') as f:
            for l in f.readlines():
                self.ignoreChars.append(l[:-1])
        with open('ignoreWords.txt') as f:
            for l in f.readlines():
                self.ignoreWords.append(l[:-1])

        self.ignoreWords = self.ignoreWords + self.stop_words


    def sanitizeWords(self, words):
        """ Sanitize words to remove junk content from a list of strings
        :param words:  List of words (strings)
        :return: Sanitized list of words
        """

        sWords = []
        for w in words:
            number = True
            ignoreChar = False

            try: # Ignore numbers
                x = int(w)
            except ValueError:
                number = False

            for c in self.ignoreChars:  # Ignore words that contain these characters
                if c in w:
                    ignoreChar = True

            # Confirm characters in word are alpha and lower case
            wTemp = ''
            for c in w:
                if c.isalpha():
                    wTemp = wTemp + c.lower()
            w = wTemp

            if number: continue
            if ignoreChar: continue

            if w not in self.ignoreWords:  # Confirm word is not a stop_word or on the ignore list
                    # Iterate through each char in w to see if it's printable, ignore if not printable
                    w = filter(lambda x: x in string.printable, w)
                    sWords.append(w)

        return sWords

    def getLinks(self, domain):
        """  Get all the links, that end in domain, on the main page of the domain
        :param domain: Specify the domain we're searching for URLS
        :return:
        """
        url = 'http://' + domain
        try:
            page = requests.get(url, timeout=5)
            print 'Search for links at: ' + url
        except requests.exceptions.ReadTimeout:
            print 'Connection timeout for: ' + url
            return

        soup = BeautifulSoup(page.text)
        linkSoup = soup.findAll('a')
        links =[]

        for tag in linkSoup:
            link = tag.get('href', None)
            if link is not None:
                if not ( link.startswith('http://') or link.startswith('https://') ):
                    link= url + link
                if domain in link:
                    links.append(link)
                    print 'Found: ' + link

        return set(links) # Set returns the unique set of links


    def getWords(self, URLs, delay=1):
        """ Pull words from target URLs
        :param URLs: List of URLs for scrapping
        :return: A list of words found
        """
        words = []

        for url in URLs:

            tknzr = nltk.tokenize.WordPunctTokenizer()
            self.printWords(words)

            time.sleep(delay) # Let's be polite and wait a bit before pulling data again

            # Get page, make soup, select tokenizer
            try:
                page = requests.get(url, timeout=5)
                print 'Getting: ' + url
            except requests.exceptions.ReadTimeout:
                print 'Connection timeout for: ' + url
                continue

            soup = BeautifulSoup(page.text)

            for n in soup.findAll("meta"):
                wordsMeta = []
                if n.get("name") == "keywords":
                    wordsMeta = tknzr.tokenize(str(n))
                if n.get("name") == "description":
                    wordsMeta = tknzr.tokenize(str(n))
                if n.get("property") == "og:description":
                    wordsMeta = tknzr.tokenize(str(n))
                if n.get("itemprop") == "description":
                    wordsMeta = tknzr.tokenize(str(n))
                for w in wordsMeta:
                    words.append(w)

            for n in soup.findAll("p"):
                wordsPara = tknzr.tokenize(str(n))
                if 'if gte mso 9' in n.text: # It is possible to get dumped on by Fatigue Science without this
                    continue
                for w in wordsPara:
                    w = w.decode('ascii','ignore')
                    words.append(w)

        return words


    def getFrequencies(self, words):
        """ Return word frequencies for an list of words
        :param words: A list of words (strings)
        :return: nltk.FreqDist, a frequency distribution object
        """

        fdist = nltk.FreqDist(words)
        #print fdist.most_common(50)
        #print len(words)
        return fdist

    def printWords(self, words, n=10):
        """ Prints a list of words nicely
        :param words: A list of words (strings)
        :param n: Words per line
        :return: Nothing
        """
        i = 0
        for w in words:
            if i == n:
                print '\n'
                i = 0
            else:
                i += 1
                print w+', ',

    def plotWorks(self, words):
        """  Ideally this thing creates some kind of informative plot...
        :param words: A list of words (strings)
        :return:
        """

if __name__ == "__main__":
    # Scrap it and dump it
    smcs = scrappyMcScraperson()
    # Fields for website
    name = 'FatigueScience'
    path = './pkl/'+name+'.pkl'
    domain = 'fatiguescience.com'
    companyDesc = 'Fatigue monitoring wrist band'
    companyType = 'Mixed' #['Software','Hardware', 'Mixed', 'Lab']
    companySize = 'Small' #['Startup', 'Small', 'Medium', 'Large']
    totalRevenueToDate = 330000
    wordQuality = 7 # 1-10


    # Pull data
    if True:
        links = smcs.getLinks(domain)
        #links = ['http://www.fatiguescience.com']
        words = smcs.getWords(links, delay=65)
        words = smcs.sanitizeWords(words)
        smcs.printWords(words, n=12)

        print ''
        print ''
        print 'Saving to: ' + path
        sd = scrapedData(name, domain, words, companyDesc, companyType, companySize, totalRevenueToDate, wordQuality, links)
        pickle.dump(sd, open(path, 'wb'))

    # Read data
    if False:
        sd2 = pickle.load(open(path, 'rb'))
        print sd2.name
        print sd2.companyDesc
        for w in sd2.words: print w
        for u in sd2.urls: print u

    # fd = nltk.FreqDist(sd2.words)
    # fd.plot(50,cumulative=False)

    #smcs.printWords(wSane)
    #fSane = smcs.getFrequencies(wSane)
    # print fSane.most_common(10)
    # not sure how to iterate this

    # DustFree
    name = 'Dustfree'
    domain = 'dustfree.com'
    companyDesc = 'UV Air quality'
    companyType = 'Hardware' #['Software','Hardware', 'Mixed', 'Lab']
    companySize = 'Small' #['Startup', 'Small', 'Medium', 'Large']
    totalRevenueToDate = 81500
    wordQuality = 8 # 1-10

    # Fields for website
    name = 'IntelLabs'
    domain = 'intel.eu'
    companyDesc = 'Research division of Intel'
    companyType = 'Lab' #['Software','Hardware', 'Mixed', 'Lab']
    companySize = 'Large' #['Startup', 'Small', 'Medium', 'Large']
    totalRevenueToDate = 379185
    wordQuality = 7 # 1-10
    URLs = ['http://www.intel.eu/content/www/eu/en/research/research-areas/intel-labs-research-areas.html']