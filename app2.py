from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb+srv://master:!!master@atlascluster.w0iwrbk.mongodb.net/?retryWrites=true&w=majority')
db = client['client_database']
collection = db['users']

def operation():
    reviews = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    search = "latest-news"
    response = requests.get(f"https://www.livemint.com/{search}")
    soup = bs(response.content, "html.parser")
    n1 = soup.find_all('div', {'id': "listview"})

    for i in n1:
        r = i.find_all('div', {'class': "listingNew clearfix impression-candidate ga-tracking"})
        for j in r:
            link = j.find('a')
            href_value = "https://www.livemint.com" + link['href']
            h2_tag = j.find("h2", {'class': "headline"})
            text_content = h2_tag.get_text(strip=True)
            updated_time_span = j.find('span', {'class': 'fl date'})
            updated_time = updated_time_span.find('span', {'data-expandedtime': True}).get('data-expandedtime')

            response2 = requests.get(href_value)
            soup2 = bs(response2.content, "html.parser")
            p1 = soup2.find_all('div', {'class': "mainArea"})
            l = []
            for i in p1:
                paragraphs = i.find_all('p')
                for p in paragraphs:
                    t2 = (p.get_text(strip=True))
                    t2 = t2.replace("Milestone Alert!Livemint tops charts as the fastest growing news website in the world🌏Click hereto know more", "")
                    l.append(t2)

            mydict = {"Updated Time": updated_time, "Article_Title": text_content, "Article_href": href_value, "Article Content": l}
            reviews.append(mydict)

    return reviews

@app.route("/")
def login():
    reviews = operation()
    return render_template('login.html', reviews=reviews)

@app.route("/register")
def register():
    reviews = operation()
    return render_template('register.html', reviews=reviews)

@app.route("/signup", methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')

    if collection.find_one({'email': email}):
        return "User already exists. Please sign in."

    user = {'email': email, 'password': password}
    collection.insert_one(user)

    return "Registration successful. Please sign in."

@app.route("/index", methods=['POST'])
def index():
    email = request.form.get('email')
    password = request.form.get('password')

    user = collection.find_one({'email': email, 'password': password})
    if user:
        reviews = operation()
        return render_template('index.html', reviews=reviews)
    else:
        return "User not found. Please sign up."

@app.route('/article/<int:index>')
def article(index):
    reviews = operation()
    article_data = reviews[index]
    return render_template('article.html', article=article_data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
