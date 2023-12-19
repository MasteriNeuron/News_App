from flask import Flask, render_template,request,session, redirect, url_for
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
from pymongo import MongoClient
import pandas as pd

import os

app = Flask(__name__)

@app.route("/")
def login():
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')



# Connect to MongoDB
client = MongoClient('mongodb+srv://master:master123@atlascluster.w0iwrbk.mongodb.net/?retryWrites=true&w=majority')
db = client['client_database']  # Replace 'client_database' with your database name
collection = db['users']  # Replace 'users' with your collection name
reviews=[]
def operation():
    # Assume your existing code for scraping and processing goes here
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    search="latest-news"
    # fetch the search results page
    response = requests.get(f"https://www.livemint.com/"+search)

    # parse the HTML using BeautifulSoup
    soup = bs(response.content, "html.parser")
    n1=soup.find_all('div', {'id': "listview"})
    
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
            for i in p1:
                # Extract all text content from <p> tags
                paragraphs = i.find_all('p')

                # Print the text content
                for p in paragraphs:
                    t2=(p.get_text(strip=True))
                    t2 = t2.replace("Milestone Alert!Livemint tops charts as the fastest growing news website in the world🌏Click hereto know more", "")
                    l.append(t2)
        
            mydict = {"Updated Time": updated_time,"Article_Title": text_content, "Article_href": href_value, "Article Content": l}
            reviews.append(mydict)
    return(reviews)
    #df = pd.DataFrame(reviews)



@app.route('/update', methods=['GET'])
def update():
    # Fetch new data for update
    new_reviews = operation()
    return render_template('update.html', reviews=new_reviews)




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
        reviews=operation()
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