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

#static dataql query
query = {
  "operationName": "vclInvestors",
  "variables": {
    "slug": "",
    "order": [
      {}
    ],
    "after": ""
  },
  "query": "query vclInvestors($slug: String!, $after: String) {\n  list(slug: $slug) {\n    id\n    slug\n    investor_count\n    vertical {\n      id\n      display_name\n      kind\n      __typename\n    }\n    location {\n      id\n      display_name\n      __typename\n    }\n    stage\n    firms {\n      id\n      name\n      slug\n      __typename\n    }\n    scored_investors(first: 8, after: $after) {\n      pageInfo {\n        hasNextPage\n        hasPreviousPage\n        endCursor\n        __typename\n      }\n      record_count\n      edges {\n        node {\n          ...investorListInvestorProfileFields\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment investorListInvestorProfileFields on InvestorProfile {\n  id\n  person {\n    id\n    first_name\n    last_name\n    name\n    slug\n    is_me\n    is_on_target_list\n    __typename\n  }\n  image_urls\n  position\n  min_investment\n  max_investment\n  target_investment\n  is_preferred_coinvestor\n  firm {\n    id\n    name\n    slug\n    __typename\n  }\n  investment_locations {\n    id\n    display_name\n    location_investor_list {\n      id\n      slug\n      __typename\n    }\n    __typename\n  }\n  investor_lists {\n    id\n    stage_name\n    slug\n    vertical {\n      id\n      display_name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"
}

#static headers for each request
headers = {
  'authority': 'signal-api.nfx.com',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'accept': '*/*',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
  'content-type': 'application/json',
  'origin': 'https://signal.nfx.com',
  'sec-fetch-site': 'same-site',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://signal.nfx.com/',
  'accept-language': 'en-US,en;q=0.9'
}

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

def get_article_page_links(slug):
    '''
    Get all the investor profile links from a slug
    Parameters: 
        * slug (string): end of a url
    Output: 
        * slugs (list) : all the links
    '''
    url = "https://signal-api.nfx.com/graphql"
    query["variables"]['slug'] = slug
    older_after = ''
    after = ''
    response = dict()
    count = 1
    first = True
    slugs = set()
    while ((older_after != after and after is not None) or first):
        print('Number of Load Mores:', count)
        print('Number of Slugs:', len(slugs))
        print('---------------')
        first = False
        try:
            query["variables"]['after'] = after
            payload = json.dumps(query)
            response_object = requests.request("POST", url, headers=headers, data=payload)
            response = response_object.json().copy()
            older_after = after[:]
            after = response['data']['list']['scored_investors']['pageInfo']['endCursor']
            edges = response['data']['list']["scored_investors"]["edges"]
        except Exception as e:
            print(e)
            continue
        
        for node in edges:
            slugs.add('https://signal.nfx.com/investors/' + node["node"]["person"]["slug"])
        count += 1
        time.sleep(random.randint(1, 4))
    return slugs

