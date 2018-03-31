"""
Usage:

  py.test sample_tests.py --solution sample_solution.py --exam sample_exam.py
"""

import pytest

def almost_equal(x, y, digits=6):

    return round(x - y, digits) == 0

def test_modulus(exam):

    assert almost_equal(exam.modulus(3, 0), 3)
    assert almost_equal(exam.modulus(0, 4), 4)
    assert almost_equal(exam.modulus(3, 4), 5)

@pytest.fixture
def sample_point(solution):

    return solution.Point(3, 4)
    
def test_point_init(exam):

    p = exam.Point(3, 4)
    assert hasattr(p, 'x') and almost_equal(p.x, 3)
    assert hasattr(p, 'y') and almost_equal(p.y, 4)

def test_point_init_raise(exam):

    with pytest.raises(ValueError):
        exam.Point("cat", "dog")

def test_point_str(exam, sample_point):

    assert hasattr(exam.Point, '__str__')
    assert exam.Point.__str__.__func__(sample_point) == "Point(+3.00, +4.00)"
    
def test_point_mod(exam, solution, sample_point):

    exam.modulus = solution.modulus
    assert almost_equal(exam.Point.mod.__func__(sample_point), 5)

