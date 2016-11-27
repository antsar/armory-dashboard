# Armory Dashboard

Scrape real-time results from Fencing Time, and calculate how many
fencers have checked in to prior events. This allows for improved
estimates of equipment inspection volume.

## Status

This is a quick weekend hack, very much not "production-ready". Use at your own risk.

## Setup

* Create a Python 3 [virtualenv](https://virtualenv.pypa.io/en/stable/)
* `pip install -r requirements.txt` to install Python dependencies

## Run

* `FLASK_APP=app.py flask run -h 0.0.0.0`
* Visit [localhost:5000](http://127.0.0.1:5000) in a browser.
