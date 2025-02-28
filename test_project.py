import pytest

from liarsdice import Bid, Die
from project import (
    _get_bid_face,
    _get_bid_count,
    get_bid_from_human,
    get_count_of_bots,
    prompt_boolean_question,
)
from unittest.mock import patch


def test__get_bid_face():
    some_inacceptable_answers = [7, 0, "", "!@#$", "qwerty"]
    for a in some_inacceptable_answers:
        with pytest.raises(StopIteration):
            with patch("builtins.input", side_effect=[str(a)]):
                _get_bid_face()

    with pytest.raises(SystemExit):
        with patch("builtins.input", side_effect=[EOFError]):
            _get_bid_face()

    mn = 1
    mx = 6
    acceptable_answers = range(mn, mx + 1)

    for a in acceptable_answers:
        with patch("builtins.input", side_effect=[str(a)]):
            assert _get_bid_face() == a


def test__get_bid_count():
    count_all_active_dice = 10
    some_inacceptable_answers = [0, "", "!@#$", "qwerty"]
    for a in some_inacceptable_answers:
        with pytest.raises(StopIteration):
            with patch("builtins.input", side_effect=[str(a)]):
                _get_bid_count(count_all_active_dice)

    with pytest.raises(StopIteration):
        with patch("builtins.input", side_effect=[str(count_all_active_dice + 1)]):
            _get_bid_count(count_all_active_dice)

    with pytest.raises(SystemExit):
        with patch("builtins.input", side_effect=[EOFError]):
            _get_bid_count(count_all_active_dice)

    mn = 1
    mx = count_all_active_dice
    acceptable_answers = range(mn, mx + 1)

    for a in acceptable_answers:
        with patch("builtins.input", side_effect=[str(a)]):
            assert _get_bid_count(count_all_active_dice) == a


def test_get_bid_from_human_default_case_only():
    active_bid = Bid(Die(3), 3)
    count_all_active_dice = 10

    with patch("project._get_bid_face", return_value=3), patch(
        "project._get_bid_count", return_value=4
    ):
        assert (
            isinstance(get_bid_from_human(active_bid, count_all_active_dice), Bid)
            == True
        )

    with patch("project._get_bid_face", return_value=4), patch(
        "project._get_bid_count", return_value=3
    ):
        assert (
            isinstance(get_bid_from_human(active_bid, count_all_active_dice), Bid)
            == True
        )


def test_get_count_of_bots():
    some_inacceptable_answers = [5, 0, "", "!@#$", "qwerty"]
    for a in some_inacceptable_answers:
        with pytest.raises(StopIteration):
            with patch("builtins.input", side_effect=[str(a)]):
                get_count_of_bots()

    with pytest.raises(SystemExit):
        with patch("builtins.input", side_effect=[EOFError]):
            get_count_of_bots()

    mn = 1
    mx = 4
    acceptable_answers = range(mn, mx + 1)

    for a in acceptable_answers:
        with patch("builtins.input", side_effect=[str(a)]):
            assert get_count_of_bots() == a


def test_prompt_boolean_question():
    some_inacceptable_answers = ["n", "N", "no", "nO", "0", "", "False", "false"]

    for a in some_inacceptable_answers:
        with patch("builtins.input", side_effect=[a]):
            assert prompt_boolean_question("") == False

    some_acceptable_answers = [
        "y",
        "y       ",
        "       y",
        "yes",
        "Y",
        "Yes",
        "1",
        "True",
        "true",
    ]

    for a in some_acceptable_answers:
        with patch("builtins.input", side_effect=[a]):
            assert prompt_boolean_question("") == True
