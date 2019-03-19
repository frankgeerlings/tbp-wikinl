import unittest
import doctest
import messagebuilder
import nomination
import nomparse

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(messagebuilder))
    tests.addTests(doctest.DocTestSuite(nomination))
    tests.addTests(doctest.DocTestSuite(nomparse))
    return tests
