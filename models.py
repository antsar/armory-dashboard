"""Domain-specific class definitions."""


class Tournament:
    def __init__(self, name, url, events=None):
        self.name = name
        self.url = url
        self.events = events or []

    def add_event(self, event):
        self.events.append(event)
        event.tournament = self

    def count_all_fencers(self):
        for event in self.events:
            event.count_fencers()


class EventStatus:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Event:
    STATUS_REGISTRATION = EventStatus("Registration")
    STATUS_STARTED = EventStatus("Started")
    STATUS_FINISHED = EventStatus("Finished")

    def __init__(self, name, time, status, fencers, tournament=None):
        self.name = name
        self.time = time
        self.status = status
        self.fencers = fencers
        self.tournament = tournament

    def __repr__(self):
        return self.name

    def count_fencers(self):
        """Count the fencers in an event.
           Result is divided by status (checked in, not checked in, etc.)"""
        self.fencers_checked_in = []
        self.new_fencers_not_checked_in = []
        self.previously_fenced = {}
        self.previous_total = 0
        if self.name == 'Y-12 Men\'s Foil':
            print(self.fencers)
        for fencer in self.fencers:
            if fencer.is_checked_in:
                self.fencers_checked_in.append(fencer)
            else:
                self.new_fencers_not_checked_in.append(fencer)
            for event in self.tournament.events:
                if event.name == self.name:
                    break
                if fencer in event.fencers:
                    if event.name in self.previously_fenced:
                        self.previously_fenced[event.name] += 1
                    else:
                        self.previously_fenced[event.name] = 1
                    self.previous_total += 1
                    try:
                        self.new_fencers_not_checked_in.remove(fencer)
                    except ValueError:
                        pass  # already removed; ignore
                    break


class Fencer:

    def __init__(self, name, is_checked_in):
        self.name = name.strip()
        self.is_checked_in = is_checked_in

    def __repr__(self):
        return '<Fencer name="{}" is_checked_in="{}">'.format(
            self.name, self.is_checked_in)

    def __eq__(self, other):
        return self.name == other.name
