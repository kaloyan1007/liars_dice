import pytest

from liarsdice import Bid, Bot, Die, Game, Human, Player, Round
from unittest.mock import patch, PropertyMock


# Tests for Die class
def test_die_init_default_case():
    for i in range(1, 6):
        assert isinstance(Die(i), Die)


def test_die_init_no_args():
    # Should raise "TypeError: Die.__init__() missing 1 required positional arguments: 'face'"
    with pytest.raises(TypeError):
        Die()


def test_die_stringify_dice_bad_input():
    with pytest.raises(TypeError):
        Die.stringify_dice(1)

    with pytest.raises(TypeError):
        Die.stringify_dice("1")

    with pytest.raises(TypeError):
        Die.stringify_dice(None)

    with pytest.raises(ValueError):
        Die.stringify_dice([])

    with pytest.raises(TypeError):
        Die.stringify_dice([Die(1), 1])

    with pytest.raises(TypeError):
        Die.stringify_dice([Die(1), "1"])

    with pytest.raises(TypeError):
        Die.stringify_dice([Die(1), None])


def test_die_init_invalid_face():
    with pytest.raises(TypeError):
        Die(None)

    with pytest.raises(ValueError):
        Die(-1)

    with pytest.raises(ValueError):
        Die(0)

    with pytest.raises(ValueError):
        Die(7)

    with pytest.raises(TypeError):
        Die(3.0)

    with pytest.raises(TypeError):
        Die("foo")

    with pytest.raises(TypeError):
        Die("1")


# Tests for Bid class
def test_bid_init_default_case():
    for i in range(1, 6):
        assert isinstance(Bid(Die(i), 3), Bid)

    bid_small = Bid(Die(1), 1)

    for i in range(1, 6):
        assert isinstance(Bid(Die(i), 4, active_bid=bid_small), Bid)

    for i in range(1, 6):
        assert isinstance(
            Bid(Die(i), 4, active_bid=bid_small, count_all_active_dice=5), Bid
        )

    for i in range(1, 6):
        assert isinstance(
            Bid(Die(i), 5, active_bid=bid_small, count_all_active_dice=5), Bid
        )


def test_bid_init_no_args():
    with pytest.raises(TypeError):
        Bid()


def test_bid_init_invalid_face():
    for i in range(1, 6):
        with pytest.raises(TypeError):
            Bid(i, 3)

    with pytest.raises(TypeError):
        Bid(None, 3)

    with pytest.raises(TypeError):
        Bid(-1, 3)

    with pytest.raises(TypeError):
        Bid(0, 3)

    with pytest.raises(TypeError):
        Bid(7, 3)

    with pytest.raises(TypeError):
        Bid(3.0, 3)

    with pytest.raises(TypeError):
        Bid("foo", 3)

    with pytest.raises(TypeError):
        Bid("1", 3)


def test_bid_init_invalid_count():
    with pytest.raises(TypeError):
        Bid(Die(1), None)

    with pytest.raises(ValueError):
        Bid(Die(1), -1)

    with pytest.raises(ValueError):
        Bid(Die(1), 0)

    with pytest.raises(TypeError):
        Bid(Die(1), 3.0)

    with pytest.raises(TypeError):
        Bid(Die(1), "foo")

    with pytest.raises(TypeError):
        Bid(Die(1), "1")


def test_bid_init_less_than_or_equals_active_bid():
    active_bid = Bid(Die(2), 4)

    with pytest.raises(ValueError):
        Bid(Die(1), 4, active_bid=active_bid)

    with pytest.raises(ValueError):
        Bid(Die(1), 5, active_bid=active_bid)

    with pytest.raises(ValueError):
        Bid(Die(2), 3, active_bid=active_bid)

    with pytest.raises(ValueError):
        Bid(Die(2), 4, active_bid=active_bid)


def test_bid_init_more_than_count_all_active_dice():
    with pytest.raises(ValueError):
        Bid(Die(1), 11, count_all_active_dice=10)


