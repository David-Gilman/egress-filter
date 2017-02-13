
import os
import shutil
import unittest
from fdutil.path_tools import pop_path
from configurationutil import Configuration, cfg_params
from pydnserver import dns_forwarders


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        cfg_params.APP_NAME = u'TestPyDNServer'
        dns_forwarders.TEMPLATE = os.path.join(pop_path(__file__), u'resources', u'dns_forwarders.json')

        self.addCleanup(self.clean)

    def tearDown(self):
        pass

    @staticmethod
    def clean():
        try:
            shutil.rmtree(pop_path(pop_path(Configuration().config_path)) + os.sep)

        except OSError:
            pass

    def test_get_forwarders(self):
        expected_output = {
            u'127.0.0.1': [u'8.8.8.8', u'8.8.4.4'],
            u'127.0.0.2': [],
            u'127.0.0.3': [u'8.8.8.8']
        }

        self.assertEqual(dns_forwarders.get_all_forwarders(), expected_output,
                         u'Get forwarders failed')

    def test_get_forwarders_by_interface(self):
        expected_output = [u'8.8.8.8', u'8.8.4.4']

        self.assertEqual(dns_forwarders.get_forwarders_by_interface(u'127.0.0.1'), expected_output,
                         u'Get forwarders by interface failed')

    def test_get_forwarders_by_bad_interface(self):
        with self.assertRaises(dns_forwarders.NoForwardersConfigured):
            _ = dns_forwarders.get_forwarders_by_interface(u'DoesNotExist')

    def test_get_forwarders_by_interface_no_forwarders(self):
        with self.assertRaises(dns_forwarders.NoForwardersConfigured):
            _ = dns_forwarders.get_forwarders_by_interface(u'127.0.0.2')


if __name__ == u'__main__':
    unittest.main()
