#!/usr/bin/env python3 

import sys
import duim
import unittest
import subprocess

class TestArgs(unittest.TestCase):
    
    def test_argparse_help(self):
        "duim.py -h returns the required options"
        p = subprocess.Popen(['/usr/bin/python3', 'duim.py', '-h'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, err = p.communicate()
        # Fail test if process returns a non-zero exit status
        return_code = p.wait()
        error_output = 'Output of `duim.py -h` doesn\'t match what\'s expected. Make sure you\'ve added an option!)'
        expected_out = ["[-h]", "[-H]", "[-l LENGTH]", "target"]
        for string in expected_out:
            self.assertIn(string, stdout.decode('utf-8'), msg=error_output)

class TestPercent(unittest.TestCase):

    def test_percent(self):
        "percent_to_graph returns correct '##    ' format"
        percent_list = [33, 56, 70, 63, 89]
        max_list = [10, 15, 20, 30, 80]
        for i in range(0, (len(percent_list)-1)):
            given = duim.percent_to_graph(percent_list[i], max_list[i])
            inv_pcnt = 100 - percent_list[i]  # to get spaces rather than symbols
            num_spcs = round((max_list[i] * inv_pcnt) / 100) 
            expected = ' ' * num_spcs
            error_msg = "The output of percent_to_graph() with the argument " + str(percent_list[i]) + " is returning the wrong value"
            self.assertIn(expected, given, error_msg)

class TestDuSub(unittest.TestCase):

    def test_du_sub(self):
        "du_sub returns a list"
        given = duim.call_du_sub('/sys')
        error_msg = "call_du_sub must return a list!"
        self.assertIsInstance(given, list, error_msg)

class TestDirDict(unittest.TestCase):

    def test_dir_dict_func(self):
        "given mock du input, create_dir_dict returns properly formatted dict"
        test_dat = ['164028\t/usr/local/lib/heroku', '11072\t/usr/local/lib/python2.7', '92608\t/usr/local/lib/node_modules', '8\t/usr/local/lib/python3.8', '267720\t/usr/local/lib']
        expected = {'/usr/local/lib/heroku': 164028, '/usr/local/lib/python2.7': 11072, '/usr/local/lib/node_modules': 92608, '/usr/local/lib/python3.8': 8, '/usr/local/lib': 267720}
        given = duim.create_dir_dict(test_dat)
        error_msg = "The dictionary returned by create_dir_dict does not match what's expected."
        self.assertDictEqual(given, expected, error_msg)

if __name__ == "__main__":
    unittest.main()