def test_bid_init_bad_count_all_active_dice():
    with pytest.raises(ValueError):
        Bid(Die(1), 11, count_all_active_dice=1)

    with pytest.raises(ValueError):
        Bid(Die(1), 11, count_all_active_dice=-1)

    with pytest.raises(ValueError):
        Bid(Die(1), 11, count_all_active_dice=0)

    with pytest.raises(TypeError):
        Bid(Die(1), 11, count_all_active_dice=5.0)

    with pytest.raises(TypeError):
        Bid(Die(1), 11, count_all_active_dice="5")


def test_bid_is_higher():
    assert Bid.is_higher(Bid(Die(1), 2), Bid(Die(1), 1)) == True
    assert Bid.is_higher(Bid(Die(1), 1), Bid(Die(1), 2)) == False

    assert Bid.is_higher(Bid(Die(2), 1), Bid(Die(1), 1)) == True
    assert Bid.is_higher(Bid(Die(1), 1), Bid(Die(2), 1)) == False

    assert Bid.is_higher(Bid(Die(2), 1), Bid(Die(1), 2)) == True
    assert Bid.is_higher(Bid(Die(1), 1), Bid(Die(2), 1)) == False

    assert Bid.is_higher(Bid(Die(2), 2), Bid(Die(1), 1)) == True
    assert Bid.is_higher(Bid(Die(1), 1), Bid(Die(2), 2)) == False

    for i in range(1, 6):
        assert Bid.is_higher(Bid(Die(i), i), Bid(Die(i), i)) == False


# Tests for Player class
def test_player_init_default_case():
    assert isinstance(Player("1"), Player)
    assert isinstance(Player("Player 1"), Player)


def test_player_init_no_args():
    with pytest.raises(TypeError):
        Player()


def test_player_draw_hand():
    p = Player("Player1")
    p.draw_hand()

    assert len(p.hand) == p.dice_left

    for d in p.hand:
        assert isinstance(d, Die)


def test_player_lose_a_die():
    p = Player("Player1")

    for i in range(1, 5):
        p.lose_a_die()
        assert p.dice_left == 5 - i

    p.lose_a_die()
    p.lose_a_die()
    p.lose_a_die()
    assert p.dice_left == 0


# Tests for Bot class
def test_bot__will_challenge_default_case():
    assert Bot._will_challenge(None, 5) == False

    max_bid = Bid(Die(6), 5, None, 5)
    assert Bot._will_challenge(max_bid, 5) == True

    with patch("random.choices", return_value=[True]):
        assert Bot._will_challenge(Bid(Die(5), 3, None, 5), 5) == True

    with patch("random.choices", return_value=[False]):
        assert Bot._will_challenge(Bid(Die(5), 3, None, 5), 5) == False


def test_bot__will_challenge_bad_count_all_active_dice():
    active_bid = Bid(Die(5), 1, None, 5)

    with pytest.raises(ValueError):
        Bot._will_challenge(active_bid, 1)

    with pytest.raises(ValueError):
        Bot._will_challenge(active_bid, -1)

    with pytest.raises(ValueError):
        Bot._will_challenge(active_bid, 0)

    with pytest.raises(TypeError):
        Bot._will_challenge(active_bid, None)

    with pytest.raises(TypeError):
        Bot._will_challenge(active_bid, 5.0)

    with pytest.raises(TypeError):
        Bot._will_challenge(active_bid, "5")


def test_bot__will_raise_by_face_default_case():
    b1 = Bid(Die(1), 5, None, 5)
    assert Bot._will_raise_by_face(b1, 5) == True

    b2 = Bid(Die(6), 3, None, 5)
    assert Bot._will_raise_by_face(b2, 5) == False

    max_bid = Bid(Die(6), 5, None, 5)
    assert Bot._will_raise_by_face(max_bid, 5) == False

    with patch("random.choices", return_value=[True]):
        assert Bot._will_raise_by_face(Bid(Die(5), 3, None, 5), 5) == True

    with patch("random.choices", return_value=[False]):
        assert Bot._will_raise_by_face(Bid(Die(5), 3, None, 5), 5) == False


def test_bot__will_raise_by_face_missing_active_bid():
    # with pytest.raises(AttributeError):
    #     Bot._will_raise_by_face(None, 5)
    assert Bot._will_raise_by_face(None, 5) == True


