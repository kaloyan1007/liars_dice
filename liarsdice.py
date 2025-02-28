import random
from collections import Counter


class Bid:
    """
    An instance of Bid represents a guess that at least as many occurences (count)
    of a die face are present within the concealed hands of all players
    """

    def __init__(self, die, count, active_bid=None, count_all_active_dice=None):
        self._check_bid_validity(die, count, active_bid, count_all_active_dice)

        self._die = die
        self._count = count

    def __str__(self):
        return f"{self.count} occurrences of:\n{Die.stringify_dice([self.die])}"

    @classmethod
    def is_higher(cls, new_bid, active_bid):
        """
        Determines whether a new_bid is higher than the active_bid
        """
        if new_bid.die.face > active_bid.die.face:
            return True
        elif new_bid.die.face < active_bid.die.face:
            return False
        else:
            if new_bid.count > active_bid.count:
                return True
            else:
                return False

    def _check_bid_validity(
        self, die, count, active_bid=None, count_all_active_dice=None
    ):
        """
        Checks if the die and face args, passed to the constructor can be used to
        create a bid object. It's helper function - the main purpose is to keep the constructor cleaner
        """
        if not isinstance(die, Die):
            raise TypeError(
                "Invalid bid: the value for the 'die' attribute must be of class Die"
            )
        if not isinstance(count, int):
            raise TypeError("Invalid bid: non-integer count")

        if not count > 0:
            raise ValueError("Invalid bid: count must be > 0")

        if not count_all_active_dice is None:
            if not isinstance(count_all_active_dice, int):
                raise TypeError("Non-integer for count_all_active_dice")

            if not count_all_active_dice > 2:
                raise ValueError(
                    "count_all_active_dice must be > 2, or the game is over"
                )

        if count_all_active_dice:
            if count > count_all_active_dice:
                raise ValueError(
                    "Invalid bid: there are currently less dice in play than bid count"
                )

        if active_bid:
            if die.face < active_bid.die.face:
                raise ValueError("Invalid bid: bid face < face in active bid")
            elif die.face == active_bid.die.face:
                if count <= active_bid.count:
                    raise ValueError(
                        "Invalid bid: bid count is not > count in active bid, while faces are the same"
                    )

    @property
    def die(self):
        return self._die

    @property
    def count(self):
        return self._count


class Die:
    """
    A Die instance represents a single die (one of the players' dice)
    """
    def __init__(self, face):
        if not isinstance(face, int):
            raise TypeError("Invalid die: non-integer face")

        if not 6 >= face >= 1:
            raise ValueError("Invalid die: face not between 1 and 6")

        self._face = face

    @staticmethod
    def stringify_dice(raw_hand):
        """
        Returns a string of ASCII art/ pseudo graphics, representing dice faces.
        Expects a list of Die objects as the only argument.

        To be used in printing player's hands & bids.
        """
        if not isinstance(raw_hand, list):
            raise TypeError(
                "The Die.stringify_dice methods expects a list of Die objects"
            )

        if len(raw_hand) == 0:
            raise ValueError(
                "The Die.stringify_dice methods expects a list of at least 1 Die object"
            )

        for d in raw_hand:
            if not isinstance(d, Die):
                raise TypeError(
                    "The Die.stringify_dice methods expects a list of Die objects"
                )

        top_bottom = "+-------+"
        blank_row = "|       |"
        middle_point = "|   O   |"
        left_side_point = "| O     |"
        right_side_point = "|     O |"
        both_side_points = "| O   O |"

        dice_faces = [
            [top_bottom, blank_row, middle_point, blank_row, top_bottom],
            [top_bottom, right_side_point, blank_row, left_side_point, top_bottom],
            [top_bottom, right_side_point, middle_point, left_side_point, top_bottom],
            [top_bottom, both_side_points, blank_row, both_side_points, top_bottom],
            [top_bottom, both_side_points, middle_point, both_side_points, top_bottom],
            [
                top_bottom,
                both_side_points,
                both_side_points,
                both_side_points,
                top_bottom,
            ],
        ]

        hand = [die.face for die in raw_hand]

        s = ""
        for i in range(5):
            for die in hand:
                s += " " + dice_faces[die - 1][i]

            s += "\n"

        return s.rstrip("\n")

    @property
    def face(self):
        return self._face


