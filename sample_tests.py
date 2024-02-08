"""
Usage:

  py.test sample_tests.py --solution sample_solution.py --exam sample_exam.py
"""

import pytest


def almost_equal(x, y, digits=6):
    return round(x - y, digits) == 0


def test_modulus(exam, score_fixture):
    try:
        assert almost_equal(exam.modulus(3, 0), 3)
        assert almost_equal(exam.modulus(0, 4), 4)
        assert almost_equal(exam.modulus(3, 4), 5)
    except Exception as err:
        score_fixture["total"] -= 10
        raise err


@pytest.fixture
def sample_point(solution):
    return solution.Point(3, 4)


def test_point_init(exam, score_fixture):
    points = 20
    try:
        p = exam.Point(3, 4)
        assert hasattr(p, "x") and almost_equal(p.x, 3)
        assert hasattr(p, "y") and almost_equal(p.y, 4)
    except Exception as err:
        score_fixture["total"] -= points
        raise err


def test_point_init_raise(exam, score_fixture):
    points = 20
    try:
        with pytest.raises(ValueError):
            exam.Point("cat", "dog")
    except Exception as err:
        score_fixture["total"] -= points
        raise err


def test_point_str(exam, sample_point, score_fixture):
    points = 20
    try:
        assert hasattr(exam.Point, "__str__")
        func = getattr(exam.Point, "__str__")
        assert func(sample_point) == "Point(+3.00, +4.00)"
    except Exception as err:
        score_fixture["total"] -= points
        raise err


def test_point_mod(exam, solution, sample_point, score_fixture):
    points = 40
    try:
        exam.modulus = solution.modulus
        func = getattr(exam.Point, "mod")
        assert almost_equal(func(sample_point), 5)
    except Exception as err:
        score_fixture["total"] -= points
        raise err