def test_bot__will_raise_by_face_bad_count_all_active_dice():
    active_bid = Bid(Die(5), 1, None, 5)

    with pytest.raises(ValueError):
        Bot._will_raise_by_face(active_bid, 1)

    with pytest.raises(ValueError):
        Bot._will_raise_by_face(active_bid, -1)

    with pytest.raises(ValueError):
        Bot._will_raise_by_face(active_bid, 0)

    with pytest.raises(TypeError):
        Bot._will_raise_by_face(active_bid, None)

    with pytest.raises(TypeError):
        Bot._will_raise_by_face(active_bid, 5.0)

    with pytest.raises(TypeError):
        Bot._will_raise_by_face(active_bid, "5")


def test_bot_play_turn_challenge():
    bot = Bot("Bot1")

    max_bid = Bid(Die(6), 5, None, 5)
    assert bot.play_turn(max_bid, 5) == None

    with patch("random.choices", return_value=[True]):
        assert bot.play_turn(Bid(Die(5), 3, None, 5), 5) == None


def test_bot_play_turn_raise():
    bot = Bot("Bot1")
    type(bot)._dice_left = PropertyMock(return_value=3)
    type(bot)._hand = PropertyMock(return_value=[Die(1), Die(2), Die(3)])

    active_bid = None
    assert isinstance(bot.play_turn(active_bid, 5), Bid)

    with patch("random.choices", return_value=[False]):
        for i in range(1, 6):
            for j in range(1, 5):
                if not (i == 6 and j == 5):
                    active_bid = Bid(Die(i), j, None, 5)
                    assert (
                        Bid.is_higher(bot.play_turn(active_bid, 5), active_bid) == True
                    )


def test_bot_play_turn_bad_count_all_active_dice():
    active_bid = Bid(Die(5), 1, None, 5)

    bot = Bot("Bot1")

    with pytest.raises(ValueError):
        bot.play_turn(active_bid, 1)

    with pytest.raises(ValueError):
        bot.play_turn(active_bid, -1)

    with pytest.raises(ValueError):
        bot.play_turn(active_bid, 0)

    with pytest.raises(TypeError):
        bot.play_turn(active_bid, None)

    with pytest.raises(TypeError):
        bot.play_turn(active_bid, 5.0)

    with pytest.raises(TypeError):
        bot.play_turn(active_bid, "5")


# Tests for Round class
def test_round_init_default_case():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")

    players = [p2, p3]
    assert isinstance(Round(1, players, p1), Round)
    players.append(p1)
    assert isinstance(Round(2, players, p2), Round)


def test_round_init_no_args():
    with pytest.raises(TypeError):
        Round()


def test_round_init_bad_players():
    p1 = Human("Player1")
    with pytest.raises(TypeError):
        Round(1, None, p1)

    with pytest.raises(ValueError):
        Round(1, [], p1)

    with pytest.raises(ValueError):
        Round(1, [p1], p1)

    with pytest.raises(TypeError):
        Round(1, [p1, 2], p1)

    with pytest.raises(TypeError):
        Round(1, [p1, "Player4"], p1)

    p2 = Bot("Bot1")
    with pytest.raises(TypeError):
        Round(1, [p1, p2, 2], p1)

    with pytest.raises(TypeError):
        Round(1, [p1, p2, "Player4"], p1)

    p3 = Bot("Bot2")
    with pytest.raises(TypeError):
        Round(1, [p1, p2, p3, 2], p1)

    with pytest.raises(TypeError):
        Round(1, [p1, p2, p3, "Player4"], p1)
        Round()


def test_round_init_bad_whose_turn():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")

    with pytest.raises(TypeError):
        Round(1, [p1, p2, p3], None)

    with pytest.raises(TypeError):
        Round(1, [p1, p2, p3], "Player3")

    with pytest.raises(TypeError):
        Round(1, [p1, p2, p3], 3)


def test_round_determine_index_of_next():
    players = [Human("Player1"), Bot("Bot1"), Bot("Bot2"), Bot("Bot3")]

    expected_turns_by_index = [
        {"prev": 0, "next": 1},
        {"prev": 1, "next": 2},
        {"prev": 2, "next": 3},
        {"prev": 3, "next": 0},
        {"prev": 0, "next": 1},
        {"prev": 1, "next": 2},
        {"prev": 2, "next": 3},
        {"prev": 3, "next": 0},
        {"prev": 0, "next": 1},
        {"prev": 1, "next": 2},
        {"prev": 2, "next": 3},
        {"prev": 3, "next": 0},
    ]
    for turn in expected_turns_by_index:
        assert (
            Round.determine_index_of_next(players, players[turn["prev"]])
            == turn["next"]
        )


