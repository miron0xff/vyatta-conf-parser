# coding:utf-8
import unittest
import re
import sys
import datadiff
from datadiff.tools import assert_equal

import vyattaconfparser as vparser


class TestBackupOspfRoutesEdgemax(unittest.TestCase):        
    def test_basic_parse_works_a1(self, dos_line_endings=False):
        s = """interfaces {
             ethernet eth0 {
                 address 192.168.0.2/24
                 address 192.168.1.2/24
                 description eth0-upstream
                 duplex auto
                 speed auto
             }
             ethernet eth1 {
                 address 192.168.2.2/24
                 description eth1-other
                 duplex auto
                 speed auto
             }"""
        if dos_line_endings:
          s = s.replace('\n', '\r\n')
        correct = {
          'interfaces': {
            'ethernet': {
              'eth0': {
                'address': ['192.168.0.2/24', '192.168.1.2/24'],
                'description': 'eth0-upstream',
                 'duplex': 'auto',
                 'speed': 'auto'
              },
              'eth1': {
                'address': '192.168.2.2/24',
                'description': 'eth1-other',
                 'duplex': 'auto',
                 'speed': 'auto'
              }
            }
          }
        }
        rv = vparser.parse_conf(s)
        assert isinstance(rv, dict) 
        assert_equal(rv, correct)

    def test_basic_parse_works_a1_dos_endings(self):
        self.test_basic_parse_works_a1(dos_line_endings=True)

    def test_parsing_quoted_config_vals(self):
        s = """interfaces {
             ethernet eth0 {
                 description "eth0-upstream 302.5-19a"
                 duplex auto
                 speed auto
             }
        }"""
        correct = {
          'interfaces': {
            'ethernet': {
              'eth0': {
                'description': 'eth0-upstream 302.5-19a',
                 'duplex': 'auto',
                 'speed': 'auto'
              }
            }
          }
        }
        rv = vparser.parse_conf(s)
        assert isinstance(rv, dict) 
        assert_equal(rv, correct)

    def test_parsing_quoted_config_vals_special_chars(self):
        s = """interfaces {
             ethernet eth0 {
                 description "eth0-upstream #302.5-19a (temp path)"
                 duplex auto
                 speed auto
             }
        }"""
        correct = {
            'interfaces': {
                'ethernet': {
                    'eth0': {
                        'description': 'eth0-upstream #302.5-19a (temp path)',
                        'duplex': 'auto',
                        'speed': 'auto'
                    }
                }
            }
        }
        rv = vparser.parse_conf(s)
        assert isinstance(rv, dict) 
        assert_equal(rv, correct)

    def test_parsing_bgp_ipv6_works(self):
        s = """protocols {
            bgp 1 {
                address-family {
                    ipv6-unicast {
                        network 2001:2000:6000::/40 {
                        }
                        network 2001:2060::/32 {
                        }
                    }
                }
                neighbor 10.10.1.2 {
                    remote-as 2
                }
                network 192.168.1.0/24 {
                }
            }
        }"""
        correct = {
            'protocols': {
                'bgp': {
                    '1': {
                        'address-family': {
                            'ipv6-unicast': {
                                'network': {
                                    '2001:2000:6000::/40': {},
                                    '2001:2060::/32': {}
                                }
                            }
                        },
                        'neighbor': {
                            '10.10.1.2': {
                                'remote-as': '2'
                            }
                        },
                        'network': {
                            '192.168.1.0/24': {}
                        }
                    }
                }
            }
        }
        rv = vparser.parse_conf(s)
        assert isinstance(rv, dict)
        assert_equal(rv, correct)

    ## Future comment parsing (using '_comment' key -- parsed obj format not yet selected).
    # def test_parsing_config_comments(self):
    #     s = """interfaces {
    #          ethernet eth0 {
    #              /* temp subnet -- chars NORMAL */
    #              address 192.168.0.2/24
    #              address 192.168.1.2/24
    #              duplex auto
    #              speed auto
    #          }
    #     }"""
    #     correct = {
    #       'interfaces': {
    #         'ethernet': {
    #           'eth0': {
    #              'address': {
    #                '192.168.0.2/24': {'_comment': 'temp subnet -- chars NORMAL'},
    #                '192.168.1.2/24': {}
    #              },
    #              'duplex': 'auto',
    #              'speed': 'auto'
    #           }
    #         }
    #       }
    #     }
    #     rv = vparser.parse_conf(s)
    #     assert isinstance(rv, dict) 
    #     assert_equal(rv, correct)
    #
    # def test_parsing_config_comments_special_chars(self):
    #     s = """interfaces {
    #          ethernet eth0 {
    #              /* temp subnet -- chars Sw #23 (temp 2.3.9) */
    #              address 192.168.0.2/24
    #              address 192.168.1.2/24
    #              duplex auto
    #              speed auto
    #          }
    #     }"""
    #     correct = {
    #       'interfaces': {
    #         'ethernet': {
    #           'eth0': {
    #              'address': {
    #                '192.168.0.2/24': {'_comment': 'temp subnet -- chars Sw #23 (temp 2.3.9)'},
    #                '192.168.1.2/24': {}
    #              },
    #              'duplex': 'auto',
    #              'speed': 'auto'
    #           }
    #         }
    #       }
    #     }
    #     rv = vparser.parse_conf(s)
    #     assert isinstance(rv, dict) 
    #     assert_equal(rv, correct)

if __name__ == "__main__":
    unittest.main()
