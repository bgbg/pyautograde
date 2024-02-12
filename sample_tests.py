"""
Usage:

  py.test sample_tests.py --solution sample_solution.py --exam sample_exam.py
"""

import pytest

from assignment_updater import update_assignment


def almost_equal(x, y, digits=6):
    return round(x - y, digits) == 0


@pytest.fixture
def sample_point(solution):
    return solution.Point(3, 4)


def test_modulus(solution, score_fixture):
    points = 20
    function = solution.modulus
    try:
        assert almost_equal(solution.modulus(3, 0), 3)
        assert almost_equal(solution.modulus(0, 4), 4)
        assert almost_equal(solution.modulus(3, 4), 5)
    except Exception as err:
        update_assignment(solution, function, err, score_fixture, points)


def test_point_init(solution, score_fixture):
    points = 20
    function = solution.Point.__init__
    try:
        p = solution.Point(3, 4)
        assert hasattr(p, "x") and almost_equal(p.x, 3)
        assert hasattr(p, "y") and almost_equal(p.y, 4)
    except Exception as err:
        update_assignment(solution, function, err, score_fixture, points)


def test_point_init_raise(solution, score_fixture):
    points = 20
    function = solution.Point.__init__
    try:
        with pytest.raises(ValueError):
            solution.Point("cat", "dog")
    except Exception as err:
        update_assignment(solution, function, err, score_fixture, points)


def test_point_str(solution, sample_point, score_fixture):
    points = 20
    function = solution.Point.__str__
    try:
        assert hasattr(solution.Point, "__str__")
        func = getattr(solution.Point, "__str__")
        assert func(sample_point) == "Point(+3.00, +4.00)"
    except Exception as err:
        update_assignment(solution, function, err, score_fixture, points)


def test_point_mod(exam, solution, sample_point, score_fixture):
    points = 40
    function = solution.modulus
    try:
        exam.modulus = solution.modulus
        func = getattr(exam.Point, "mod")
        assert almost_equal(func(sample_point), 5)
    except Exception as err:
        update_assignment(solution, function, err, score_fixture, points)
