from lxml import html
import requests
import re
from urllib.parse import urlparse, urljoin
from itertools import repeat


def scrape():
    results_url = "https://fencingresults.ant.sr/cobra/"
    results = requests.get(results_url)
    results_tree = html.fromstring(results.content)
    try:
        event_urls = results_tree.xpath(
            '//div[@id="schedule"]/table/tr/td/a[text()="View"]/@href')
    except IndexError:
        return "No event schedule found"
    tournament_name = results_tree.xpath(
        '//span[@class="tournName"]/text()')[0]
    tournament_details = results_tree.xpath(
        '//span[@class="tournDetails"]/text()')[0]
    events = []
    for event_url in event_urls:
        if not urlparse(event_url).netloc:
            event_url = urljoin(results_url, event_url)
        event = requests.get(event_url)
        event_tree = html.fromstring(event.content)
        event_details = event_tree.xpath(
            '//span[@class="tournDetails"]/text()')
        event_name = event_details[0]
        event_time = event_details[1]
        if event_tree.xpath('//a[text()="Final Results"]'):
            fencers = event_tree.xpath('//div[@id="finalResults"]/table/tr/td[2]/text()')
            fencers = dict(zip(fencers, repeat("Checked In")))
            event_status = "closed"
        elif event_tree.xpath('//a[text()="Seeding"]'):
            fencers = event_tree.xpath('//div[@id="Round1Seeding"]/table/tr/td[2]/text()')
            fencers = dict(zip(fencers, repeat("Checked In")))
            event_status = "ongoing"
        elif event_tree.xpath('//a[text()="Check-In Status"]'):
            event_status = "open"
            fencers_checked_in = [True if len(list(f)) else False for f in event_tree.xpath('//div[@id="checkIn"]/table/tr/td[1]')]
            fencers = event_tree.xpath('//div[@id="checkIn"]/table/tr/td[2]/text()')
            fencers = dict(zip(fencers, fencers_checked_in))
        try:
            del this_event
        except:
            pass # not yet set, oh well
        this_event = {
            'name': event_name,
            'time': event_time,
            'status': event_status,
            'fencers': [],
            'fencers_checked_in': [],
            'new_fencers_not_checked_in': [],
            'previously_fenced': {},
            'previous_total': 0
        }
        for fencer, is_checked_in in fencers.items():
            fencer = fencer.strip()
            this_event['fencers'].append(fencer)
            if is_checked_in:
                this_event['fencers_checked_in'].append(fencer)
            else:
                this_event['new_fencers_not_checked_in'].append(fencer)
            for e in events:
                if e['name'] == event_details:
                    continue
                if fencer in e['fencers']:
                    if e['name'] in this_event['previously_fenced']:
                        this_event['previously_fenced'][e['name']] += 1
                    else:
                        this_event['previously_fenced'][e['name']] = 1
                    this_event['previous_total'] += 1
                    try:
                        this_event['new_fencers_not_checked_in'].remove(fencer)
                    except ValueError:
                        pass # already removed; ignore
                    break
        events.append(this_event)
    return (tournament_name, tournament_details, events)
