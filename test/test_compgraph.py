"""
Test CompGraph construction.

python test_compgraph.py # using unittest
py.test test_compgraph.py
"""

import unittest
from epypes import compgraph


def dummy_func(*args, **kwargs):
    return True


class TestCompGraph(unittest.TestCase):

    def test_complains_about_missing_source_tokens(self):

        cg = compgraph.CompGraph(
            func_dict={'func': dummy_func},
            func_io={'func': (('a', 'b', 'c'), 'bool_val')}
        )

        runner = compgraph.CompGraphRunner(cg)

        with self.assertRaises(compgraph.UndefinedSourceTokensException):
            runner.run()

        with self.assertRaises(compgraph.UndefinedSourceTokensException):
            runner.run(a=1)

        with self.assertRaises(compgraph.UndefinedSourceTokensException):
            runner.run(a=1, b='hello')

        try:
            runner.run()
        except compgraph.UndefinedSourceTokensException as e:
            self.assertEqual(e.missing_source_tokens, {'a', 'b', 'c'})

        try:
            runner.run(a=1)
        except compgraph.UndefinedSourceTokensException as e:
            self.assertEqual(e.missing_source_tokens, {'b', 'c'})

        try:
            runner.run(a=1, b='hello')
        except compgraph.UndefinedSourceTokensException as e:
            self.assertEqual(e.missing_source_tokens, {'c'})


if __name__ == '__main__':
    unittest.main()
