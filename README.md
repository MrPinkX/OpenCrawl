### Documentation
This is a webcrawler script written in python. The goal is that everyone could travel the web themselves. 

Several things - 
You could either add a brand new link or start from where you left of. First time you'd run the script it'd require you to provide a link - it'd create a DB file using sqlite3, to which it'll append all the webpages (referenced by the webpage you provide). It'll then proceed to do the same for them - each appended webpage will be scanned for URLs, content, title, and date of creation - all of which correspond to a single row. 

There is a machine learning model involved used to detect URLs likely referring to content pages such as news articles. The goal of course is to be able to query yourself whatever you crawled. This an ongoing work, naturally there might be issues. 

You could choose how many entries to add to the dataset, and how many pages to gather from each page. You could choose, as said, whether to begin the loop from a new link you provided, or from some existing point at the dataset. If you don't provide an answer to the first question it'll choose to start from an existing point, and you don't specify it it'd be the last entry in the dataset. 

---

Ultimately you'd want to pair it up with some frontend that'd allow for some discovery experiece. Till then you could just make your own queries. 
