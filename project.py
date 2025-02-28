import sys

from liarsdice import Bid, Bot, Die, Game, Human
from pyfiglet import Figlet


def main():
    try:
        # Greet user
        print(get_greeting())

        invitation_to_play = "Hey, there! Care for a game of dice? (y/n)\n"
        if not prompt_boolean_question(invitation_to_play):
            sys.exit("Maybe another time... Bye!")
        # Get number of players
        print("Great! How many opponents will you take on?")
        count_of_bots = get_count_of_bots()

        # Instantiate game & players
        invitation_wild_1s = (
            "Feeling lucky today? Test yourself with 'wild' ones mode! (y/n)\n"
        )
        game = Game(prompt_boolean_question(invitation_wild_1s))

        human = Human("Human_Player")
        players = [human]

        for i in range(count_of_bots):
            players.append(Bot(f"Bot_{i}"))

        game.players = players

        # Start game
        while game.count_players_with_remaining_dice() > 1:
            # Add & setup round
            round = game.add_round()
            round.draw_hands()

            print(announcement(str(round), "="))

            # Show hand to human player
            print(f"*** The dice you've rolled:")
            print(human.stringify_hand())
            input()

            # Play turns
            count_all_active_dice = round.get_count_of_all_active_dice()

            while round.round_loser == None:
                # Player whose turn it is makes a bid or challenge
                if isinstance(round.whose_turn, Human):
                    if round.active_bid == None:
                        print(f"Your turn! Time to make the first bid for the round:")

                        turn_result = get_bid_from_human(
                            round.active_bid, count_all_active_dice
                        )
                    else:
                        will_bid = f"Do you want to raise the active bid (if not, you automatically call 'Liar')? (y/n)\n"
                        if prompt_boolean_question(will_bid):
                            turn_result = get_bid_from_human(
                                round.active_bid, count_all_active_dice
                            )
                        else:
                            turn_result = None

                elif isinstance(round.whose_turn, Bot):
                    turn_result = round.whose_turn.play_turn(
                        round.active_bid, count_all_active_dice
                    )

                # If a challenge is issued
                if not isinstance(turn_result, Bid):
                    print(
                        f"{(round.whose_turn).name} calls 'Liar' on {(round.active_bidder).name}"
                    )
                    input()

                    if round.evaluate_challenge(round.active_bid, game.wild_1s):
                        round.active_bidder.lose_a_die()
                        round.round_loser = round.active_bidder
                    else:
                        round.whose_turn.lose_a_die()
                        round.round_loser = round.whose_turn

                    print(announcement("Revealing all dice:", "-"))

                    for player in round.players:
                        print(player.stringify_hand())

                    print(
                        f"*** Active bid is {round.active_bid} by {(round.active_bidder).name}"
                    )
                    print(
                        announcement(
                            f"{(round.round_loser).name} loses Round {round.number}!", "-"
                        )
                    )
                    input()
                # If the bid was raised
                else:
                    round.active_bid = turn_result
                    round.active_bidder = round.whose_turn
                    print(f"{(round.whose_turn).name} bids {turn_result}")
                    input()

                    round.rotate_turn()

            # Announce if loser leaves the game
            if round.round_loser.dice_left < 1:
                if isinstance(round.round_loser, Human):
                    print(announcement("You're out of dice, and are leaving the game", "*"))
                    sys.exit()
                else:
                    print(announcement(f"{(round.round_loser).name} leaves the game", "*"))
                    input()

        # Declare winner & say goodbye
        for player in round.players:
            if player.dice_left > 0:
                game.winner = player
        print(get_congratulation())
    except (KeyboardInterrupt, EOFError):
        sys.exit("You've quit the game. See you next time!")


def announcement(msg, line_elem):
    s = (line_elem * 79) + "\n"
    s += msg.center(79) + "\n"
    s += line_elem * 79

    return s


def _get_bid_face():
    while True:
        try:
            face = int(input("Face: ").strip())
        except ValueError:
            pass
        except EOFError:
            sys.exit()
        else:
            if 6 >= face >= 1:
                return face


def _get_bid_count(count_all_active_dice):
    while True:
        try:
            count = int(input("Count (occurences of given face): ").strip())
        except ValueError:
            pass
        except EOFError:
            sys.exit()
        else:
            if count_all_active_dice >= count > 0:
                return count


def get_bid_from_human(active_bid, count_all_active_dice):
    while True:
        # Get bid face & count
        face = _get_bid_face()
        count = _get_bid_count(count_all_active_dice)

        # Try to instantiate the bid
        try:
            bid = Bid(Die(face), count, active_bid, count_all_active_dice)
        except Exception as e:
            print(e)
        else:
            break

    return bid


def get_congratulation():
    f = Figlet()
    f.setFont(font="thin")

    s = f"Congratulations! You won the game!\n"
    s += f"Nice playing you!"

    return f.renderText(s)


def get_count_of_bots():
    while True:
        try:
            count = int(
                input("(choose number of opponents, between 1 and 4)\n").strip()
            )
        except ValueError:
            pass
        except EOFError:
            sys.exit()
        else:
            if 4 >= count >= 1:
                break

    return count


def get_greeting():
    f = Figlet()
    f.setFont(font="doom")
    return f.renderText("Liar's Dice")


def prompt_boolean_question(prompt):
    acceptable_answers = ["y", "yes", "1", "true"]
    return input(prompt).strip().lower() in acceptable_answers


if __name__ == "__main__":
    main()
