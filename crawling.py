import urllib2
import time
import re
import urlparse
import csv
import sys
import threading
SLEEP_TIME = 1


# download the html with specific retry nums and user_agent
def download(url, num_retry=2, user_agent='zhuangh7'):
    print 'download :', url
    header = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=header)  # create a header with user_agent
    try:
        html = urllib2.urlopen(request).read()  # open url with the specific request
    except urllib2.URLError as e:
        print 'download error :', e.reason
        html = None
        if (num_retry > 0):  # check the time for retry
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, num_retry - 1)
        else:
            print 'download false'
            return None
    print 'download succes'
    return html


# def crawl_sitemap(url, num_retry=2, user_agent='zhuangh7', find_what='(.*)'):
#     sitemap = download(url, num_retry, user_agent)
#     # extract the sitemap links
#     results = re.findall(find_what, sitemap)
#     # print results
#     print 'begin match'
#     if results == []:
#         print 'find no match !'
#     else:
#         for result in results:
#             print result
#

# my first callback (find the need infor and save to csv
class callback_1:
    def __init__(self):
        self.writer = csv.writer(open('huaji.csv', 'w'))
        self.fields = ('id', 'name', 'url')
        self.writer.writerow(self.fields)
        self.id = 0

    def __call__(self, html, url):
        if re.search('/view/', url):
            for link in get_palyer_links(html):
                print link
                if re.match('/player', link):
                    link = urlparse.urljoin('http://www.12yeye.com/',link)
                    htmln = download(link).decode('gb2312','ignore')
                    reload(sys)
                    sys.setdefaultencoding('utf-8')
                    results = re.findall('f:\'(http://.*?11bubu\.com/.*?)\'', htmln)
                    row = []
                    # print results
                    print 'begin match'
                    if results == []:
                        print 'find no match !'
                    else:
                        row.append(self.id)
                        self.id= self.id+1
                        a = re.findall('<title>(.*?)</title>',htmln)
                        if not a == []:
                            row.append(a.pop(0))
                        else:
                            row.append('title error')
                        row.append(results[0])
                        self.writer.writerow(row)
                        print 'save'
                        break;


# crawl_queue [] : the major queue for url and add the seed_url to the list
# seen {} : to save which url is saved and its depth
def link_sitemap(seed_url, num_retry=2, user_agent='zhuangh7', link_regex='(.*)', max_depth=2, scrape_callback=None):
    crawl_queue = [seed_url]
    seen = {seed_url: 0}
    while crawl_queue: # for the url in de main queue
        url = crawl_queue.pop()
        html = download(url, num_retry, user_agent) # download it
        if html: # if download success
            if scrape_callback:
                scrape_callback(html, url) # call back
            depth = seen[url] # get the depth of the url
            if depth != max_depth:
                for link in get_links(html):  # find all the links in the html of the url
                    if re.match(link_regex, link):  # if we need the link then add it to the major queue
                        link = urlparse.urljoin(seed_url, link)
                        if link not in seen:
                            seen[link] = depth + 1 # set the depth
                            crawl_queue.append(link)  # be avid to cramp the same sit


def get_links(html):
    # find all links in the given html
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


def get_palyer_links(html):
    webpage_regex = re.compile('<a href=(/player.*?) ', re.IGNORECASE) # create new compile
    return webpage_regex.findall(html) # set the compile to the html and get all results


def printHTML(html):
    # print html
    saveHTML(html)


def saveHTML(html):
    file = open('' + time.time().__int__().__str__() + '.html', 'w')
    file.write(html)
    file.close()
    print 'save'


if __name__ == '__main__':
    link_sitemap('http://www.12yeye.com/view/index6676.html', num_retry=2, user_agent='zhuangh7', link_regex='^(/view.{0,20}\.html)$',
                 max_depth=5, scrape_callback=callback_1())
