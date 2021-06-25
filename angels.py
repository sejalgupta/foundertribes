from bs4 import BeautifulSoup
import urllib.request,sys,time
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import requests
import pandas as pd
import csv
import time
import random
import requests
import json

def get_html(url):
    '''
    Get HTML of a singular url
    '''
    try:
        req = Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        page_soup = BeautifulSoup(webpage, "html.parser")
    except Exception as e:
        print("Error with parsing:", url)
        print(e)
    
    return page_soup

def get_links():
    url = 'https://www.angelinvestmentnetwork.us/find-investors/'
    pages_list = [url] 
    #for i in range(2, 2):
    for i in range(2, 3116):
        pages_list.append(url + str(i) + '/')
    return pages_list

def get_page_links(url):
    '''
    Get all the investor profile links from a slug
    Parameters: 
        * url (string):
    Output: 
        * url_list (list) : all the links
    '''
    try:
        page_html = get_html(url)
    except:
        print("Error with parsing:", url)
        return []
    a_tags = page_html.findAll("a", {"class": "btn btn-default", "target": "_blank"})
    links = []
    for tag in a_tags:
        links.append(tag.get('href'))
    return links

def get_investor_data(url):
    try:
        page_html = get_html(url)
    except:
        print("Error with parsing:", url)
        return []
    
    try:
        name = page_html.find("h2", {"class": "title-mr-40"}).text.strip()
    except:
        name = ''
    
    try:
        content = page_html.find('p', {"class": "location"})
        raw = str(content.contents[2])
        start_index = raw.find('>') + 1
        end_index = raw[start_index:].find('<')
        location = raw[start_index:start_index + end_index].strip() + ' ' + str(content.contents[3]).strip()
    except:
        location = ''

    try:
        type = page_html.find('div', {'id': "js-investor-type"}).text.strip()
    except:
        type = ''
    
    try:
        min_investment = page_html.find('div', {'id': "js-min-investment"}).text.strip()
    except:
        min_investment = ''

    try:
        max_investment = page_html.find('div', {'id': "js-max-investment"}).text.strip()
    except:
        max_investment = ''

    try:
        stages = page_html.find('div', {'class': "list-inline js-stagelist"}).text.strip()
    except:
        stages = ''

    try:
        industries = page_html.find('div', {'class': "col-lg-8 col-md-8 col-sm-5 col-xs-12 js-industrylist"}).text.strip()
    except:
        industries = ''
    
    try:
        cities = page_html.find('div', {'class': "col-lg-8 col-md-8 col-sm-5 col-xs-12 js-locationlist"}).text.strip()
    except:
        cities = ''

    try:
        countries = page_html.find('div', {'class': "col-lg-8 col-md-8 col-sm-5 col-xs-12 js-countriesList"}).text.strip()
    except:
        countries = ''


    investment = {
        'minimum': min_investment,
        'maximum': max_investment,
        'startup_funding_stages': stages,
        'industries': industries,
        'startup_cities': cities,
        'startup_countries': countries
    }

    dict_object = {
        'name' : name,
        'type' : type,
        'location': location,
        'investment_information' : [investment]
    }

    return dict_object

def get_data():
    '''
    Get investor data
    '''
    investor_links = set()
    for i, url in enumerate(get_links()):
        print(i, url)
        links = get_page_links(url)
        investor_links = investor_links.union(set(links))
        #delay
        time.sleep(random.randint(1, 5))
    
    data = {}
    data['angels'] = []
    for i, url in enumerate(investor_links):
        print(i, url)
        data['angels'].append(get_investor_data(url))
        #delay
        time.sleep(random.randint(1, 5))
    
    return data

def save_json(data, name):
    '''
    save the dictionary of data as a json
    '''
    with open(name, 'w') as outfile:
        json.dump(data, outfile)

if __name__ == "__main__":
    data = get_data()
    save_json(data, 'angels.json')