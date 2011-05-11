#!/usr/bin/env python
# grab a site's title
# TODO: add error checking to display()

import BeautifulSoup
import sys
import urllib2

def load(url):
    try:
        soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(url).read())
        title = str(soup.find('title').contents[0])
    except BeautifulSoup.HTMLParseError, e:
        print 'HTML parser error:', str(e)
        title = None
    except urllib2.HTTPError, e:
        title = e.getcode()

    return title

def display(url):
    title = load(url)

    if type(title) == type(str()):  
        msg = '%s: %s' % (url, title)
    elif type(title) == type(int()):  
        msg = '%s returned HTTP error %d' % (url, title)
    else:     
        msg   = 'failed to load title for %s' % url

    return msg

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print display(sys.argv[1])

