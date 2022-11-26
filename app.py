from flask import Flask, render_template
from data import Articles

#Creating instance of flask
app = Flask(__name__)

get_articles = Articles()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = get_articles) #Extracting data articles

@app.route('/single_article/<string:id>/')
def articles(id):
    return render_template('single_article.html', id=id)

if __name__ == "__main__":
    app.run(debug=True)