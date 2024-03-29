import datetime
import os

from trello.trelloclient import TrelloClient

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_SECRET = os.getenv('TRELLO_API_SECRET')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')

BOARD_ID = os.getenv('TRELLO_BOARD', '5f7f61eda018ce481185be8f')
HIGHLIGHTS_BOARD_ID = os.getenv('HIGHLIGHTS_BOARD', '60e4b0e00879a001f87ff95c')

COLOR_EPIC = 'purple'
COLOR_TASK = 'blue'
COLOR_PRODUCT = None
COLOR_PORTFOLIO= 'red'

LIST_DONE = 'Done'
LIST_IN_PROGRESS = 'In Progress'
LIST_BACKLOG = 'Backlog'
LIST_BLOCKED = 'Blocked/Waiting'
LIST_EVENTS = 'Scheduled Events'

LABEL_CONFERENCE_TALK = 'Conference Talk'
LABEL_CONFERENCE_WORKSHOP = 'Conference Workshop'
LABEL_CONTENT = 'Content'
LABEL_CUSTOMER = 'Customer Engagement'
LABEL_LIVE_STREAM = 'Live Stream'
LABEL_OPENSHIFT = 'OpenShift'
LABEL_RHEL = 'RHEL'
LABEL_DEVTOOLS="DevTools"
LABEL_APPSERVICES="Application Services/Integration"
LABEL_RUNTIMES_JAVA="Runtimes/Java"
LABEL_RUNTIMES_QUARKUS="Runtimes/Quarkus"
LABEL_RUNTIMES_OTHERS="Runtimes/Others"


