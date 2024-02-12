#!/usr/bin/env python

# AUTHOR_ID: YOUR_ID_HERE


def modulus(x, y):
# GRADER: module 'code' has no attribute 'Point'
# GRADER: -40 points
    return (x**2 + y**2) ** 0.5


class Point(object):
    def __init__(self, x, y):
        try:
            self.x = float(x)
            self.y = float(y)
        except ValueError as err:
            raise ValueError("Invalid parameters")

    def __str__(self):
    # GRADER: assert '' == 'Point(+3.00, +4.00)'
    # GRADER:   - Point(+3.00, +4.00)
    # GRADER: -20 points
        return ""

    def mod(self):
        return modulus(
            self.x, self.y
        )  