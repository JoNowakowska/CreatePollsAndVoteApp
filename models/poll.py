from db_interactions import DbInteractions
from typing import List

class Poll:
    def __init__(self, poll_question, owner, poll_id = None):
        self.poll_question = poll_question
        self.owner = owner
        self.poll_id = poll_id

    def __repr__(self):
        return {"Poll_id:": self.poll_id, "Poll_question:": self.poll_question, "Owner:":self.owner}

    def print_poll_question(self):
        print("Poll id: ", self.poll_id, '\n{}'.format(self.poll_question))

    def save_to_db(self):
        try:
            self.poll_id = DbInteractions.save_poll_to_db(self.poll_question, self.owner)
            return self.poll_id
        except Exception as e:
            print(e)

    @classmethod
    def print_all_polls(cls) -> List["Poll"]:
        all_polls_tuple = DbInteractions.select_all_polls()
        all_polls_list = [Poll(poll_params[1], poll_params[2], poll_params[0]) for poll_params in all_polls_tuple]
        return all_polls_list

    @classmethod
    def select_by_id(cls, poll_id) -> "Poll":
        poll_question_tuple = DbInteractions.select_poll_by_id(poll_id)
        poll = Poll(poll_question_tuple[1], poll_question_tuple[2], poll_question_tuple[0])
        return poll

    def show_poll_votes_stats(self):
        poll_options = DbInteractions.show_poll_options(self.poll_id)
        stats = DbInteractions.show_vote_stats(self.poll_id)
        poll_option_list = [[option[0], option[1]] for option in poll_options]
        stats_dict = {stat[0]: [stat[1], stat[2]] for stat in stats}
        for poll_option in poll_option_list:
            if poll_option[0] not in stats_dict.keys():
                stats_dict[poll_option[0]] = [0, 0]
            stats_dict[poll_option[0]].append(poll_option[1])
        return stats_dict


    @classmethod
    def show_poll_ids(cls):
        return DbInteractions.show_poll_ids()