class Round:
    """
    A Round instance represents one of the rounds in a game of "Liar's dice".
    """
    def __init__(self, number, players, whose_turn):
        if not isinstance(number, int):
            raise TypeError("Invalid round number: has to be a positive integer")
        if not number > 0:
            raise ValueError("Invalid round number: has to be a positive integer")
        self._number = number

        for p in players:
            if not isinstance(p, Player):
                raise TypeError(
                    "The 'players' property of a Round object has to be a list of Player objects"
                )

        if len(players) < 2:
            raise ValueError("A round can't have less than 2 players")
        self._players = players

        if not isinstance(whose_turn, Player):
            raise TypeError(
                "The 'whose_turn' property has to reference a Player object"
            )
        self._whose_turn = whose_turn

        self._active_bid = None
        self._active_bidder = None
        self._round_loser = None

    def __str__(self):
        return f"Round {self.number} begins! ({len(self.players)} players in the game)"

    @classmethod
    def determine_index_of_next(cls, players, previous_in_turn):
        """
        Returns the index of the next player, whose turn it will be.
        Ignores whether the returned index is of the player, who lost the previous round,
        or whether they have dice left.
        """
        overflowed_index_of_next = (players.index(previous_in_turn)) + 1

        if overflowed_index_of_next < len(players):
            return overflowed_index_of_next
        else:
            return len(players) % overflowed_index_of_next

    @classmethod
    def determine_whose_turn_at_next_round(
        cls, prev_round_players, loser, prev_round_whose_turn
    ):
        """
        Returns the player whose turn it will be at the start of the next round (for round > round1)
        """
        if prev_round_players is None or len(prev_round_players) < 2:
            raise Exception(
                "For a next round to start, there need to be at least 2 prev_round_players"
            )

        if loser is None or prev_round_whose_turn is None:
            raise TypeError(
                "'loser' and 'prev_round_whose_turn' can't == None! Remember: determine_whose_turn_at_next_round() is only to be called for a Next round, not for First round of a game"
            )

        if loser.dice_left > 0:
            return loser

        return cls._return_next(prev_round_players, loser, prev_round_whose_turn)

    @staticmethod
    def _return_next(players, loser, whose_turn):
        """
        Recursive method to loop over the players list continuosly and return the next player whose turn it will be.
        Only called when the loser of the previous round has no dice left and can't continue.
        """
        # Base case
        index_of_next = Round.determine_index_of_next(players, whose_turn)
        next = players[index_of_next]

        if next != loser:
            return next

        # Recursive call
        return Round._return_next(players, loser, next)

    def get_count_of_all_active_dice(self):
        count_all_active_dice = 0
        for player in self.players:
            count_all_active_dice += player.dice_left

        return count_all_active_dice

    def draw_hands(self):
        """
        Simulates all players (of the current round) rolling their dice
        """
        if self.players is None or len(self.players) < 2:
            raise Exception(
                "There must be at least 2 players if hands are going to be drawn"
            )

        for player in self.players:
            player.draw_hand()

    def evaluate_challenge(self, active_bid, is_wild_1s):
        total_count = 0
        if is_wild_1s:
            for p in self._players:
                for die in p.hand:
                    if die.face in [active_bid.die.face, 1]:
                        total_count += 1
        else:
            # Classic rules:
            for p in self._players:
                for die in p.hand:
                    if die.face == active_bid.die.face:
                        total_count += 1

        return total_count < active_bid.count

    def rotate_turn(self):
        self._whose_turn = self._players[
            Round.determine_index_of_next(self.players, self.whose_turn)
        ]

    @property
    def number(self):
        return self._number

    @property
    def players(self):
        return self._players

    @property
    def whose_turn(self):
        return self._whose_turn

    @whose_turn.setter
    def whose_turn(self, p):
        if not isinstance(p, Player):
            raise TypeError(
                "The 'whose_turn' property of a Round object has to be a Player object"
            )

        if p not in self._players:
            raise ValueError(
                "The 'whose_turn' property of a Round object has to be a Player object which is included in the list of players in Round.players"
            )

        if p == self._whose_turn:
            raise ValueError("It can't be same player's turn twice in a row")

        self._whose_turn = p

    @property
    def active_bid(self):
        return self._active_bid

    @active_bid.setter
    def active_bid(self, b):
        if not isinstance(b, Bid):
            raise TypeError(
                "The 'active_bid' property of a Round object has to be a Bid object"
            )

        if not self._active_bid is None:
            if not Bid.is_higher(b, self._active_bid):
                raise ValueError("The new bid has to be higher than the active bid")

        self._active_bid = b

    @property
    def active_bidder(self):
        return self._active_bidder

    @active_bidder.setter
    def active_bidder(self, p):
        if not isinstance(p, Player):
            raise TypeError(
                "The 'active_bidder' property of a Round object has to be a Player object"
            )

        if p not in self._players:
            raise ValueError(
                "The 'active_bidder' property of a Round object has to be a Player object which is included in the list of players in Round.players"
            )

        if p == self._active_bidder:
            raise ValueError("It can't be same player's bid twice in a row")

        self._active_bidder = p

    @property
    def round_loser(self):
        return self._round_loser

    @round_loser.setter
    def round_loser(self, p):
        if not isinstance(p, Player):
            raise TypeError(
                "The 'round_loser' property of a Round object has to be a Player object"
            )

        if p not in self._players:
            raise ValueError(
                "The 'round_loser' property of a Round object has to be a Player object which is included in the list of players in Round.players"
            )

        if self._round_loser is None:
            self._round_loser = p


