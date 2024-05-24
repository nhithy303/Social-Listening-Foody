from urllib import response
from flask import Flask, flash, jsonify, render_template, request
from processer import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('landing.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html',
                           total_stores=total_stores,
                           total_categories=len(category_reviews['category']),
                           total_cuisine=len(cuisine_reviews['cuisine']))

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)