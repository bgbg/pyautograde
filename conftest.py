#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2015-05-22 00:58 ycopin@lyonovae03.in2p3.fr>
import warnings

import numpy as np
import pytest
from importlib.machinery import SourceFileLoader


# Initialize a global score
score = {"total": 100}  # Use a dict to allow modifications


@pytest.fixture(scope="session")
def score_fixture():
    # This fixture allows tests to access and modify the global score
    global score
    return score


def load_source(what, path):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        solution = SourceFileLoader(what, path).load_module()

    return solution


def pytest_addoption(parser):
    """Add a custom command-line option to py.test."""

    parser.addoption("--exam", help="Code file to be tested.")
    parser.addoption("--solution", help="Solution file.")


@pytest.fixture(scope="session")
def solution(request):
    """Import code specified with command-line custom option '--solution'."""
    soluce = load_source(what="solution", path=request.config.getoption("--solution"))
    return soluce


@pytest.fixture(scope="session")
def exam(request):
    """Import code specified with command-line custom option '--exam'."""

    # correction = __import__("solution")

    # Import module (standard __import__ does not support import by filename)
    codename = request.config.getoption("--exam")
    code = load_source(what="code", path=codename)
    return code


def pytest_sessionfinish(session, exitstatus):
    remaining = np.round(score["total"], 1)
    print(f"\nRemaining Score: {remaining}")
