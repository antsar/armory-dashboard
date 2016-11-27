from lxml import html
import requests
import re
from urllib.parse import urlparse, urljoin

results_url = "http://www.escrimeresults.com/cobra/index.htm"
results = requests.get(results_url)
results_tree = html.fromstring(results.content)
try:
    event_urls = results_tree.xpath(
        '//div[@id="schedule"]/table/tr/td/a[text()="View"]/@href')
except IndexError:
    print("No event schedule found")
    exit()
tournament_name = results_tree.xpath(
    '//span[@class="tournName"]/text()')[0]
tournament_details = results_tree.xpath(
    '//span[@class="tournDetails"]/text()')[0]
print(tournament_name)
print(tournament_details)
print("{0} Events\n".format(len(event_urls)))
events = {}
for event_url in event_urls:
    if not urlparse(event_url).netloc:
        event_url = urljoin(results_url, event_url)
    event = requests.get(event_url)
    event_tree = html.fromstring(event.content)
    event_details = event_tree.xpath(
        '//span[@class="tournDetails"]/text()')[0]
    print("\n\n{0}".format(event_details))
    if event_tree.xpath('//a[text()="Final Results"]'):
        fencers = event_tree.xpath('//div[@id="finalResults"]/table/tr/td[2]/text()')
        print("Event Closed ({0} fencers)".format(len(fencers)))
    elif event_tree.xpath('//a[text()="Check-In Status"]'):
        checkin_summary = event_tree.xpath(
            'normalize-space(//div[@class="checkInSummary"]/text())')
        print(checkin_summary)
        fencers = event_tree.xpath('//div[@id="checkIn"]/table/tr/td[2]/text()')
    events[event_details] = []
    prior_events = {}
    for fencer in fencers:
        events[event_details].append(fencer.strip())
        for e in events:
            if e == event_details:
                continue
            if fencer.strip() in events[e]:
                if e in prior_events:
                    prior_events[e] += 1
                else:
                    prior_events[e] = 1
                break
    for e in prior_events:
        print("{0} Fencers previously fenced in {1}".format(prior_events[e], e))
    # TODO: Tally fencers who have checked in
