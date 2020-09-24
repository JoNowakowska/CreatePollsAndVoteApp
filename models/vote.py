from db_interactions import DbInteractions
import datetime
import pytz

class Vote:

    def __init__(self, users_vote, users_name, timestamp_):
        self.users_vote = users_vote
        self.users_name = users_name
        self.timestamp_ = timestamp_

    def save_to_db(self):
        DbInteractions.save_vote_to_db(self.users_vote, self.users_name, self.timestamp_)

    @classmethod
    def select_random_winner(cls, poll_id, start_date_naive, end_date_naive, timezone_):
        users_timezone = pytz.timezone(timezone_)
        start_date_aware = users_timezone.localize(start_date_naive)
        end_date_aware = users_timezone.localize(end_date_naive)

        start_date_as_utc = start_date_aware.astimezone(pytz.utc)
        end_date_as_utc = end_date_aware.astimezone(pytz.utc)

        start_utc_timestamp = start_date_as_utc.timestamp()
        end_utc_timestamp = end_date_as_utc.timestamp()

        random_winner = DbInteractions.draw_random_winner(poll_id, start_utc_timestamp, end_utc_timestamp)
        option_id, username, utc_timestamp, _, option_text, poll_id, _, poll_question, owner = random_winner

        utc_time_of_vote_naive = datetime.datetime.utcfromtimestamp(utc_timestamp)
        utc_timezone = pytz.timezone("UTC")
        utc_time_of_vote_aware = utc_timezone.localize(utc_time_of_vote_naive)
        selectors_time_of_vote = utc_time_of_vote_aware.astimezone(users_timezone)

        return poll_id, poll_question, username, option_text, selectors_time_of_vote





