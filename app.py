from urllib.parse import urlparse, urljoin
import re
from flask import Flask, render_template
from lxml import html
import requests
from scrape import scrape

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

@app.route("/")
def index():
    tournament_name, tournament_details, events = scrape()
    return render_template('index.html',
        tournament_name = tournament_name,
        tournament_details = tournament_details,
        events = events)

if __name__ == "__main__":
    app.run()
