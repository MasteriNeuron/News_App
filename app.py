from flask import Flask, render_template,request,session, redirect, url_for
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
from pymongo import MongoClient
import pandas as pd
import pathlib
import textwrap
import os

import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown


app = Flask(__name__)

@app.route("/")
def login():
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')


#you can use this too

import sys
sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

GOOGLE_API_KEY  = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)



# Connect to MongoDB
client = MongoClient('mongodb+srv://master:!!master@atlascluster.w0iwrbk.mongodb.net/?retryWrites=true&w=majority')
db = client['client_database']  # Replace 'client_database' with your database name
collection = db['users']  # Replace 'users' with your collection name


# Assume your existing code for scraping and processing goes here
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
search="latest-news"
# fetch the search results page
response = requests.get(f"https://www.livemint.com/"+search)

# parse the HTML using BeautifulSoup
soup = bs(response.content, "html.parser")
n1=soup.find_all('div', {'id': "listview"})
reviews=[]

for i in n1:
    r=i.find_all('div',{'class':"listingNew clearfix impression-candidate ga-tracking"})
    for j in r:
        link = j.find('a')
        href_value = "https://www.livemint.com"+link['href']
        h2_tag=j.find("h2",{'class':"headline"})
        text_content = h2_tag.get_text(strip=True)
                # Extract the Updated time
        updated_time_span = j.find('span', {'class': 'fl date'})
        updated_time = updated_time_span.find('span', {'data-expandedtime': True}).get('data-expandedtime')

        
                # fetch the search results page
        response2 = requests.get(href_value)
        # parse the HTML using BeautifulSoup
        soup2 = bs(response2.content, "html.parser")
        p1=soup2.find_all('div', {'class': "mainArea"})
        l=[]
        p2=soup2.find_all('span', {'class': "pos-rel dblock imgmobalignment"})
        # Find the img tag and extract the src attribute
        img_tag = p2[0].find('img')
        if img_tag:
            src_attribute = img_tag['src']
            image=src_attribute
        else:
            image=("No img tag found.")
        for i in p1:
            # Extract all text content from <p> tags
            paragraphs = i.find_all('p')

            # Print the text content
            for p in paragraphs:
                t2=(p.get_text(strip=True))
                t2 = t2.replace("Milestone Alert!Livemint tops charts as the fastest growing news website in the world🌏Click hereto know more", "")
                l.append(t2)
       
        try:       
            model = genai.GenerativeModel('gemini-pro')
            query=f"summarize the written text in paragarph fashion  like as inshot app(as written by professional editors of news ) and word limit will be 250 words:{l}"
            response2=model.generate_content(query)
            article_new=response2.text
            article_new2=[article_new]

        except Exception as e:
            article_new2=[('The Exception message is: ',e)]

       # print(article_new)
        mydict = {"Updated Time": updated_time,"Article_Title": text_content, "Article_href": href_value, "Article Content": article_new2, "Image":image}
        reviews.append(mydict)


df = pd.DataFrame(reviews)
df.to_csv("news.csv")



@app.route('/update', methods=['GET'])
def update():
    # Fetch new data for update

    return render_template('update.html', reviews=reviews)




@app.route("/signup", methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if user already exists
    if collection.find_one({'email': email}):
        return "User already exists. Please sign in."

    # Insert new user into MongoDB
    user = {'email': email, 'password': password}
    collection.insert_one(user)

    return "Registration successful. Please sign in."

@app.route("/index", methods=['POST'])
def index():
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if user exists and password matches
    user = collection.find_one({'email': email, 'password': password})
    print(user)
    if user:

        # Valid credentials, redirect to the home page or perform desired actions
        return render_template('index.html', reviews=reviews)
    else:
        # Invalid credentials, show error message and prompt to sign up
        return "User not found. Please sign up."



@app.route('/article/<int:index>')
def article(index):
    article_data = reviews[index]
    return render_template('article.html', article=article_data)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)