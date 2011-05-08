# grab a site's title

import urllib2
from BeautifulSoup import BeautifulSoup

def load(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())

    title = soup.find('title').contents[0]

    return title

def display(url):
    title = load(url)
    msg   = '%s: %s' % (url, title)

    return msg

