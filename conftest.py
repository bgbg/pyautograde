#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2015-05-22 00:58 ycopin@lyonovae03.in2p3.fr>

import pytest
import imp  # Import standard library


def pytest_addoption(parser):
    """Add a custom command-line option to py.test."""

    parser.addoption("--exam", help="Code file to be tested.")
    parser.addoption("--solution", help="Solution file.")


@pytest.fixture(scope="session")
def solution(request):
    """Import code specified with command-line custom option '--solution'."""

    soluce = imp.load_source("solution", request.config.getoption("--solution"))

    return soluce


@pytest.fixture(scope="session")
def exam(request):
    """Import code specified with command-line custom option '--exam'."""

    # correction = __import__("solution")

    # Import module (standard __import__ does not support import by filename)
    codename = request.config.getoption("--exam")
    try:
        # print "Importing {!r}...".format(codename)
        code = imp.load_source("code", codename)
    except Exception as err:
        print("ERROR while importing {!r}".format(codename))
        raise

    return code
