#!/usr/bin/env python


def modulus(x, y):
    return (x**2 + y**2) ** 0.5


class Point(object):
    def __init__(self, x, y):
        try:
            self.x = float(x)
            self.y = float(y)
        except ValueError as err:
            raise ValueError("Invalid parameters")

    def __str__(self):
        return "Point({:+.2f}, {:+.2f})".format(self.x, self.y)

    def mod(self):
        return modulus(self.x, self.y)
