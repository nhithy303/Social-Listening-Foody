from urllib import response
from flask import Flask, flash, jsonify, render_template, request, redirect
from processer import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('landing.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    processed_info = get_avalaible_data()
    if processed_info['fetch_counts'][0] == 0:
        processed_info = fetch_data()
    return render_template('dashboard.html',
                           total_stores=processed_info['total_stores'][0],
                           total_categories=processed_info['total_categories'][0],
                           total_cuisine=processed_info['total_cuisine'][0],
                           total_reviews=processed_info['total_reviews'][0],
                           n_category_charts=range(0, processed_info['n_category_charts'][0]),
                           n_cuisine_charts=range(0, processed_info['n_cuisine_charts'][0]))

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/fetch-data', methods=['POST'])
def fetch():
    processed_info = fetch_data()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)