def test_round__return_next():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")
    p4 = Bot("Bot3")
    players = [p1, p2, p3, p4]

    # Case: last round was loser's turn
    assert Round._return_next(players, p1, p1) == p2
    assert Round._return_next(players, p2, p2) == p3
    assert Round._return_next(players, p3, p3) == p4
    assert Round._return_next(players, p4, p4) == p1

    # Case: last round was (loser - 1)'s turn
    assert Round._return_next(players, p1, p4) == p2
    assert Round._return_next(players, p2, p1) == p3
    assert Round._return_next(players, p3, p2) == p4
    assert Round._return_next(players, p4, p3) == p1

    # Case: last round was (loser + 1)'s turn
    assert Round._return_next(players, p1, p2) == p3
    assert Round._return_next(players, p2, p3) == p4
    assert Round._return_next(players, p3, p4) == p1
    assert Round._return_next(players, p4, p1) == p2


def test_round_determine_whose_turn_at_next_round():
    p1 = Human("Player1")
    players = []

    with pytest.raises(Exception):
        Round.determine_whose_turn_at_next_round(players, p1, p1)

    players.append(p1)

    with pytest.raises(Exception):
        Round.determine_whose_turn_at_next_round(players, p1, p1)

    p2 = Bot("Bot1")
    players.append(p2)

    assert Round.determine_whose_turn_at_next_round(players, p1, p1) == p1
    assert Round.determine_whose_turn_at_next_round(players, p1, p2) == p1
    assert Round.determine_whose_turn_at_next_round(players, p2, p1) == p2
    assert Round.determine_whose_turn_at_next_round(players, p2, p2) == p2

    p3 = Bot("Bot2")
    players.append(p3)

    with pytest.raises(Exception):
        Round.determine_whose_turn_at_next_round(players, None, None)
    with pytest.raises(Exception):
        Round.determine_whose_turn_at_next_round(players, p1, None)
    with pytest.raises(Exception):
        Round.determine_whose_turn_at_next_round(players, None, p1)

    type(p3)._dice_left = PropertyMock(return_value=5)
    assert Round.determine_whose_turn_at_next_round(players, p3, p1) == p3
    # The other cases are covered in test_round__return_next(),
    # as they depend on the Round._return_next() method


def test_round_rotate_turn():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")

    r = Round(1, [p1, p2, p3], p1)

    expected_turns = [p2, p3, p1, p2, p3, p1, p2, p3, p1]
    for p in expected_turns:
        r.rotate_turn()
        assert r.whose_turn == p


def test_round_whose_turn_setter():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")

    r = Round(1, [p1, p2, p3], p1)

    with pytest.raises(TypeError):
        r.whose_turn = None

    with pytest.raises(TypeError):
        r.whose_turn = "Bot1"

    with pytest.raises(TypeError):
        r.whose_turn = 2

    p4 = Bot("Bot3")
    with pytest.raises(ValueError):
        r.whose_turn = p4

    with pytest.raises(ValueError):
        r.whose_turn = p1

    r.whose_turn = p2
    assert r.whose_turn == p2


def test_round_active_bid_setter():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")

    r = Round(1, [p1, p2, p3], p1)

    with pytest.raises(TypeError):
        r.active_bid = None

    with pytest.raises(TypeError):
        r.active_bid = "Bot1"

    with pytest.raises(TypeError):
        r.active_bid = 2

    with pytest.raises(TypeError):
        r.active_bid = p1

    b1 = Bid(Die(5), 2, None, 5)
    r.active_bid = b1
    assert r.active_bid == b1

    b2 = Bid(Die(5), 3, None, 5)
    r.active_bid = b2
    assert r.active_bid == b2

    type(r)._active_bid = PropertyMock(return_value=b1)
    with pytest.raises(ValueError):
        r.active_bid = Bid(Die(5), 1, None, 5)

    with pytest.raises(ValueError):
        r.active_bid = b1

    with pytest.raises(ValueError):
        r.active_bid = Bid(Die(4), 3, None, 5)


