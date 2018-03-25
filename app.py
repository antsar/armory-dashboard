from urllib.parse import urlparse, urljoin
import re
from flask import Flask, render_template, redirect, request, url_for
from flask_caching import Cache
from lxml import html
import requests
from scrape import scrape

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')

@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/live")
@cache.cached(timeout=300, key_prefix=make_cache_key)
def live(results_url=None):
    results_url = request.args.get('results_url')
    if not results_url:
        return redirect(url_for('index'))
    tournament_name, tournament_details, events = scrape(results_url)
    return render_template('live.html',
        tournament_name = tournament_name,
        tournament_details = tournament_details,
        events = events)

if __name__ == "__main__":
    app.run()
