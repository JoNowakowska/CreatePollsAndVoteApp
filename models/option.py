from typing import List

from db_interactions import DbInteractions

class Option:
    def __init__(self, poll_id, option_text, option_id = None):
        self.poll_id = poll_id
        self.option_text = option_text
        self.option_id = option_id

    def __repr__(self):
        return {"Poll_id:": self.poll_id, "Option_text:": self.option_text, "Option_id:":self.option_id}

    def print_option(self):
        print(self.option_id, " - ", self.option_text)

    def save_to_db(self):
        try:
            DbInteractions.save_option_to_db(self.option_text, self.poll_id)
        except Exception as e:
            print(e)

    @classmethod
    def select_by_poll_id(cls, poll_id) -> List["Option"]:
        options_tuple = DbInteractions.select_options_by_poll_id(poll_id)
        options_list = [Option(options_params[2], options_params[1], options_params[0]) for options_params in options_tuple]
        return options_list

