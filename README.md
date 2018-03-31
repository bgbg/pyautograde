pyTestExam
============

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
