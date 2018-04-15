from flask import Flask, render_template, redirect, request, url_for
from flask_caching import Cache
from scraper import Scraper

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

    scraper = Scraper(results_url)
    tournament = scraper.scrape()
    return render_template('live.html',
                           tournament_name=tournament.name,
                           events=tournament.events)


if __name__ == "__main__":
    app.run()