'''
def get_article_page_links(url):
    #without the load more
    try:
        page_html = get_html(url)
    except:
        print("Error with parsing:", url)
        return []
    links = []
    a_tags = page_html.findAll("a", {"class": "vc-search-card-name"})
    for link in a_tags:
        links.append('https://signal.nfx.com' + link.get('href'))
    return links
'''

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
        name = page_html.find("h1", {"class": "f3 f1-ns mv1"}).contents[0]
    except:
        name = ''
    
    #TYPE OF INVESTOR
    try:
        type = page_html.find("h3", {"class": "subheader white-subheader b pb1"}).find_all('span')[0].text
    except:
        type = ''
    
    #COMPANY AND TITLE
    try:
        title_company = page_html.find("h3", {"class": "subheader lower-subheader pb2"}).contents[0].replace(';', ',')
    except:
        title_company = ''
    
    #URL OF COMPANY
    try:
        company_url = page_html.find("a", {"class": "ml1 subheader lower-subheader"}).get('href')
    except:
        company_url = ''
    
    #LOCATION OF COMPANY
    try:
        location = page_html.find("span", {"class": "ml1"}).getText()
    except:
        location = ''
    
    #PERSON LINKEDIN
    try:
        socials = page_html.find_all("a", {"class": "iconlink", "rel": "dofollow noopener noreferrer", "target":"_blank"})
        linkedin = socials[1].get('href')
    except:
        linkedin = ''
    
    #NUMBER OF PEOPLE THAT RECOMMEND
    try:
        recommendation = page_html.find("div", {"class": "upvote-component"})
        recommendations = recommendation.find_all('span')[2].text
    except:
        recommendations = ''

    #NAME OF COMPANY, TITLE OF PERSON, INVESTMENT RANGE, NUMBER, FUND SIZE
    worked = True
    try:
        investments = page_html.find_all("span", {"class": "lh-solid"})
    except:
        worked = False
        investing_company = ''
        title_company = ''
        investment_range = ''
        num_investments = ''
        fund_size = ''

    if worked:
        try:
            investing_company_combined = str(investments[1])
    
            #name of company
            start_index = investing_company_combined.find('>') + 1
            end_index = investing_company_combined[1:].find('<') + 1
            investing_company = investing_company_combined[start_index:end_index]
            
            #title of person
            index = investing_company_combined[end_index:].find('</span>') + end_index + 15
            title_company = investing_company_combined[index:-7]
        except:
            investing_company = ''
            title_company = ''
        
        try:
            investment_range = investments[5].text
            num_investments = investments[7].text
            fund_size = investments[9].text
        except:
            investment_range = ''
            num_investments = ''
            fund_size = ''

    #INTERESTED IN CATEGORIES
    c_list = []
    try:
        categories = page_html.find_all("a", {"class": "vc-list-chip"})
        for category in categories:
            try:
                c_list.append(category.text)
            except:
                continue
    except:
        c_list = []

    #COMPANIES INVESTED IN
    investment_list = []
    try:
        table_body = page_html.find("tbody", {"class": "past-investments-table-body"})
        rows = table_body.find_all('tr')
        for row in rows:
            try:
                cols = row.find_all('td', {'class':"with-coinvestors"})
                invest_company_name = cols[0].find('a', {'rel':"nofollow noopener noreferrer", 'target':"_blank"}).getText()
                investment = cols[1].get_text(',').split(',')
                stage = investment[0]
                date = investment[1]
                round_size = investment[2]
                investment_dict = {
                    'invested_company_name' : invest_company_name,
                    'invested_company_stage' : stage, 
                    'invested_company_date' : date, 
                    'invested_company_round_size' : round_size
                }
                investment_list.append(investment_dict)
            except:
                continue
    except:
        investment_list = []

    dict_obj = {
        'name': name, 
        'number_upvotes': recommendations, 
        'type_of_investor': type,  
        'company_title': title_company, 
        'company_name': investing_company,
        'company_url': company_url, 
        'company_location': location, 
        'linkedin': linkedin, 
        'investment_sweet_spot': investment_range, 
        'num_investments' : num_investments, 
        'fund_size' : fund_size, 
        'interested_in_categories' : c_list, 
        'past_investments' : investment_list
        }
    return dict_obj

def get_all_links(filename):
    '''
    Get all the links from a file
    Parameters: 
        * filename (file): file of all links
    Output: 
        * linked (list) : all the links
    '''
    linked = set()
    with open(filename) as f:
        reader = csv.reader(f)
        link_list = list(reader)
    for link in link_list:
        linked.add(link[0])
    return list(linked)

def get_investor_information(investor_links):
    '''
    Main function to call to scrape
    Parameters: 
        * url_list (list): all the urls with investor lists to scrape
    Output: 
        * data (dict) : all the compiled information about all investors
    '''
    
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

'''
def save_csv(data, name):
    with open(name, 'w') as f:
        f.write("Name; Type of Investor; Title; Company; Recommendations; Company URL; Location of Company; Linkedin; Investment Sweet Spot; Number of Investments; Fund Size; Interested in Categories; Past Investments;\n")
        for investor in data:
            f.write("%s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s;\n" % (investor[0], investor[1], investor[2], investor[3], investor[4], investor[5], investor[6], investor[7], investor[8], investor[9], investor[10], investor[11], investor[12]))
'''

def save_json(data, name):
    '''
    save the dictionary of data as a json
    '''
    with open(name, 'w') as outfile:
        json.dump(data, outfile)

if __name__ == "__main__":
    file_name = 'slugs_2.csv'
    page_urls = get_all_links(file_name)
    data = get_investor_information(page_urls)
    save_json(data, 'signal_nfx_data_2.json')
    
    #print(page_urls)
    #link_list = get_investor_information(page_urls)
    #save_csv(link_list, "test_data.csv")
    #testing
    #url = 'https://signal.nfx.com/investors/jeff-clavier'
    #url = 'https://signal.nfx.com/investor-lists/top-advertising-series-a-investors'
    #page_urls = ['https://signal.nfx.com/investor-lists/top-marketplaces-seed-investors','https://signal.nfx.com/investor-lists/top-saas-seed-investors', 'https://signal.nfx.com/investor-lists/top-fintech-seed-investors', 'https://signal.nfx.com/investor-lists/top-enterprise-seed-investors']
    #page_urls = ['https://signal.nfx.com/investor-lists/top-autotech-seed-investors']
    #data = get_investor_information(page_urls)
    #save_json(data, 'test.json')