class Player:
    """
    Holds the main properties & methods that a player needs. Has 2 sub-classes - Bot, and Human.
    """
    def __init__(self, name):
        if not isinstance(name, str):
            raise TypeError("The 'name' property of a Player object must be a string")
        if name == "":
            raise ValueError("Each player must have a name")
        self._name = name

        self._dice_left = 5
        self._hand = []

    def draw_hand(self):
        """
        Simulates a player rolling their dice
        """
        self._hand = []
        for _ in range(self._dice_left):
            self._hand.append(Die(random.randint(1, 6)))

    def stringify_hand(self):
        """
        Return a string, representing the player's hand.
        """
        if len(self._hand) > 0:
            return Die.stringify_dice(self.hand)
        else:
            return None

    def lose_a_die(self):
        """
        Decrements the player's dice by one, when they've lost the previous round
        """
        if self._dice_left > 0:
            self._dice_left -= 1

    @property
    def name(self):
        return self._name

    @property
    def dice_left(self):
        return self._dice_left

    @property
    def hand(self):
        return self._hand


class Bot(Player):
    """
    An instance of Bot represents one of the oponents that the user plays against.
    """
    @classmethod
    def _will_challenge(cls, active_bid, count_all_active_dice):
        """
        Decide whether to bid or challenge, with bias towards bidding
        """
        # Check args
        if not isinstance(count_all_active_dice, int):
            raise TypeError("Non-integer for count_all_active_dice")

        if not count_all_active_dice > 2:
            raise ValueError("count_all_active_dice must be > 2, or the game is over")

        # Decide
        if active_bid is None:
            return False

        if active_bid.die.face == 6 and active_bid.count == count_all_active_dice:
            return True
        else:
            # Turns out that random.choices() always returns a list (even if it has 1 element),
            # so the '[0]' part is necessary, in order to get the actual result
            return (random.choices([True, False], k=1, weights=[20, 80]))[0]

    @classmethod
    def _will_raise_by_face(cls, active_bid, count_all_active_dice):
        """
        Decide whether to raise the active_bid by face.
        If not - will have to raise by count.
        """
        # Check args
        if not isinstance(count_all_active_dice, int):
            raise TypeError("Non-integer for count_all_active_dice")

        if not count_all_active_dice > 2:
            raise ValueError("count_all_active_dice must be > 2, or the game is over")

        # Decide
        if active_bid is None:
            return True
        elif active_bid.die.face < 6 and active_bid.count == count_all_active_dice:
            return True
        elif active_bid.die.face == 6:
            return False
        else:
            # Turns out that random.choices() always returns a list (even if it has 1 element),
            # so the '[0]' part is necessary, in order to get the actual result
            return (random.choices([True, False], k=1))[0]

    def play_turn(self, active_bid, count_all_active_dice):
        """
        Represents a bot player playing their turn.
        Returns either a Bid object, or None (which means a challenge to the previous player's bid)
        """
        # Check args
        if not isinstance(count_all_active_dice, int):
            raise TypeError("Non-integer for count_all_active_dice")

        if not count_all_active_dice > 2:
            raise ValueError("count_all_active_dice must be > 2, or the game is over")

        # Decide to bid or challenge
        if Bot._will_challenge(active_bid, count_all_active_dice):
            return None

        # Formulate bid
        if Bot._will_raise_by_face(active_bid, count_all_active_dice):
            # Decide by which face to raise
            # Check which face has most occurences in own hand
            counts_in_hand = Counter([element.face for element in self._hand])

            # Check if face with most occurences in own hand suffices
            raised_face = None

            if active_bid is None:
                raised_face = counts_in_hand.most_common(1)[0][0]
                count_in_bid = counts_in_hand.most_common(1)[0][1]

                return Bid(
                    Die(raised_face), count_in_bid, active_bid, count_all_active_dice
                )
            else:

                for i in range(len(counts_in_hand)):
                    try:
                        f = counts_in_hand.most_common(i)[0][0]
                    except IndexError:
                        pass
                    else:
                        if f > active_bid.die.face:
                            raised_face = f
                            break

                if raised_face is None:
                    raised_face = active_bid.die.face + 1

                return Bid(Die(raised_face), 1, active_bid, count_all_active_dice)
        else:
            raised_count = random.randint(active_bid.count + 1, count_all_active_dice)

            return Bid(active_bid.die, raised_count, active_bid, count_all_active_dice)


