from bs4 import BeautifulSoup as bs
import requests as r

import time 
from  datetime import datetime

now = datetime.now()
print("Current date and time: ", now)


def get_urlbase(url):
    try:
        if 'https' in url:
            return "https://" + url.split('/')[2]
        else:
            return url.split('/')[0]
    except:
        print('url')




import re 
def is_url_article(url): 
    if re.findall("\d{4}/", url): 
        return "True"
    return "False"



import re 
from datetime import datetime 

def get_date_from_page(soup):
    pub_date_titles = ["datePublished"]
    date_element = ''
    for i in pub_date_titles:
        date_element = re.search(i, str(soup))
        if date_element:
            break 

    if date_element: 
        range_date = str(soup)[date_element.span()[0]:date_element.span()[0]+100]
        print("found official date")
    else:
        range_date = str(soup)

    date_str_patterns = ["\d{4}[-.\/]\d{0,2}[-.\/]\d{2}", "\d{2}[-.\/]\d{0,2}[-.\/]\d{4}", "[A-z]{0,8} \d{0,2}, \d{4}"]
    date_ = [re.findall(i, range_date) for i in date_str_patterns][0][0]
    print(date_)


    dformat = ["%b-%d-%Y", "%B-%d-%Y", "%Y-%d-%m", "%Y-%m-%d"]
    for d in dformat:
        try: 
            date_ = datetime.strptime(date_, d)
            return date_
        except Exception as e:
            None
            # print(e)
    return date_




def get_webpage_(url): 

    print("getting initiated for ", url)
    response = r.get(url)
    print("got response")

    soup = bs(response.content)
    print("got soup")

    links = soup.find_all('a') 
    texts = soup.find_all('p')


    links_ = []
    content = ''

    try:
        title = soup.title.string.strip()
    except:
        title = url

    

    base_url = get_urlbase(url)
    
    for i in links: 
        if 'http' in str(i.get('href')):
            links_.append(str(i.get('href')))
        elif '/' in str(i.get('href')):
            links_.append(base_url + str(i.get('href')))

    for i in texts:
        content += i.get_text(separator='\n', strip=True) 

    article_ = False

    
    try:
        date = get_date_from_page(soup) 
    except Exception as e:
        print(e, "Couldn't retrive date")
        date = "Null_"


    if type(date) == list:
        date = date[0][0]

    if (len(texts) > 20) or is_url_article(url):
        article_ = True


    page = {'title': title, 'base_url': base_url, 'url': url, 'content': content, 'links': links_, 'article':article_, "date": date}
    return page 


import sqlite3 


conn = sqlite3.connect('enteries___.db')
cursor = conn.cursor()



cursor.execute('''CREATE TABLE IF NOT EXISTS enteries__ (
    title VARCHAR,
    base_url VARCHAR,
    url VARCHAR,
    content VARCHAR,
    links VARCHAR,
    article VARCHAR,
    date VARCHAR, 
    source VARCHAR, 
    retrival_time VARCHAR, 
    c_date VARCHAR,
    index_row VARCHAR
    );''')


cursor.execute('SELECT * FROM enteries__')


conn.commit()



def tuple_todic(tup):
    dic = {}
    dic['url'] = tup[2]
    dic['title'] = tup[0]
    dic['content'] = tup[3]
    dic['links'] = tup[4]
    dic['base_url'] = tup[1]
    return dic

rows = [tuple_todic(i) for i in cursor.fetchall()]
# Fetch current crawl 
initial_length = len(rows)



# rows.append(get_webpage_("https://www.economist.com/"))

import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
loaded_vectorizer = joblib.load('./machine_models/model/vectorizer4.joblib')
loaded_clf = joblib.load('./machine_models/model/naive_bayes_model4.joblib')


def is_url_articlesk(url):
    url_counts = loaded_vectorizer.transform([url])
    prediction = loaded_clf.predict(url_counts)
    if prediction[0] == "non article":
        return False 
    
    return True







def crawl(total_amount=20, single_entry_amount=10, pages_per_base=10): 
    amount_added = 0

    bases_crawled = {}

    index = len(rows)-1
    print(index)
    while amount_added<total_amount:

        links_togo = []
        while len(links_togo) < 1:
            entry = rows[index]
            # All referenced URLs of a single entry
            if type(entry["links"]) == str:
                entry_links = eval(entry["links"])
            else:
                entry_links = entry["links"]

            # Only those not in the database 
            links_togo = set(entry_links) - set([i['url'] for i in rows])

            # Only those likely referring to an article
            links_togo = [i for i in links_togo if is_url_articlesk(i)]
            index -= 1


        retrived_from_entry = 0
        print("Retriving pages from: ", entry["title"])
        # Retrive webpages from a single entry 
        for link in links_togo:
            if retrived_from_entry > single_entry_amount:
                break

            # Limits amount of gathered pages per base
            url_base = get_urlbase(link)
            if url_base in bases_crawled:
                if bases_crawled[url_base] < pages_per_base:
                    bases_crawled[url_base] += 1 
            else:
                bases_crawled[url_base] = 1
            
            # Retrieve webpage only if we've crawled less then this or that amount of pages of it's base
            if bases_crawled[url_base] < pages_per_base:
                try: 
                    # Get webpage
                    webpage = get_webpage_(link) 
                    rows.append(webpage) 
                    amount_added += 1 
                    retrived_from_entry += 1

                    # Append to DataBase
                    retrival_time = datetime.now()
                    command = "INSERT INTO enteries__ (base_url, url, title, content, links, source, article, retrival_time, c_date, index_row) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    cursor.execute(command, (str(webpage['base_url']), str(webpage['url']),str (webpage['title']), str(webpage['content']), str(webpage['links']), str(rows[index]['url']), str(webpage['article']), retrival_time, webpage['date'], len(rows) + amount_added))
                    conn.commit()

                    # Show what's going on 
                    print(webpage['title'], "added") 
                    print(retrived_from_entry, "out of ", single_entry_amount, "for that entry")
                    print(bases_crawled[url_base], "out of ", pages_per_base, "for that base")
                    print(amount_added, "out of ", total_amount, "total")
                    print(url_base)
                    print(bases_crawled)
                    print('\n')

                except Exception as e:
                    bases_crawled[url_base] -= 1
                    print(e, link)
        print("\n")
    index += 1
            


    
crawl(150)
# print(rows)




