def test_round_active_bidder_setter():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")

    r = Round(1, [p1, p2, p3], p1)

    with pytest.raises(TypeError):
        r.active_bidder = None

    with pytest.raises(TypeError):
        r.active_bidder = "Bot1"

    with pytest.raises(TypeError):
        r.active_bidder = 2

    p4 = Bot("Bot3")
    with pytest.raises(ValueError):
        r.active_bidder = p4

    r.active_bidder = p1
    assert r.active_bidder == p1

    type(r)._active_bidder = PropertyMock(return_value=p1)
    with pytest.raises(ValueError):
        r.active_bidder = p1


def test_round_round_loser_setter():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")

    r = Round(1, [p1, p2, p3], p1)

    with pytest.raises(TypeError):
        r.round_loser = None

    with pytest.raises(TypeError):
        r.round_loser = "Bot1"

    with pytest.raises(TypeError):
        r.round_loser = 2

    p4 = Bot("Bot3")
    with pytest.raises(ValueError):
        r.round_loser = p4

    r.round_loser = p1
    assert r.round_loser == p1

    type(r)._round_loser = PropertyMock(return_value=p1)
    r.round_loser = p3
    assert r.round_loser == p1


def test_round_draw_hands():
    with patch.object(
        Round, "players", new_callable=PropertyMock
    ) as mock_players, patch.object(
        Player, "dice_left", new_callable=PropertyMock
    ) as mock_dice_left:
        p1 = Human("Player1")
        p2 = Bot("Bot1")
        p3 = Bot("Bot2")

        r = Round(1, [p1, p2, p3], p1)

        mock_players.return_value = None
        with pytest.raises(Exception):
            r.draw_hands()

        mock_players.return_value = [p1]
        with pytest.raises(Exception):
            r.draw_hands()

        mock_players.return_value = [p1, p2, p3]
        mock_dice_left.return_value = 5
        r.draw_hands()

        for p in r.players:
            assert isinstance(p.hand, list)
            assert len(p.hand) > 0

            for d in p.hand:
                assert isinstance(d, Die)


def test_round_evaluate_challenge():
    # Basic setup
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")

    r = Round(1, [p1, p2, p3], p1)

    b1 = Bid(Die(5), 3, None, 15)

    type(r)._active_bid = PropertyMock(return_value=b1)
    type(r)._active_bidder = PropertyMock(return_value=p1)

    # Test successful challenge - classic rules
    type(p1)._hand = PropertyMock(return_value=[Die(2), Die(2), Die(2), Die(2), Die(2)])
    type(p2)._hand = PropertyMock(return_value=[Die(2), Die(2), Die(2), Die(2), Die(2)])
    type(p3)._hand = PropertyMock(return_value=[Die(2), Die(2), Die(2), Die(2), Die(2)])

    assert r.evaluate_challenge(b1, False) == True

    # Test successful challenge - wild 1s
    type(p1)._hand = PropertyMock(return_value=[Die(1), Die(2), Die(2), Die(2), Die(2)])
    p2._hand = [Die(1), Die(2), Die(2), Die(2), Die(2)]
    p3._hand = [Die(2), Die(2), Die(2), Die(2), Die(2)]

    assert r.evaluate_challenge(b1, True) == True

    # Test unsuccessful challenge - classic rules
    type(p1)._hand = PropertyMock(return_value=[Die(5), Die(2), Die(2), Die(2), Die(2)])
    type(p2)._hand = PropertyMock(return_value=[Die(5), Die(2), Die(2), Die(2), Die(2)])
    type(p3)._hand = PropertyMock(return_value=[Die(5), Die(2), Die(2), Die(2), Die(2)])

    assert r.evaluate_challenge(b1, False) == False

    type(p1)._hand = PropertyMock(return_value=[Die(5), Die(5), Die(2), Die(2), Die(2)])
    type(p2)._hand = PropertyMock(return_value=[Die(5), Die(2), Die(2), Die(2), Die(2)])
    type(p3)._hand = PropertyMock(return_value=[Die(5), Die(2), Die(2), Die(2), Die(2)])

    assert r.evaluate_challenge(b1, False) == False

    # Test unsuccessful challenge - wild 1s
    type(p1)._hand = PropertyMock(return_value=[Die(5), Die(2), Die(2), Die(2), Die(2)])
    p2._hand = [Die(5), Die(2), Die(2), Die(2), Die(2)]
    p3._hand = [Die(1), Die(2), Die(2), Die(2), Die(2)]

    assert r.evaluate_challenge(b1, True) == False

    type(p1)._hand = PropertyMock(return_value=[Die(5), Die(2), Die(2), Die(2), Die(2)])
    type(p2)._hand = PropertyMock(return_value=[Die(1), Die(2), Die(2), Die(2), Die(2)])
    type(p3)._hand = PropertyMock(return_value=[Die(1), Die(2), Die(2), Die(2), Die(2)])

    assert r.evaluate_challenge(b1, True) == False

    type(p1)._hand = PropertyMock(return_value=[Die(1), Die(2), Die(2), Die(2), Die(2)])
    type(p2)._hand = PropertyMock(return_value=[Die(1), Die(2), Die(2), Die(2), Die(2)])
    type(p3)._hand = PropertyMock(return_value=[Die(1), Die(2), Die(2), Die(2), Die(2)])

    assert r.evaluate_challenge(b1, True) == False


