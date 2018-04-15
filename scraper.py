from lxml import html
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin

from models import Event, Fencer, Tournament


class Scraper:
    def __init__(self, tournament_url):
        self.tournament_url = tournament_url

    def scrape(self):

        # Get tournament info
        try:
            results = requests.get(self.tournament_url)
        except requests.exceptions.MissingSchema:
            results = requests.get("http://{}".format(self.tournament_url))
        results_tree = html.fromstring(results.content)
        try:
            tournament_name = results_tree.xpath(
                '//span[@class="tournName"]/text()')[0]
            updated = (results_tree.xpath(
                '//span[@class="lastUpdate"]/text()')[0]
                .replace('Last Updated:', '').strip())
        except IndexError:
            raise ScrapeError("Tournament info not found.")

        self.tournament = Tournament(tournament_name, results.url, updated)

        # Get tournament events
        try:
            event_urls = results_tree.xpath(
                '//div[@id="schedule"]/table/tr/td/a[text()="View"]/@href')
        except IndexError:
            raise ScrapeError("No event schedule found.")

        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.scrape_events(event_urls))

        return self.tournament

    async def scrape_events(self, event_urls):

        with ThreadPoolExecutor(max_workers=20) as executor:
            loop = asyncio.get_event_loop()
            futures = []

            for event_url in event_urls:
                if not urlparse(event_url).netloc:
                    event_url = urljoin(self.tournament.url, event_url)
                futures.append(loop.run_in_executor(
                    executor,
                    requests.get,
                    event_url))

            for response in await asyncio.gather(*futures):
                event = self.parse_event(response)
                self.tournament.add_event(event)

            self.tournament.count_all_fencers()

    def parse_event(self, event):
        # Get the event details (name, time) as text
        event_tree = html.fromstring(event.content)
        event_details = event_tree.xpath(
            '//span[@class="tournDetails"]/text()')
        try:
            event_name = event_details[0]
            event_time = event_details[1]
        except IndexError:
            raise ScrapeError(
                "Failed to interpret live results for event \"{}\"."
                .format(event_details))

        # Get the event status
        if event_tree.xpath('//a[text()="Final Results"]'):
            fencers = event_tree.xpath(
                '//div[@id="finalResults"]/table/tr/td[2]/text()')
            fencers = [Fencer(f, True) for f in fencers]
            event_status = Event.STATUS_FINISHED
        elif event_tree.xpath('//a[text()="Seeding"]'):
            fencers = event_tree.xpath(
                '//div[@id="Round1Seeding"]/table/tr/td[2]/text()')
            fencers = [Fencer(f, True) for f in fencers]
            event_status = Event.STATUS_STARTED
        elif event_tree.xpath('//a[text()="Check-In Status"]'):
            event_status = Event.STATUS_REGISTRATION
            fencers_checked_in = [
                True if len(list(f)) else False
                for f in event_tree.xpath(
                    '//div[@id="checkIn"]/table/tr/td[1]')]
            fencers = event_tree.xpath(
                '//div[@id="checkIn"]/table/tr/td[2]/text()')
            fencers = [Fencer(f, ci)
                       for (f, ci) in zip(fencers, fencers_checked_in)]

        return Event(event_name, event_time, event_status, event.url, fencers)


class ScrapeError(Exception):
    pass
