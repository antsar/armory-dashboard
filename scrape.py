from lxml import html
import requests
import re
from urllib.parse import urlparse, urljoin


def scrape():
    results_url = "http://www.escrimeresults.com/cobra/index.htm"
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
            '//span[@class="tournDetails"]/text()')[0]
        if event_tree.xpath('//a[text()="Final Results"]'):
            fencers = event_tree.xpath('//div[@id="finalResults"]/table/tr/td[2]/text()')
            event_status = "Event Closed ({0} fencers)".format(len(fencers))
        elif event_tree.xpath('//a[text()="Seeding"]'):
            fencers = event_tree.xpath('//div[@id="Round1Seeding"]/table/tr/td[2]/text()')
            event_status = "Event is Ongoing ({0} fencers)".format(len(fencers))
        elif event_tree.xpath('//a[text()="Check-In Status"]'):
            event_status = event_tree.xpath(
                'normalize-space(//div[@class="checkInSummary"]/text())')
            fencers = event_tree.xpath('//div[@id="checkIn"]/table/tr/td[2]/text()')
        try:
            del this_event
        except:
            pass
        this_event = {
            'name': event_details,
            'status': event_status,
            'fencers': [],
            'previously_fenced': {},
            'previous_total': 0
        }
        for fencer in fencers:
            this_event['fencers'].append(fencer.strip())
            for e in events:
                if e['name'] == event_details:
                    continue
                if fencer.strip() in e['fencers']:
                    if e['name'] in this_event['previously_fenced']:
                        this_event['previously_fenced'][e['name']] += 1
                    else:
                        this_event['previously_fenced'][e['name']] = 1
                    this_event['previous_total'] += 1
                    break
        events.append(this_event)
        # TODO: Tally fencers who have checked in
    return (tournament_name, tournament_details, events)
