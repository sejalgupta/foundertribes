from bs4 import BeautifulSoup
import urllib.request,sys,time
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import requests
import pandas as pd
import csv

def get_html(url):
    try:
        req = Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        page_soup = BeautifulSoup(webpage, "html.parser")
    except:
        print("Error with parsing:", url)
    
    return page_soup

def get_article_page_links(url):
    try:
        page_html = get_html(url)
    except:
        print("Error with parsing:", url)
        return []
    #links = []
    links = {}
    for link in page_html.findAll('a'):
        try:
            url = link.get('href')
            if url.startswith('https://') or url.startswith('http://') or url.startswith('www.'):
                add = True
                for keyword in ['bench', 'facebook', 'instagram', 'twitter']:
                    if keyword in url:
                        add = False
            if add:
                domain = urlparse(url).netloc.lower()
                if domain[0] != 'w':
                    domain = 'www.' + domain
                links[domain] = url
        except:
            continue
    return links

def save_csv(save_dict, name):
    with open(name, 'w') as f:
        f.write("Name; Article Link;\n")
        for key in save_dict.keys():
            f.write("%s; %s;\n" % (key, save_dict[key]))

if __name__ == "__main__":
    page_url = 'https://bench.co/blog/operations/small-business-grants/'
    link_dict = get_article_page_links(page_url)
    save_csv(link_dict, "grant_links.csv")