class Human(Player):
    """
    A sub class of Player that represents the user.
    Doesn't implement any methods as of now, but is used to differentiate between players.
    """
    pass


class Game:
    """
    An instance a of Game represents a game of "Liar's dice".
    """
    def __init__(self, wild_1s):
        if not isinstance(wild_1s, bool):
            raise TypeError(
                "The 'wild_1s' property of a Game instance has to be Boolean"
            )
        self._wild_1s = wild_1s

        self._players = None
        self._rounds = []
        self._winner = None

    def __str__(self):
        if len(self._players) == 0 or len(self._rounds) == 0:
            return f"The game hasn't started yet"

        if self._winner is None:
            return f"The game is in round #{(self.rounds[len(self.rounds) - 1]).number} - there is still no winner"
        else:
            return f"The game ended in round #{(self.rounds[len(self.rounds) - 1]).number} - the winner is {self.winner}"

    def _get_first_round(self):
        """
        Helper to .add_round(). Returns round 1#.
        """
        # Determine round number
        round_number = 1

        # Determine players
        players_in_round = self.players
        if players_in_round is None or len(players_in_round) < 2:
            raise Exception(
                "For a round to start, there need to be > 2 players in the game"
            )

        # Determine turn
        whose_turn = players_in_round[0]

        return Round(round_number, players_in_round, whose_turn)

    def _get_n_th_round(self):
        """
        Helper to .add_round(). Returns a subsequent round round 1#.
        """
        # Determine round number
        previous_round = self.rounds[len(self.rounds) - 1]
        round_number = previous_round.number + 1

        # Determine players
        players_in_round = (previous_round.players).copy()

        if (previous_round.round_loser).dice_left < 1:
            players_in_round.remove(previous_round.round_loser)

        if players_in_round is None or len(players_in_round) < 2:
            raise Exception(
                "For a round to start, there need to be > 2 players in the game"
            )

        # Determine turn
        whose_turn = Round.determine_whose_turn_at_next_round(
            previous_round.players,
            previous_round.round_loser,
            previous_round.whose_turn,
        )

        return Round(round_number, players_in_round, whose_turn)

    def add_round(self):
        """
        Adds rounds to the game.rounds property of a Game instance.
        """
        if len(self.rounds) == 0:
            next_round = self._get_first_round()
        else:
            next_round = self._get_n_th_round()

        if isinstance(next_round, Round):
            self._rounds.append(next_round)
            return next_round

    def count_players_with_remaining_dice(self):
        count = 0
        for player in self._players:
            if player.dice_left > 0:
                count += 1

        return count

    @property
    def wild_1s(self):
        return self._wild_1s

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, players):
        for p in players:
            if not isinstance(p, Player):
                raise TypeError(
                    "The 'players' property of a Game object has to be a list of Player objects"
                )

        if not 5 >= len(players) >= 2:
            raise ValueError("A game can't have less than 2, and more than 5 players")

        if self._players is None:
            self._players = players
        else:
            raise Exception(
                "The players list can only be added once, at the start of the game"
            )

    @property
    def rounds(self):
        return self._rounds

    @property
    def winner(self):
        return self._winner

    @winner.setter
    def winner(self, p):
        if not isinstance(p, Player):
            raise TypeError(
                "The 'winner' property of a Game object has to be a Player object"
            )

        if not p in self._players:
            raise ValueError(
                "The 'winner' property of a Game object has to be a Player object included in the list in Game.players"
            )

        players_with_remaining_dice = self.count_players_with_remaining_dice()

        if players_with_remaining_dice > 1:
            raise Exception(
                "Can't produce a winner when more than 1 player has remaining dice"
            )
        elif players_with_remaining_dice < 1:
            raise Exception(
                "Can't produce a winner when more than all players have no remaining dice"
            )

        if p.dice_left < 1:
            raise Exception(
                "The Player object that you're trying to assign as winner has no remaining dice"
            )

        if self._winner is None:
            self._winner = p
