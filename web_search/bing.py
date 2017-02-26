import re
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import urllib2

from xml.sax.saxutils import unescape
from BeautifulSoup import BeautifulSoup

MAX_PAGES = 10


def search(query):
    """
    Query Bing and return text snippets
    :param query: the search query (key words separated by spaces)
    :return: text snippets containing the key words
    """

    results = []

    for i in range(MAX_PAGES):

        # Generate the query for the next page
        query = query.replace(' ', '%20')
        first = i * 10 + 1
        url = 'http://www.bing.com/search?q=%s&first=%d' % (query, first)

        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent' : user_agent}

        try:
            req = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(req)
            html = response.read()
            soup = BeautifulSoup(html)

        # No more pages
        except:
            break

        # Get the search results, clean the HTML and fix encoding issues
        snippets = [x.find('p') for x in soup.findAll('li', { 'class' : 'b_algo' })]
        results.extend(map(clean_html, snippets))

    return results


def clean_html(text):
    """
    Removes html tags, escape characters and weird encoding
    :param text: the html text
    :return: the clean text
    """
    text = re.sub(r'<.*?>', '', str(text))
    text = re.sub(r'[\x80-\xff]', '', text)
    text = unescape(text)
    return text