def test_round_get_count_of_all_active_dice():
    with patch.object(Player, "dice_left", new_callable=PropertyMock) as mock_dice_left:
        p1 = Human("Player1")
        p2 = Bot("Bot1")
        p3 = Bot("Bot2")

        r = Round(1, [p1, p2, p3], p1)

        mock_dice_left.return_value = 5
        assert r.get_count_of_all_active_dice() == 15

        mock_dice_left.return_value = 0
        assert r.get_count_of_all_active_dice() == 0


# Tests for Game class
def test_game_init_default_case():
    assert isinstance(Game(True), Game)
    assert isinstance(Game(False), Game)


def test_game_init_no_args():
    with pytest.raises(TypeError):
        Game()


def test_game_init_bad_wild_1s():
    with pytest.raises(TypeError):
        Game("yes")

    with pytest.raises(TypeError):
        Game(1)

    with pytest.raises(TypeError):
        Game(0)

    with pytest.raises(TypeError):
        Game(1.0)


def test_game__get_first_round():
    p1 = Human("Player1")
    p2 = Bot("Bot1")

    with patch.object(Game, "players", new_callable=PropertyMock) as mock_players:
        game = Game(False)

        mock_players.return_value = None

        with pytest.raises(Exception):
            game._get_first_round()

        mock_players.return_value = [p1]

        game = Game(False)
        with pytest.raises(Exception):
            game._get_first_round()

        mock_players.return_value = [p1, p2]

        r = game._get_first_round()
        assert isinstance(r, Round)
        assert r.number == 1
        assert r.players == [p1, p2]


def test_game__get_n_th_round():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")
    p4 = Bot("Bot3")

    with patch.object(
        Game, "players", new_callable=PropertyMock
    ) as mock_players, patch.object(
        Game, "rounds", new_callable=PropertyMock
    ) as mock_rounds:
        game = Game(False)

        mock_players.return_value = None

        with pytest.raises(Exception):
            game._get_n_th_round()

        mock_players.return_value = [p1]

        game = Game(False)
        with pytest.raises(Exception):
            game._get_n_th_round()

        mock_players.return_value = [p1, p2, p3, p4]

        with patch.object(
            Round, "round_loser", new_callable=PropertyMock
        ) as round_loser_players:
            r1 = Round(1, game.players, p3)
            round_loser_players.return_value = p1

            mock_rounds.return_value = [r1]

            r2 = game._get_n_th_round()
            assert isinstance(r2, Round)
            assert r2.number == 2
            assert r2.players == [p1, p2, p3, p4]


def test_game_add_round():
    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")
    p4 = Bot("Bot3")

    with patch.object(Game, "players", new_callable=PropertyMock) as mock_players:
        game = Game(False)

        mock_players.return_value = None

        with pytest.raises(Exception):
            game.add_round()

        mock_players.return_value = [p1]

        game = Game(False)
        with pytest.raises(Exception):
            game.add_round()

        mock_players.return_value = [p1, p2, p3, p4]

        for i in range(1, 11):
            r = game.add_round()
            assert isinstance(r, Round)
            assert r.number == i


