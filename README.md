Automated grading
============

This project is a fork of [pyTestExam](https://gitlab.in2p3.fr/ycopin/pyTestExam) by Yannick Copin.

The goal is to provide a simple way to test student's code using [py.test](https://docs.pytest.org/) machinery.


Below is the original README.md file, the usage and explanations may be outdated.


Usage
-----

Test student code using [py.test](https://docs.pytest.org/) machinery.

1.  Write test file `sample_tests.py` to check code:

    ``` python
    def test_point_init(exam):

        p = exam.Point(3, 4)
        assert hasattr(p, 'x') and almost_equal(p.x, 3)
        assert hasattr(p, 'y') and almost_equal(p.y, 4)
    ```

    All tests are available from:

    ```
    py.test --collect-only sample_tests.py
    ```

2.  Write a solution file `sample_solution.py` passing all tests:

    ``` python
    class Point(object):

        def __init__(self, x, y):

            try:
                self.x = float(x)
                self.y = float(y)
            except ValueError as err:
                raise ValueError("Invalid parameters")
    ```

3.  Test student's code `sample_exam.py`:

    ```
    py.test sample_tests.py --solution sample_solution.py --exam sample_exam.py
    ```

4.  Be nice!

Explanations
---------------

*   `conftest.py` defines 2 new options, `--exam` (student's code) and
    `--solution` (teacher's code).
*   The student code is imported as module `exam`, from which the
    functions and classes to be tested are tested:

    ``` python
    def test_modulus(exam):

        assert almost_equal(exam.modulus(3, 0), 3)
        assert almost_equal(exam.modulus(0, 4), 4)
        assert almost_equal(exam.modulus(3, 4), 5)
    ```

*   The solution should be used to test further in the code without
    being impacted by previous failing tests.  Say `f2()` depends on
    `f1()`: one wants to test `f2()` without being impacted by an
    invalid implementation of `f1()`, so tests should be written using
    `f1()` from solution.

    E.g., the following test will test `Point.mod` method using
    solution `modulus` function and `Point` class:

    ``` python
    def test_point_mod(exam, solution, sample_point):

        exam.modulus = solution.modulus
        assert almost_equal(exam.Point.mod.__func__(sample_point), 5)
    ```

To do
------

- [ ] automatic grading: set a note per test, and cumulate tests
- [ ] reporting
- [ ] sandboxing: run student's code in a sandbox

See also
----------

* initial StackOverflow
  [question](https://stackoverflow.com/questions/27694679/use-pytest-to-test-and-grade-student-code)
* [pyGrade](https://github.com/tapilab/pygrade/blob/master/example/Example.ipynb)
