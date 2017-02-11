
import unittest
import pydnserver
from pydnserver import _metadata

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Instantiation
    def test_version(self):
        self.assertEqual(pydnserver.__version__, _metadata.__version__, u'Version is incorrect')


if __name__ == u'__main__':
    unittest.main()