def test_game_count_players_with_remaining_dice():
    game = Game(False)

    p1 = Human("Player1")
    p2 = Bot("Bot1")

    with pytest.raises(TypeError):
        game.count_players_with_remaining_dice()

    game.players = [p1, p2]
    assert game.count_players_with_remaining_dice() == 2

    type(p1)._dice_left = PropertyMock(return_value=0)
    type(p2)._dice_left = PropertyMock(return_value=0)
    assert game.count_players_with_remaining_dice() == 0

    type(p1)._dice_left = PropertyMock(return_value=1)
    type(p2)._dice_left = PropertyMock(return_value=0)
    assert game.count_players_with_remaining_dice() == 1

    type(p1)._dice_left = PropertyMock(return_value=0)
    type(p2)._dice_left = PropertyMock(return_value=1)
    assert game.count_players_with_remaining_dice() == 1


def test_game_players_setter():
    game = Game(False)

    p1 = Human("Player1")
    p2 = Bot("Bot1")

    with pytest.raises(ValueError):
        game.players = []

    with pytest.raises(TypeError):
        game.players = [None]

    with pytest.raises(TypeError):
        game.players = [p1, p2, None]

    with pytest.raises(TypeError):
        game.players = [p1, p2, False]

    with pytest.raises(TypeError):
        game.players = [p1, p2, 2]

    with pytest.raises(TypeError):
        game.players = [p1, p2, "Player4"]

    with pytest.raises(ValueError):
        game.players = [p1]

    p3 = Bot("Bot2")
    p4 = Bot("Bot3")
    p5 = Bot("Bot4")
    p6 = Bot("Bot5")

    with pytest.raises(ValueError):
        game.players = [p1, p2, p3, p4, p5, p6]

    game.players = [p1, p2, p3, p4, p5]
    assert game.players == [p1, p2, p3, p4, p5]

    with pytest.raises(Exception):
        game.players = [p1, p2]

    # Using private property accessor because PropertyMock seems to block the setter
    game._players = None
    game.players = [p1, p2]
    assert game.players == [p1, p2]


def test_game_winner_setter():
    game = Game(False)

    p1 = Human("Player1")
    p2 = Bot("Bot1")
    p3 = Bot("Bot2")

    type(game)._players = PropertyMock(return_value=[p1, p2, p3])

    with pytest.raises(TypeError):
        game.winner = None

    with pytest.raises(TypeError):
        game.winner = "Bot1"

    with pytest.raises(TypeError):
        game.winner = 2

    p4 = Bot("Bot3")
    with pytest.raises(ValueError):
        game.winner = p4

    type(p1)._dice_left = PropertyMock(return_value=1)
    type(p2)._dice_left = PropertyMock(return_value=1)
    type(p3)._dice_left = PropertyMock(return_value=1)
    with pytest.raises(Exception):
        game.winner = p1

    # When using type() in conjunction with PropertyMock(return_value=1),
    # this actually sets the property to the same return value for every instance
    # of that class.
    # So, in the above lines there is no point in setting it for both p2 and p3,
    # (as they are instances of the same class) other than to be explicit.
    # In the below lines, however we want the p2 and p3 to have different values
    # for their 'dice_left' properties.
    # The simplest way to do this is to use the private '_dice_left' properties

    p1._dice_left = 1
    p2._dice_left = 1
    p3._dice_left = 0
    with pytest.raises(Exception):
        game.winner = p1

    type(p1)._dice_left = PropertyMock(return_value=0)
    type(p2)._dice_left = PropertyMock(return_value=0)
    type(p3)._dice_left = PropertyMock(return_value=0)
    with pytest.raises(Exception):
        game.winner = p1

    type(p1)._dice_left = PropertyMock(return_value=1)
    type(p2)._dice_left = PropertyMock(return_value=0)
    type(p3)._dice_left = PropertyMock(return_value=0)
    with pytest.raises(Exception):
        game.winner = p3

    type(p1)._dice_left = PropertyMock(return_value=1)
    type(p2)._dice_left = PropertyMock(return_value=0)
    type(p3)._dice_left = PropertyMock(return_value=0)
    game.winner = p1
    assert game.winner == p1
