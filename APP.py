from models.poll import Poll
from models.option import Option
from models.vote import Vote
import datetime
import pytz

class Menu:
    MENU = """
        --- Menu ---

        1 - Create new poll
        2 - List open polls
        3 - Vote on a poll
        4 - Show poll votes statistics
        5 - Select a random winner from a poll
        6 - Exit

        Enter your choice:
    """

    @classmethod
    def select_from_menu(cls):
        choice_id = input(cls.MENU)
        while choice_id not in ["0", "1", "2", "3", "4", "5", "6"]:
            input(
                """Sorry, you've entered an invalid value. Please select an option from the Menu and enter it's ID. 
                Press Enter to continue...""")
            choice_id = input(cls.MENU)

        cls.show_selected_option(choice_id)

    @classmethod
    def show_selected_option(cls, choice_id):
        choices_with_ids = {
            "1": cls.create_new_poll,
            "2": cls.list_open_polls,
            "3": cls.vote_on_a_poll,
            "4": cls.show_poll_votes_stats,
            "5": cls.select_random_winner,
            "6": cls.exit
        }

        return choices_with_ids[choice_id]()

    @classmethod
    def create_new_poll(cls):
        owner = input("Please provide your name: ")
        while not owner:
            owner = input("Try again. Please provide your name: ")
        poll_question = input("Please provide a question you want your poll respond for: ")
        while not poll_question:
            poll_question = input("Try again. Please provide a question you want your poll responds for: ")
        options = []
        option = input("Please provide the first option: ")
        while option != '':
            options.append(option)
            option = input("Please provide the next option or leave it blank to finish the process, then press Enter : ")
        try:
            new_poll = Poll(poll_question, owner)
            poll_id = new_poll.save_to_db()[0]
            for option in options:
                Option(poll_id, option).save_to_db()
        except Exception as e:
            print(e)
            return

        input("Your poll has been created! Press Enter to see it...")
        print("\nPoll id: ", poll_id)
        print(poll_question)
        for option in options:
            print("\t", option)
        input("\nPres Enter to continue...")
        cls.select_from_menu()


    @classmethod
    def list_open_polls(cls):
        print("Following are the polls you can vote on: ")
        for poll in Poll.print_all_polls():
            print(poll.poll_id, poll.poll_question)
        input("\nPress Enter to continue...")
        cls.select_from_menu()

    @classmethod
    def vote_on_a_poll(cls):
        poll_id = input("Enter the id of the poll you want to vote on: ")
        try:
            poll = Poll.select_by_id(int(poll_id))
        except:
            print("An error occurred. I can't find the poll id '{}' in the database. Please make sure you've entered a valid poll id.".format(poll_id))
            cls.vote_on_a_poll()
            return

        options_list = Option.select_by_poll_id(poll_id)

        poll.print_poll_question()
        for option in options_list:
            option.print_option()

        users_vote = input("Enter an id of you answer: ")
        while users_vote not in [str(option.option_id) for option in options_list]:
            users_vote = input("This is not a valid answer. Enter an id of you answer: ")
        users_name = input("Enter your name: ")
        while not users_name:
            users_name = input("Enter your name: ")
        users_timezone = input("Enter your timezone: ")
        while users_timezone not in pytz.all_timezones:
            users_timezone = input("This is not a valid timezone. Try again. Enter your timezone: ")

        users_timezone_obj = pytz.timezone(users_timezone)
        local_time_of_vote = users_timezone_obj.localize(datetime.datetime.now())
        utc_timestamp = local_time_of_vote.astimezone(pytz.utc).timestamp()

        vote = Vote(users_vote, users_name, utc_timestamp)
        vote.save_to_db()

        input(f'\nThank you for participating in the poll, {users_name}! Press Enter to continue...')
        cls.select_from_menu()

    @classmethod
    def show_poll_votes_stats(cls):
        poll_id = input("Enter the id of the poll you want to see statistics for: ")
        try:
            poll = Poll.select_by_id(poll_id)
        except Exception:
            print("\nAn error occurred. Please make sure you've entered a valid poll id.")
            return
        poll.print_poll_question()
        stats_dict = poll.show_poll_votes_stats()
        for key, value in stats_dict.items():
            print(
                f"""
{key} - {value[2]}:
        number of votes: {value[0]} = {value[1]:.1f}%
                """
            )
        input("\nPress Enter to continue...")
        cls.select_from_menu()

    @classmethod
    def select_random_winner(cls):
        poll_ids = Poll.show_poll_ids()
        poll_id = input("Enter an id of a poll voters of which you want to select a random winner from: ")
        while poll_id not in [str(id[0]) for id in poll_ids]:
            poll_id = input("This is not a valid poll id. Enter a valid poll id: ")
        start_date = input("Select a time period of which you want to pick up a random winner. \nEnter a start date and start hour (dd-mm-yyyy HH:MM): ")
        end_date = input("Enter the end date and the end hour (dd-mm-yyyy HH:MM): ")
        try:
            start_date_naive = datetime.datetime.strptime(start_date.strip(), "%d-%m-%Y %H:%M")
            end_date_naive = datetime.datetime.strptime(end_date.strip(), "%d-%m-%Y %H:%M")
        except ValueError:
            input("At least one of the dates you've entered is not in a valid date format. Try again. Press Enter...")
            cls.select_random_winner()
            return
        if start_date_naive > end_date_naive:
            input("End date cannot be older than the start date. Try again. Press Enter...")
            cls.select_random_winner()
            return
        timezone_ = input("Enter your timezone: ")
        while timezone_ not in pytz.all_timezones:
            input("You've entered an invalid timezone. Please try again. Press Enter...")
            timezone_ = input("Enter your timezone: ")

        try:
            poll_id, poll_question, username, option_text, selectors_time_of_vote = Vote.select_random_winner(poll_id, start_date_naive, end_date_naive, timezone_)

            print(f'''\nA winner of a poll number {poll_id} answering a question "{poll_question}" is: {username}.
The winner responded "{option_text}". 
Time of vote: {selectors_time_of_vote.strftime("%d-%m-%Y %H:%M")}.    
            ''')

            input("\nPress Enter to continue...")

        except Exception:
            input("An error occurred. Press Enter...")

        finally:
            cls.select_from_menu()

    @classmethod
    def exit(cls):
        print("Thanks for your time! Goodbye and have a nice day!")

Menu.select_from_menu()