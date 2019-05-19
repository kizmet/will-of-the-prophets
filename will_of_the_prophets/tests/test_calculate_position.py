"""Test calculate_position."""

from datetime import datetime

import pytest
from model_mommy import mommy
from pytz import utc

from will_of_the_prophets import board, models


@pytest.fixture(autouse=True)
def clear_caches():
    board.clear_caches()


@pytest.mark.django_db
def test_zero_rolls():
    """Test with zero rolls."""
    assert models.Roll.objects.count() == 0
    assert board.calculate_position(utc.localize(datetime(2369, 7, 5, 8))) == 1


@pytest.mark.django_db
def test_one_roll():
    """Test with one roll."""
    mommy.make("Roll", number=22, embargo=utc.localize(datetime(2369, 7, 1)))
    assert board.calculate_position(utc.localize(datetime(2369, 1, 1))) == 1
    assert board.calculate_position(utc.localize(datetime(2369, 12, 31))) == 23


@pytest.mark.django_db
def test_many_rolls():
    """Test with many rolls."""
    for day_of_month, roll in enumerate([3, 20, 2, 40, 17, 5]):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    assert board.calculate_position(utc.localize(datetime(2369, 7, 1, 1))) == 4
    assert board.calculate_position(utc.localize(datetime(2369, 7, 6, 1))) == 88


@pytest.mark.django_db
def test_butthole():
    """Test that a butthole has an effect."""
    mommy.make("Butthole", start_square=88, end_square=5)

    # Create some rolls.
    for day_of_month, roll in enumerate([3, 20, 2, 40, 17, 5, 2]):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    assert board.calculate_position(utc.localize(datetime(2369, 7, 10))) == 7


@pytest.mark.django_db
def test_butthole_before_effective():
    """Test that a butthole has no effect before it's time frame has started."""
    # Make a butthole which isn't effective until the end of July.
    mommy.make(
        "Butthole",
        start_square=88,
        end_square=5,
        start=utc.localize(datetime(2369, 8, 1)),
    )

    # Create some rolls, all which take place in July.
    for day_of_month, roll in enumerate([3, 20, 2, 40, 17, 5, 2]):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    # Assert that calculate_position doesn't take the butthole into consideration.
    assert board.calculate_position(utc.localize(datetime(2369, 7, 5, 1))) == 83
    assert board.calculate_position(utc.localize(datetime(2369, 7, 6, 1))) == 88
    assert board.calculate_position(utc.localize(datetime(2369, 7, 7, 1))) == 90


@pytest.mark.django_db
def test_butthole_after_effective():
    """Test that a butthole has no effect after it's time frame has passed."""
    # Make a butthole which is effective until the start of July.
    mommy.make(
        "Butthole",
        start_square=88,
        end_square=5,
        end=utc.localize(datetime(2369, 7, 1)),
    )

    # Create some rolls, all which take place in July.
    for day_of_month, roll in enumerate([3, 20, 2, 40, 17, 5, 2]):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    # Assert that calculate_position doesn't take the butthole into consideration.
    assert board.calculate_position(utc.localize(datetime(2369, 7, 5, 1))) == 83
    assert board.calculate_position(utc.localize(datetime(2369, 7, 6, 1))) == 88
    assert board.calculate_position(utc.localize(datetime(2369, 7, 7, 1))) == 90


@pytest.mark.django_db
def test_special_square_auto_move_positive():
    """Test a special square can move the runabout forwards."""
    # Make a special square which moves the runabout forward five spaces.
    mommy.make("SpecialSquare", square=24, type__auto_move=5, type__image="")

    # Create some rolls.
    for day_of_month, roll in enumerate([3, 20, 2]):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    # Assert that calculate_position takes the special square into
    # consideration.
    assert board.calculate_position(utc.localize(datetime(2369, 7, 1, 1))) == 4
    assert board.calculate_position(utc.localize(datetime(2369, 7, 2, 1))) == 29
    assert board.calculate_position(utc.localize(datetime(2369, 7, 3, 1))) == 31


@pytest.mark.django_db
def test_special_square_auto_move_negative():
    """Test a special square can move the runabout backwards."""
    # Make a special square which moves the runabout backward five spaces.
    mommy.make("SpecialSquare", square=24, type__auto_move=-5, type__image="")

    # Create some rolls.
    for day_of_month, roll in enumerate([3, 20, 2]):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    # Assert that calculate_position takes the special square into
    # consideration.
    assert board.calculate_position(utc.localize(datetime(2369, 7, 1, 1))) == 4
    assert board.calculate_position(utc.localize(datetime(2369, 7, 2, 1))) == 19
    assert board.calculate_position(utc.localize(datetime(2369, 7, 3, 1))) == 21


@pytest.mark.django_db
def test_special_square_before_effective():
    """Test that a special square has no effect before it's time frame has started."""
    # Make a special square which isn't effective until the end of July.
    mommy.make(
        "SpecialSquare",
        square=24,
        type__auto_move=5,
        type__image="",
        start=utc.localize(datetime(2369, 8, 1)),
    )

    # Create some rolls, all which take place in July.
    for day_of_month, roll in enumerate([3, 20, 2]):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    # Assert that calculate_position doesn't take the special square into consideration.
    assert board.calculate_position(utc.localize(datetime(2369, 7, 1, 1))) == 4
    assert board.calculate_position(utc.localize(datetime(2369, 7, 2, 1))) == 24
    assert board.calculate_position(utc.localize(datetime(2369, 7, 3, 1))) == 26


@pytest.mark.django_db
def test_special_square_after_effective():
    """Test that a special square has no effect after it's time frame has passed."""
    # Make a special square which isn't effective until the start of July.
    mommy.make(
        "SpecialSquare",
        square=24,
        type__auto_move=5,
        type__image="",
        end=utc.localize(datetime(2369, 7, 1, 0, 0)),
    )

    # Create some rolls, all which take place in July.
    for day_of_month, roll in enumerate([3, 20, 2]):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    # Assert that calculate_position doesn't take the special square into consideration.
    assert board.calculate_position(utc.localize(datetime(2369, 7, 1, 0, 0))) == 4
    assert board.calculate_position(utc.localize(datetime(2369, 7, 2, 0, 0))) == 24
    assert board.calculate_position(utc.localize(datetime(2369, 7, 3, 0, 0))) == 26


@pytest.mark.django_db
@pytest.mark.parametrize(
    "rolls, expected_position",
    [
        ([3, 20, 2, 40, 17, 5, 10, 1], 99),
        ([3, 20, 2, 40, 17, 5, 10, 2], 100),
        ([3, 20, 2, 40, 17, 5, 10, 3], 1),
        ([3, 20, 2, 40, 17, 5, 10, 6], 4),
    ],
)
def test_100(rolls, expected_position):
    """Tests for series of rolls around 100."""
    # Create a series of rolls which move the runabout to position 99.
    for day_of_month, roll in enumerate(rolls):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    assert (
        board.calculate_position(utc.localize(datetime(2369, 12, 31)))
        == expected_position
    )


@pytest.mark.django_db
def test_butthole_after_100():
    """Test that buttholes take effect on the second time around to board."""
    # Positions should be calculated as 99, 9, and 14…
    for day_of_month, roll in enumerate([98, 10, 5]):
        mommy.make(
            "Roll",
            number=roll,
            embargo=utc.localize(datetime(2369, 7, day_of_month + 1)),
        )

    # …except there's a butthole from 9 to 2, meaning the positions should be 99, 2,
    # and 7.
    mommy.make("Butthole", start_square=9, end_square=2)
    assert board.calculate_position(utc.localize(datetime(2369, 12, 31))) == 7
