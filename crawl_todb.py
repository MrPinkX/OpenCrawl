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

    print("getting initiated")
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
        print("Is article")


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
    return dic

rows = [tuple_todic(i) for i in cursor.fetchall()]
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



def crawl(start_point, amount_toappend):
    amount_added = 0

    increase = 1
    no_links_enteries = []

    index = start_point
    current_page = rows[index]

    while amount_added<amount_toappend:
        try:
            print(current_page.keys())
            row_links = eval(str(current_page['links']))
            existing_urls = [i['url'] for i in rows] 

            links_togo = set(row_links) - set(existing_urls)
            articles = [i for i in links_togo if is_url_articlesk(i)]
            if len(articles) < 1:
                no_links_enteries.append(index)
            
            print("\n")
            print("Retriving from: " + current_page["url"], "links: " + str(articles[0:5]))
            for i in articles: 
                print(" ")
                if amount_added > amount_toappend:
                    print("yes")
                    break
                try:
                    print("getting: " + str(i))
                    new_webpage = get_webpage_(i)
                    rows.append(new_webpage)
                    print("no")
                    retrival_time = datetime.now()
                    print("Got " + str(i))
                    command = "INSERT INTO enteries__ (base_url, url, title, content, links, source, article, retrival_time, c_date, index_row) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    cursor.execute(command, (str(new_webpage['base_url']), str(new_webpage['url']),str (new_webpage['title']), str(new_webpage['content']), str(new_webpage['links']), str(rows[index]['url']), str(new_webpage['article']), retrival_time, new_webpage['date'], len(rows) + amount_added))
                    conn.commit()
                    print(new_webpage['title'], "Added")
                    amount_added += 1 
                except Exception as e:
                    print(e, "###### url: {} ######".format(i))
        except Exception as e:
            print(e, " #### Entry: {} #######".format(rows[index]['url']))
        
        index += 1
        current_page = rows[index]

        print("index: ", index)

                        

    added = [i['url'] for i in rows[initial_length-1:(initial_length-1)+amount_added]]
    return ("\n", added, "Links added")





start_point = -1
while (start_point==-1):
    new_link = input("Provide a new link or start from somewhere in the dataset")
    if new_link:
        rows.append(get_webpage_(new_link))
        start_point = len(rows)-1
    else:
        if len(rows) > 0:
            start_point = input("Where to start? ") or len(rows)-1 



crawl(start_point, 30)

amount_toappend = input("How many new pages? ") or 1000 













