'''
If you want to scrape from https://investorhunt.co/investors/, run this file!
'''

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

def get_page_links(url):
    #without the load more
    try:
        page_html = get_html(url)
    except:
        print("Error with parsing:", url)
        return []
    links = []
    #<a class="button is-dark" style="margin:auto; text-align:center" href="/investors/adam-stoll">More Details</a>
    a_tags = page_html.findAll("a", {"class": "button is-dark", "style" : "margin:auto; text-align:center"})
    for link in a_tags:
        links.append('https://investorhunt.co' + link.get('href'))
    print(links)
    return links

def get_investor_data(url):
    '''
    Get one investor's data
    Parameters: 
        * url (string): url to the investor profile on website
    Output: 
        * dict_obj (dict) : compiled information about the investor
    '''

    #get the html for the url
    page_html = get_html(url)
    
    #NAME
    try:
        name = page_html.find("h1", {"class": "title", "style": "color:white"}).text.strip()
    except:
        name = ''
    
    #LINKEDIN
    try:
        socials = page_html.find_all("div", {"class": "container"})[1].find_all('a')
        company_url  = socials[0].get('href')
        linkedin = socials[1].get('href')
        twitter = socials[2].get('href')
    except:
        linkedin = ''

    #LOCATION
    try:
        information = page_html.find_all("article", {"class": "tile is-child notification is-light"})
        locations = information[0].find_all('a')
        location = ''
        for place in locations:
            location = location + place.text + ';'
    except:
        location = ''
    
    #CATEGORIES
    try:
        information = page_html.find_all("article", {"class": "tile is-child notification is-light"})
        markets = information[1].find_all('a')
        c_list = []
        for industry in markets:
            c_list.append(industry.text)
    except:
        c_list = []
    
    #INVESTMENT INFORMATION
    try:
        information = page_html.find_all("article", {"class": "tile is-child notification is-light"})
        investment = information[2].find_all('p')
        num_investments = investment[0].text[18:].strip().split(' ')[0]
        investment_range = investment[1].text[19:].strip()
    except:
        num_investments = ''
        investment_range = ''
    
    #INVESTMENT LIST
    try:
        information = page_html.find_all("article", {"class": "tile is-child notification is-light"})
        investment_list = []
        for i in range(3, len(information)):
            investment_dict = {
                'invested_company_name' : information[i].text.strip().split('\n')[0],
                'invested_company_stage' : '', 
                'invested_company_date' : '', 
                'invested_company_round_size' : ''
            }
            investment_list.append(investment_dict)
    except:
        investment_list = []
    
    #TYPE OF INVESTOR
    type = 'Angel'
     
    title_company = ''
    location = ''
    recommendations = ''
    investing_company = ''
    fund_size = ''

    dict_obj = {
        'name': name, 
        'number_upvotes': recommendations, 
        'type_of_investor': type,  
        'company_title': title_company, 
        'company_name': investing_company,
        'company_url': company_url, 
        'company_location': location, 
        'linkedin': linkedin, 
        'twitter': twitter,
        'investment_sweet_spot': investment_range, 
        'num_investments' : num_investments, 
        'fund_size' : fund_size, 
        'interested_in_categories' : c_list, 
        'past_investments' : investment_list
        }

    return dict_obj

def get_investor_information():
    '''
    Main function to call to scrape
    
    Output: 
        * data (dict) : all the compiled information about all investors
    '''

    #get all the slugs of the investors
    investor_links = set()
    for i in range(1, 1783):
        url = 'https://investorhunt.co/investors/?page=' + str(i)
        print(i, url)
        try:
            links = get_page_links(url)
            investor_links = investor_links.union(set(links))
        except:
            continue
        #delay
        time.sleep(random.randint(5, 10))
    
    save_csv(investor_links, 'investor_links.csv')
    data = {}
    data['investors'] = []
    
    #get all the information about all the investors
    for i, link in enumerate(investor_links):
        print(i, link)
        try:
            data['investors'].append(get_investor_data(link))
        except:
            continue
        time.sleep(random.randint(5, 15))
    return data

def save_json(data, name):
    '''
    save the dictionary of data as a json
    '''
    with open(name, 'w') as outfile:
        json.dump(data, outfile)

def save_csv(data, name):
    with open(name, 'w') as f:
        f.write("Links;\n")
        for investor in data:
            f.write("%s;\n" % (investor,))

if __name__ == "__main__":
    data = get_investor_information()
    save_json(data, 'investorhunt.json')