class DashboardData:

    def __init__(self):

        # Board Agnostic
        self.label_names = None  # [str]
        self.epic_label_names = None  # [str]
        self.task_label_names = None  # [str]
        self.product_label_names = None  # [str]
        self.portfolio_label_names = None # [str]

        self.members_by_id = {}  # [str: Member]

        # Live Board
        self.board = None

        self.all_labels = None  # [Label]
        self.all_cards = None  # [Card]
        self.all_lists = None  # [TrelloList]
        self.all_members = None  # [Member]

        self.list_names = None  # [str]
        self.lists_by_id = None  # {str: [List]}
        self.lists_by_name = None  # {str: [List]}
        self.ongoing_list_ids = None  # [str]

        self.cards_by_list_id = {}  # {str: [Card]}
        self.cards_by_label = {}  # {str: [Card]}
        self.cards_by_member = {}  # {str: [Card]}

        # Archive Board
        self.archives = None

        self.archive_lists = None  # [TrelloList]
        self.archive_cards = None  # [Card]

        self.archive_lists_by_id = {}  # {str: [List]}
        self.archive_cards_by_list_id = {}  # {str: [List]}
        self.archive_cards_by_label = {}  # {str: [List]}
        self.archive_cards_by_member = {}  # {str: [List]}

        self.highlights_list_ids = None  # [str]

    def load(self, client: TrelloClient) -> None:
        """
        Loads all of the necessary data from the Trello client, organizing it as necessary
        for future calls. No other calls should be made to objects of this class without having
        first called this method.

        :param client: authenticated trello client
        """

        # Live network calls
        self.board = client.get_board(BOARD_ID)
        self.all_labels = self.board.get_labels()
        self.all_cards = self.board.open_cards()
        self.all_lists = self.board.open_lists()
        self.all_members = self.board.all_members()

        self.archives = client.get_board(HIGHLIGHTS_BOARD_ID)
        self.archive_lists = self.archives.open_lists()
        self.archive_cards = self.archives.open_cards()

        # Organize labels
        self.label_names = [label.name for label in self.all_labels]

        self.epic_label_names = [label.name for label in self.all_labels if label.color == COLOR_EPIC]
        self.task_label_names = [label.name for label in self.all_labels if label.color == COLOR_TASK]
        self.product_label_names = [label.name for label in self.all_labels if label.color == COLOR_PRODUCT]
        self.portfolio_label_names = [label.name for label in self.all_labels if label.color == COLOR_PORTFOLIO]
        self.event_label_names = [LABEL_CUSTOMER, LABEL_CONFERENCE_WORKSHOP, LABEL_CONFERENCE_TALK]

        # Organize members
        self.members_by_id = {m.id: m for m in self.all_members}

        # Organize lists
        self.list_names = [tlist.name for tlist in self.all_lists]
        self.lists_by_id = {tlist.id: tlist for tlist in self.all_lists}
        self.lists_by_name = {tlist.name: tlist for tlist in self.all_lists}
        self.archive_lists_by_id = {tlist.id: tlist for tlist in self.archive_lists}

        self.ongoing_list_ids = (
            self.lists_by_name[LIST_DONE].id,
            self.lists_by_name[LIST_IN_PROGRESS].id
        )

        self.highlights_list_ids = [tlist.id for tlist in self.archive_lists if
                                         tlist.name.startswith('Highlights')]

        # Organize cards
        def _process_card(card, member_cards, label_cards, list_cards):
            # Rebuild date as a date object
            if card.due:
                card.real_due_date = datetime.datetime.strptime(card.due, '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                card.real_due_date = None

            # FIXME: workaround for unknown member ids breaking the dashboard rendering
            # Removing from card list for now
            for m_id in card.member_ids:
                if m_id == "56cf3a7319f7628c3131411a" or m_id == "5a7cbd085aba14c4e71e8d82":
                    card.member_ids.remove(m_id)

            # Add in member names instead of IDs
            for m_id in card.member_ids:
                print(m_id)
            if card.member_ids :
                card.member_names = [self.members_by_id[m_id].full_name for m_id in card.member_ids]

                for member in card.member_names:
                    mapping = member_cards.setdefault(member, [])
                    mapping.append(card)

            # Label breakdown
            if card.labels:

                # In most cases, any cards with multiple labels will only have one per type
                # (i.e. epic, activity, product, etc). In case they do cover multiple, sort them
                # alphabetically for consistency.
                card.labels.sort(key=lambda x: x.name)

                for label in card.labels:
                    mapping = label_cards.setdefault(label.name, [])
                    mapping.append(card)

            # List cache
            list_cards.setdefault(card.list_id, []).append(card)

        for card in self.all_cards:
            _process_card(card, self.cards_by_member, self.cards_by_label, self.cards_by_list_id)

        for card in self.archive_cards:
            _process_card(card, self.archive_cards_by_member, self.archive_cards_by_label,
                          self.archive_cards_by_list_id)

    def in_progress_cards(self):
        """
        Cards: All from 'In Progress' list
        Sort: Due Date
        Extra Fields: type
        """
        in_progress_id = self.lists_by_name[LIST_IN_PROGRESS].id
        in_progress_cards = self.cards_by_list_id[in_progress_id]
        add_card_types(in_progress_cards, self.task_label_names)
        sorted_cards = sorted(in_progress_cards, key=sort_cards_by_due)
        return sorted_cards

    def backlog_cards(self):
        """
        Cards: All from 'Backlog' list
        Sort: Due Date
        Extra Fields: type
        """
        backlog_id = self.lists_by_name[LIST_BACKLOG].id
        backlog_cards = self.cards_by_list_id[backlog_id]
        add_card_types(backlog_cards, self.task_label_names)
        sorted_cards = sorted(backlog_cards, key=sort_cards_by_due)
        return sorted_cards

    def blocked_cards(self):
        """
        Cards: All from the 'Blocked/Waiting' list
        Sort: Due Date
        Extra Fields: type
        """
        blocked_id = self.lists_by_name[LIST_BLOCKED].id
        blocked_cards = self.cards_by_list_id[blocked_id]
        add_card_types(blocked_cards, self.task_label_names)
        sorted_cards = sorted(blocked_cards, key=sort_cards_by_due)
        return sorted_cards

    def upcoming_events_cards(self):
        """
        Cards: All from 'Scheduled Events' and 'In Progress' list
        Sort: Due Date
        Extra Fields: type
        """

        # Everything in the scheduled events list
        all_cards = self.cards_by_list_id[self.lists_by_name[LIST_EVENTS].id]

        # Event-related cards from the in progress list
        in_progress_cards = self.cards_by_list_id[self.lists_by_name[LIST_IN_PROGRESS].id]
        for c in in_progress_cards:
            if not c.labels:
                continue

            for label_name in c.labels:
                if label_name.name in self.event_label_names:
                    all_cards.append(c)
                    break

        add_card_types(all_cards, self.event_label_names)
        sorted_cards = sorted(all_cards, key=sort_cards_by_due)
        return sorted_cards

    def done_cards(self):
        """
        Cards: All from the 'Done' list
        Sort: Due Date
        Extra Fields: type
        """
        done_id = self.lists_by_name[LIST_DONE].id

        if done_id in self.cards_by_list_id:
            done_cards = self.cards_by_list_id[done_id]
            add_card_types(done_cards, self.task_label_names)
            cards = sorted(done_cards, key=sort_cards_by_due)
        else:
            cards = []
        return cards

    def coming_soon_cards(self):
        """
        Cards: From 'Backlog' and 'Scheduled Events' with due dates in the next 21 days
        Sort: Due Date
        Extra Fields: type
        """
        backlog_id = self.lists_by_name[LIST_BACKLOG].id
        backlog_cards = self.cards_by_list_id[backlog_id]

        events_id = self.lists_by_name[LIST_EVENTS].id
        events_cards = self.cards_by_list_id[events_id]

        all_soon_cards = backlog_cards + events_cards

        # Filter out cards with no due date or those due in more than X many days
        upcoming_date = datetime.datetime.now() + datetime.timedelta(days=21)
        upcoming_cards = [c for c in all_soon_cards if c.real_due_date and c.real_due_date < upcoming_date]

        add_card_types(upcoming_cards, self.task_label_names)
        sorted_cards = sorted(upcoming_cards, key=sort_cards_by_due)

        return sorted_cards

    def in_progress_products(self):
        """
        Cards: [product labels, cards] for 'In Progress'
        Sort: Due Date
        Extra Fields: type
        """
        return self._list_label_filter([self.lists_by_name[LIST_IN_PROGRESS].id], self.product_label_names)

    def in_progress_activities(self):
        """
        Cards: [task labels, cards] for 'In Progress'
        Sort: Due Date
        Extra Fields: type
        """
        return self._list_label_filter([self.lists_by_name[LIST_IN_PROGRESS].id], self.task_label_names)

    def in_progress_epics(self):
        """
        Cards: [epic labels, cards] for 'In Progress'
        Sort: Due Date
        Extra Fields: type
        """
        return self._list_label_filter([self.lists_by_name[LIST_IN_PROGRESS].id], self.epic_label_names)

    def in_progress_team(self):
        """
        Cards: [member name, cards] for 'In Progress'
        Sort: Due Date
        Extra Fields: type
        """
        filtered = {}
        for member_name, card_list in self.cards_by_member.items():
            filtered[member_name] = []
            for card in card_list:
                if card.list_id in [self.lists_by_name[LIST_IN_PROGRESS].id]:
                    filtered[member_name].append(card)
            add_card_types(filtered[member_name], self.task_label_names)
            filtered[member_name].sort(key=sort_cards_by_due)

        return filtered

    def backlog_products(self):
        """
        Cards: [product label, cards] for 'Backlog'
        Sort: Due Date
        Extra Fields: type
        """
        return self._list_label_filter([self.lists_by_name[LIST_BACKLOG].id], self.product_label_names)

    def backlog_activities(self):
        """
        Cards: [task label, cards] for 'Backlog'
        Sort: Due Date
        Extra Fields: type
        """
        return self._list_label_filter([self.lists_by_name[LIST_BACKLOG].id], self.task_label_names)

    def backlog_epics(self):
        """
        Cards: [epic label, cards] for 'Backlog'
        Sort: Due Date
        Extra Fields: type
        """
        return self._list_label_filter([self.lists_by_name[LIST_BACKLOG].id], self.epic_label_names)

    def backlog_team(self):
        """
        Cards: [member name, cards] for 'Backlog'
        Sort: Due Date
        Extra Fields: type
        """
        filtered = {}
        for member_name, card_list in self.cards_by_member.items():
            filtered[member_name] = []
            for card in card_list:
                if card.list_id in [self.lists_by_name[LIST_BACKLOG].id]:
                    filtered[member_name].append(card)
            add_card_types(filtered[member_name], self.task_label_names)
            filtered[member_name].sort(key=sort_cards_by_due)

        return filtered

    def month_list(self):
        """ Returns a tuple of [name, id] for all monthly highlights lists """
        monthly_list = []
        for l in self.archive_lists:
            if l.name.startswith('Highlights'):
                name = l.name[len('Highlights - '):]
                monthly_list.append([name, l.id])
        return monthly_list

    def month_highlights(self, list_id):
        """
        Cards: all cards from the given list
        Sort: Type
        Extra Fields: type
        """
        trello_list = self.archive_lists_by_id[list_id]
        highlight_label_names = self.task_label_names + self.epic_label_names + self.portfolio_label_names

        cards_by_label = self._list_label_filter([list_id], highlight_label_names,
                                                 label_cards=self.archive_cards_by_label)
        # Add extra data for each card
        for card_list in cards_by_label.values():
            add_card_types(card_list, highlight_label_names)
            pull_up_custom_fields(card_list)

        # Summarize monthly data
        stats = {
            'Event Attendance': 0,
            'Customer Attendance': 0,
        }

        # Event Attendance
        event_attendance_cards = \
            cards_by_label.get(LABEL_CONFERENCE_TALK, []) +\
            cards_by_label.get(LABEL_CONFERENCE_WORKSHOP, []) +\
            cards_by_label.get(LABEL_LIVE_STREAM, [])

        for card in event_attendance_cards:
            if card.attendees:
                stats['Event Attendance'] += card.attendees

        # Customer Attendance
        for card in cards_by_label.get(LABEL_CUSTOMER, []):
            if card.attendees:
                stats['Customer Attendance'] += card.attendees

        return cards_by_label, trello_list.name, stats

    def customer_attendees(self):
        labels = (LABEL_CUSTOMER, )
        return self._process_attendees_list(labels)

    def all_attendees(self):
        labels = (LABEL_CONFERENCE_TALK, LABEL_CONFERENCE_WORKSHOP, LABEL_CUSTOMER, LABEL_LIVE_STREAM)
        return self._process_attendees_list(labels)

    def _process_attendees_list(self, labels):
        month_cards = {}
        month_data = {}
        for month_list_id in self.highlights_list_ids:
            # Parse month name out of the list name
            month_list_name = self.archive_lists_by_id[month_list_id].name
            month_name = month_list_name.split(' ')[2]

            # Initialize the month aggregate data
            month_data[month_name] = {
                'attendees': 0
            }

            # Get the relevant cards for the month
            month_by_labels = self._list_label_filter([month_list_id], labels, label_cards=self.archive_cards_by_label)
            all_cards_for_month = []
            for cards in month_by_labels.values():
                all_cards_for_month += cards

            # For each card, pull up the type information for simplicity
            add_card_types(all_cards_for_month, labels)

            # For each card, pull the attendees up to the top level for simplicity
            for c in all_cards_for_month:
                # Figure out the event attendance
                c.attendees = 0  # default in case we don't have these values
                if len(c.custom_fields) > 0:
                    for field in c.custom_fields:
                        if field.name == 'Attendees':
                            c.attendees = int(field.value)

                # Increment the monthly count
                month_data[month_name]['attendees'] += c.attendees

            # Store the results
            month_cards[month_name] = all_cards_for_month

        return month_cards, month_data

    def _list_label_filter(self, id_list, label_list, label_cards=None):
        label_cards = label_cards or self.cards_by_label

        filtered = {}
        for label, card_list in label_cards.items():
            if label not in label_list:
                continue

            filtered[label] = []
            for card in card_list:
                if card.list_id in id_list:
                    filtered[label].append(card)

            # Remove the label if there were no matching cards found
            if len(filtered[label]) == 0:
                filtered.pop(label)

        return filtered


def sort_cards_by_due(card):
    """ Sorting key function for sorting a list of cards by their due date. """
    if card.due:
        return card.due
    else:
        return ''


def sort_cards_by_type(card):
    """ Sorting key function for card types (as added by add_card_types) """
    if len(card.types) > 0:
        return card.types[0]
    else:
        return ''


def add_card_types(card_list, accepted_labels):
    """
    Adds a new field named "type" to each card in the given list. The type will be a list
    of all label names in that card that appear in the list of provided acceptable labels.
    If the card has no labels or none match, the type field will be an empty list.
    """
    for c in card_list:
        card_types = []
        if c.labels:
            card_types = [l.name for l in c.labels if l.name in accepted_labels]
        c.types = card_types


def pull_up_custom_fields(card_list):
    """
    For each of the custom fields we use, pull them up to the card level for simplicity.
    """
    for c in card_list:
        # Establish defaults
        c.attendees = None
        c.content_url = None

        if len(c.custom_fields) > 0:
            for field in c.custom_fields:
                if field.name == 'Attendees':
                    c.attendees = int(field.value)
                elif field.name == 'URL':
                    c.content_url = field.value
