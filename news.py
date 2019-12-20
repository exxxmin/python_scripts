import requests
import bs4
import re
import time
import json

keywords = ['republican', 'GOP', 'grand old party', 'democratic', 'Republican', 'Grand Old Party', 'Democratic']

def get_refs_for_main_page():
    req = requests.get("https://www.foxnews.com/")
    if req.status_code != 200: 
        return {}
    soup = bs4.BeautifulSoup(req.text, features="lxml")
    cont = soup.findAll('div', attrs={'class':'main main-secondary'})
    refs = []
    ref_dict = {}
    for div in cont:
        refs += re.findall(r'<h2 class="title">(.*?)</h2>',str(div))
        for ref in refs:
            key = re.sub(r'<.*?>','', ref)
            val = re.findall(r'href="(.*?)"', ref)[0]
            ref_dict[key] = val    
    return ref_dict

    
def get_content_for_new(news_link:str):
    req = requests.get(news_link)
    if req.status_code != 200: 
        print("Status is "+str(req.status_code))
        return {}
    
    soup = bs4.BeautifulSoup(req.text, features="lxml")
    content_dict = {}

    if re.search('www.foxnews.com',news_link):        #we've got foxnews site
        cont = soup.findAll('div', attrs={'class':'article-body'})
        aucont = soup.findAll('div', attrs={'class':'author-byline'})
    elif re.search('insider.foxnews.com',news_link):  #we've got foxbusiness site
        cont = soup.findAll('div', attrs={'class':'articleBody'})
        aucont = []
    else:
        return {}

    paragraphs = []
    authors = []
    for div in cont:
        paragraphs += re.findall(r'<p.*?>(.*?)</p>',str(div))   
    for div in aucont:
        authors += re.findall(r'<span><a.*?>(.*?)</a>',str(div)) 
    if len(paragraphs):
        content_dict['content'] = ' '.join(paragraphs)
    if len(authors):
        content_dict['authors'] = ' '.join(authors)
    return content_dict

def validate_entry(entry:dict):
    global keywords
    title = entry.get('title')
    content = entry.get('content')
    if title == None or content == None:
        return False
    fit = False
    for keyword in keywords:
        if re.search(keyword,title):
            fit = True
        if re.search(keyword,content):
            fit = True
    return fit

def save_to_JSON(data, fname:str):
    with open(fname, 'w') as fp:
        json.dump(data, fp)
        
def load_from_JSON(fname:str):
    d = {}
    try:
        with open(fname, 'r') as fp:
            d = json.load(fp)
    except IOError:
        print("Unable to open "+fname+"... do nothing")
    finally:
        return d
    
if __name__ == '__main__':
    entries = load_from_JSON("foxnews_entries.json")
    filtered_entries = load_from_JSON("foxnews_entries_filtered.json")
    i = 1
    
    while 1:
        print("attempt #"+str(i))
        refs = get_refs_for_main_page()
        for entry_name, link in refs.items():
            if entries.get(link) == None:
                time.sleep(.5)
                print('Getting content for "'+entry_name+'"...')
                news = get_content_for_new(link)
                if len(news):
                    news['title'] = entry_name
                    entries[link] = news
                    if validate_entry(news):
                        filtered_entries[link] = news
                else:
                    entries[link] = {}
        save_to_JSON(entries, "foxnews_entries.json")
        save_to_JSON(filtered_entries, "foxnews_entries_filtered.json")
        print("attempt #"+str(i)+" finished\n")
        i+=1
        time.sleep(3600)