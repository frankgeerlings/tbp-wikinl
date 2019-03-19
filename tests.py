import unittest
import doctest
import messagebuilder
import nomination

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(messagebuilder))
    tests.addTests(doctest.DocTestSuite(nomination))
    return tests
