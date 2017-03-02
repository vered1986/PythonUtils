import re
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import math
import urllib2

from threading import Thread
from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

MAX_PAGES = 10
MAX_THREADS = 10


def search(query_words, max_pages=MAX_PAGES):
    """
    Query Bing News in English and return text snippets and titles along with their timestamps
    :param query_words: a list of key words to query
    :return: text snippets and titles along with their timestamps
    """

    threads = []
    results = {}
    query = '"' + '"+"'.join(query_words).replace(' ', '%20') + '"'

    # Run every MAX_THREADS in parallel
    runs = int(math.ceil(max_pages / MAX_THREADS))

    for run_index in range(runs):
        for page_index in range(run_index * MAX_THREADS, min((run_index + 1) * MAX_THREADS, max_pages)):

            # Generate the query for the next page
            first = page_index * 10 + 1
            url = 'http://www.bing.com/news/search?setmkt=en-US&q=%s&first=%d' % (query, first)

            # Create a new search thread and start it
            curr_url_reader = URLReader()
            url_opener = urllib2.build_opener(curr_url_reader)
            thread = Thread(target=url_opener.open, args=(url,))
            results[thread] = curr_url_reader
            thread.start()

            threads.append(thread)

        # Wait for all threads to complete
        for t in threads:
            t.join()

    results = [res for t in threads for res in results[t].results]
    return results


def clean_html(html):
    """
    Removes html tags, escape characters and weird encoding
    :param html: the html text
    :return: the clean text
    """
    soup = BeautifulSoup(html)

    # Remove style, image, links and script tags
    for tag in ['script', 'style', 'a', 'image']:
        [s.extract() for s in soup(tag)]

    # Get text
    text = ''.join(soup.findAll(text=True))

    # Space between escape characters
    text = re.sub('&', ' &', text)
    text = re.sub(';', '; ', text)

    # Encoding
    text = re.sub(r'(\\u[0-9A-Fa-f]+)', lambda matchobj: chr(int(matchobj.group(0)[2:], 16)), str(text))
    text = re.sub(r'[\x80-\xff]', '', text)

    # Remove tags and escape characters
    text = re.sub(r'<.*?>', '', text)
    text = HTMLParser().unescape(text)

    # Multiple spaces
    text = re.sub('\n+', '\n', text)
    text = re.sub('\s+', ' ', text).strip()

    return text


class URLReader(urllib2.HTTPHandler):

    def http_response(self, request, response):
        """
        Callback function to read the page content
        :param request: the request object
        :param response: the response object containing the HTML
        :return: sets self.results to contain the titles and snippets of the search results,
        along with their timestamps, and returns the response
        """

        self.results = []
        html = response.read()
        soup = BeautifulSoup(html)

        # Get the snippets and titles with timestamps
        # format: <div class="newsitem item cardcommon" url="[URL]">
        captions = [x.find('div', { 'class' : 'caption' })
                    for x in soup.findAll('div', { 'class' : 'newsitem item cardcommon' })]

        results = [(unicode(caption.find('div', { 'class' : 'snippet' })),
                    unicode(caption.find('a', { 'class' : 'title' })),
                    caption.find('div', { 'class' : 'source' }).find('span', { 'class' : 'timestamp' }).text)
                   for caption in captions]

        if len(results) > 0:
            snippets, titles, timespans = zip(*results)
            snippets = [clean_html(snippet[snippet.index('>') + 1 : -6]) for snippet in snippets]
            titles = [clean_html(title[title.index('>') + 1 : -4]) for title in titles]
            timespans = map(clean_html, timespans)
            self.results = zip(snippets, timespans) + zip(titles, timespans)

        return response
