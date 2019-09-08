import unittest
import check_time_of_use_coverage
import datetime


class TestCompilingOverlaps(unittest.TestCase):
    def testSimpleOverlappingCase(self):
        test_tariff = {'first_comp': {'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                      'TimeIntervals': {'T1': ['00:00', '13:00'],
                                                        'T2': ['13:00', '00:00']
                                                        },
                                      'Weekday': True,
                                      'Weekend': True
                                      },
                       'second_comp': {'Month': [1, 2],
                                       'TimeIntervals': {'T1': ['11:00', '12:00']},
                                       'Weekday': True,
                                       'Weekend': True
                                       }
                       }
        expect_answer = \
        '''Overlaps on Month: 1, Week time: Weekday, Half hour ending: 11:30 are, first_comp T1, second_comp T1
Overlaps on Month: 1, Week time: Weekday, Half hour ending: 12:00 are, first_comp T1, second_comp T1
Overlaps on Month: 1, Week time: Weekend, Half hour ending: 11:30 are, first_comp T1, second_comp T1
Overlaps on Month: 1, Week time: Weekend, Half hour ending: 12:00 are, first_comp T1, second_comp T1
Overlaps on Month: 2, Week time: Weekday, Half hour ending: 11:30 are, first_comp T1, second_comp T1
Overlaps on Month: 2, Week time: Weekday, Half hour ending: 12:00 are, first_comp T1, second_comp T1
Overlaps on Month: 2, Week time: Weekend, Half hour ending: 11:30 are, first_comp T1, second_comp T1
Overlaps on Month: 2, Week time: Weekend, Half hour ending: 12:00 are, first_comp T1, second_comp T1
No gaps in the component time intervals were found.'''
        answer = check_time_of_use_coverage.compile_set_of_overlapping_components_on_yearly_basis(test_tariff)
        self.assertEqual(answer, expect_answer)


class TestCheckForOverlap(unittest.TestCase):
    def testSimpleOverlappingCase(self):
        test_tariff = {'first_comp': {'Month': [1, 2],
                                      'TimeIntervals': {'T1': ['11:00', '12:00'],
                                                        'T2': ['12:00', '13:00']
                                                        },
                                      'Weekday': False,
                                      'Weekend': True
                                      },
                       'second_comp': {'Month': [1, 2],
                                       'TimeIntervals': {'T1': ['11:00', '12:00'],
                                                         'T2': ['12:00', '13:00']
                                                         },
                                       'Weekday': False,
                                       'Weekend': True
                                       }
                       }
        expect_answer = ['first_comp T1', 'second_comp T1']
        answer = check_time_of_use_coverage._overlapping_components(test_tariff, month=1, hour=11,
                                                                    minute=30, week_time='Weekend')
        self.assertListEqual(answer, expect_answer)

    def testSimpleOverlappingWithinComponent(self):
        test_tariff = {'first_comp': {'Month': [1, 2],
                                      'TimeIntervals': {'T1': ['11:00', '12:00'],
                                                        'T2': ['11:00', '13:00']
                                                        },
                                      'Weekday': False,
                                      'Weekend': True
                                      },
                       'second_comp': {'Month': [1, 2],
                                       'TimeIntervals': {'T1': ['11:00', '12:00'],
                                                         'T2': ['12:00', '13:00']
                                                         },
                                       'Weekday': False,
                                       'Weekend': True
                                       }
                       }
        expect_answer = ['first_comp T1', 'first_comp T2', 'second_comp T1']
        answer = check_time_of_use_coverage._overlapping_components(test_tariff, month=1, hour=11,
                                                                   minute=30, week_time='Weekend')
        self.assertListEqual(answer, expect_answer)


class TestCheckIfTestTimeInInterval(unittest.TestCase):
    def testFailAtStartTime(self):
        test_interval = ['12:00', '13:00']
        expected_answer = False
        answer = check_time_of_use_coverage._is_right_time(interval=test_interval, hour=12, minute=00)
        self.assertEqual(answer, expected_answer)

    def testAcceptAtEndTime(self):
        test_interval = ['12:00', '13:00']
        expected_answer = True
        answer = check_time_of_use_coverage._is_right_time(interval=test_interval, hour=13, minute=00)
        self.assertEqual(answer, expected_answer)

    def testGoodTime(self):
        test_interval = ['12:00', '13:00']
        expected_answer = True
        answer = check_time_of_use_coverage._is_right_time(interval=test_interval, hour=12, minute=30)
        self.assertEqual(answer, expected_answer)

    def testReversedFailAtStartTime(self):
        test_interval = ['13:00', '12:00']
        expected_answer = True
        answer = check_time_of_use_coverage._is_right_time(interval=test_interval, hour=12, minute=00)
        self.assertEqual(answer, expected_answer)

    def testAcceptReversedAtEndTime(self):
        test_interval = ['13:00', '12:00']
        expected_answer = False
        answer = check_time_of_use_coverage._is_right_time(interval=test_interval, hour=13, minute=00)
        self.assertEqual(answer, expected_answer)

    def testReversedGoodTime(self):
        test_interval = ['13:00', '12:00']
        expected_answer = True
        answer = check_time_of_use_coverage._is_right_time(interval=test_interval, hour=13, minute=30)
        self.assertEqual(answer, expected_answer)

    def testFailReversedBadTime(self):
        test_interval = ['13:00', '12:00']
        expected_answer = False
        answer = check_time_of_use_coverage._is_right_time(interval=test_interval, hour=12, minute=30)
        self.assertEqual(answer, expected_answer)


class TestInterpretUserTimeString(unittest.TestCase):
    def testGoodTimeString(self):
        test_string = '12:00'
        expected_answer = datetime.time(hour=12, minute=0)
        answer = check_time_of_use_coverage._interpret_user_time_string(test_string)
        self.assertEqual(answer, expected_answer)

    def testHoursLeadingZeros(self):
        test_string = '02:0'
        expected_answer = datetime.time(hour=2, minute=0)
        answer = check_time_of_use_coverage._interpret_user_time_string(test_string)
        self.assertEqual(answer, expected_answer)

    def testHoursNoLeadingZeros(self):
        test_string = '2:0'
        expected_answer = datetime.time(hour=2, minute=0)
        answer = check_time_of_use_coverage._interpret_user_time_string(test_string)
        self.assertEqual(answer, expected_answer)

    def testMinutesWithLeadingZeros(self):
        test_string = '2:01'
        expected_answer = datetime.time(hour=2, minute=1)
        answer = check_time_of_use_coverage._interpret_user_time_string(test_string)
        self.assertEqual(answer, expected_answer)

    def testMinutesWithoutLeadingZeros(self):
        test_string = '2:1'
        expected_answer = datetime.time(hour=2, minute=1)
        answer = check_time_of_use_coverage._interpret_user_time_string(test_string)
        self.assertEqual(answer, expected_answer)

