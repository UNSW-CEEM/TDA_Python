import unittest
import validate_component_table_cell_values


class TestValidateTimeWindows(unittest.TestCase):
    def testGoodTimeWindowOneSlot(self):
        test_string = "{\'T1\' : ['22:00', '23:00']}"
        expect_answer = ''
        answer = validate_component_table_cell_values._time_intervals(test_string)
        self.assertEqual(answer, expect_answer)

    def testGoodTimeWindowTwoSlot(self):
        test_string = "{\'T1\' : ['22:00', '23:00'], \'T1\' : ['22:00', '23:00']}"
        expect_answer = ''
        answer = validate_component_table_cell_values._time_intervals(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailTimeWindowTwoSlotMissingComma(self):
        test_string = "{\'T1\' : ['22:00', '23:00'] \'T1\' : ['22:00', '23:00']}"
        expect_answer = 'Time windows not comma separated.'
        answer = validate_component_table_cell_values._time_intervals(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailTimeWindowTwoSlotMissingQuotesOnName(self):
        test_string = "{T1 : ['22:00', '23:00'], \'T1\' : ['22:00', '23:00']}"
        expect_answer = 'Time window name not quoted.'
        answer = validate_component_table_cell_values._time_intervals(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailTimeWindowTwoSlotCommaInWrongPosition(self):
        test_string = "{\'T1\' : ['22:00', '23:00'], \'T1\' : ['22:00', '23:00'],}"
        expect_answer = 'Incorrect trailing comma.'
        answer = validate_component_table_cell_values._time_intervals(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailTimeWindowTwoSlotForgotFirstColon(self):
        test_string = "{\'T1\' ['22:00', '23:00'], \'T1\' : ['22:00', '23:00']}"
        expect_answer = 'Time window names and values should be separated by a colon (:).'
        answer = validate_component_table_cell_values._time_intervals(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailTimeWindowTwoSlotSecondTimeWindowNotCommaSeparated(self):
        test_string = "{\'T1\' : ['22:00', '23:00'], \'T1\' : ['22:00'| '23:00']}"
        expect_answer = 'Time window should have two times, separated by a comma.'
        answer = validate_component_table_cell_values._time_intervals(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailTimeWindowTwoSlotSecondTimeWindowOK(self):
        test_string = "{\'T1\' : ['22:00', '23:00'], \'T1\' : ['22:00', '25:00']}"
        expect_answer = 'The hour provided is not an integer between 0 and 24.'
        answer = validate_component_table_cell_values._time_intervals(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailTimeWindowTwoSlotMissingSquareBrackets(self):
        test_string = "{\'T1\' : ['22:00', '23:00', \'T1\' : '22:00', '25:00']}"
        expect_answer = 'Time window should have two times, separated by a comma.'
        answer = validate_component_table_cell_values._time_intervals(test_string)
        self.assertEqual(answer, expect_answer)


class TestTimeWindowChecks(unittest.TestCase):
    def testFailOnBlankInput(self):
        test_string = ''
        expect_answer = 'Blank input provided.'
        answer = validate_component_table_cell_values._not_empty_string(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassOnNonBlankInput(self):
        test_string = ' '
        expect_answer = ''
        answer = validate_component_table_cell_values._not_empty_string(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnNoCurlyBraces(self):
        test_string = "\"T1\" : ['22:00', '23:00']"
        expect_answer = 'Input not enclosed in curly braces.'
        answer = validate_component_table_cell_values._closed_curly_braces(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnJustFirstCurlyBrace(self):
        test_string = "{\"T1\" : ['22:00', '23:00']"
        expect_answer = 'Input not enclosed in curly braces.'
        answer = validate_component_table_cell_values._closed_curly_braces(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnJustSecondCurlyBrace(self):
        test_string = "\"T1\" : ['22:00', '23:00']}"
        expect_answer = 'Input not enclosed in curly braces.'
        answer = validate_component_table_cell_values._closed_curly_braces(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassWithCurlyBraces(self):
        test_string = "{\"T1\" : ['22:00', '23:00']}"
        expect_answer = ''
        answer = validate_component_table_cell_values._closed_curly_braces(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailsOnNothingInsideCurlyBraces(self):
        test_string = "{}"
        expect_answer = 'Blank input provided inside curly braces.'
        answer = validate_component_table_cell_values._non_blank_inside_curly_braces(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassOnSomethingInsideCurlyBraces(self):
        test_string = "{ }"
        expect_answer = ''
        answer = validate_component_table_cell_values._non_blank_inside_curly_braces(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassElementIfColonSeparated(self):
        test_string = "hi:[there"
        expect_answer = ''
        answer = validate_component_table_cell_values._colon_separated(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailElementIfNotColonSeparated(self):
        test_string = "hi there"
        expect_answer = 'Time window names and values should be separated by a colon (:).'
        answer = validate_component_table_cell_values._colon_separated(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailElementIfNoTimeWindowNameProvided(self):
        test_string = ": there"
        expect_answer = 'Time window without name provided.'
        answer = validate_component_table_cell_values._time_window_has_name(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassElementIfTimeWindowNameProvided(self):
        test_string = "hi : there"
        expect_answer = ''
        answer = validate_component_table_cell_values._time_window_has_name(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailElementIfTimeWindowNameNotQuoted(self):
        test_string = "hi: there"
        expect_answer = 'Time window name not quoted.'
        answer = validate_component_table_cell_values._window_name_quoted(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassElementIfTimeWindowNameQuoted(self):
        test_string = "\'hi\':[there"
        expect_answer = ''
        answer = validate_component_table_cell_values._window_name_quoted(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailElementIfTimeWindowNameBlankInsideQuotes(self):
        test_string = "\'\':[there"
        expect_answer = 'Blank window name provided inside quotes.'
        answer = validate_component_table_cell_values._window_name_not_blank_inside_quotes(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassElementIfTimeWindowNameNotBlankInsideQuotes(self):
        test_string = "\'hi\':[there"
        expect_answer = ''
        answer = validate_component_table_cell_values._window_name_not_blank_inside_quotes(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfTimeWindowNotInsideSquareBrackes(self):
        test_string = "\'hi\':[there"
        expect_answer = 'Time window not inside square brackets.'
        answer = validate_component_table_cell_values._time_window_inside_square_brackets(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfTimeWindowNotInsideFirstSquareBrackes(self):
        test_string = "\'hi\':there]"
        expect_answer = 'Time window not inside square brackets.'
        answer = validate_component_table_cell_values._time_window_inside_square_brackets(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfTimeWindowNotInsideLastSquareBrackes(self):
        test_string = "\'hi\':[there"
        expect_answer = 'Time window not inside square brackets.'
        answer = validate_component_table_cell_values._time_window_inside_square_brackets(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassElementIfTimeWindowInsideSquareBrackets(self):
        test_string = "\'hi\':[there]"
        expect_answer = ''
        answer = validate_component_table_cell_values._time_window_inside_square_brackets(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfTimeWindowHasOneElement(self):
        test_string = "\'hi\':[there]"
        expect_answer = 'Time window should have two times, separated by a comma.'
        answer = validate_component_table_cell_values._time_window_has_two_elements(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfTimeWindowHasNoElements(self):
        test_string = "\'hi\':[]"
        expect_answer = 'Time window should have two times, separated by a comma.'
        answer = validate_component_table_cell_values._time_window_has_two_elements(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfTimeWindowHasTwoElements(self):
        test_string = "\'hi\':[there, you]"
        expect_answer = ''
        answer = validate_component_table_cell_values._time_window_has_two_elements(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfTimeNotQuoted(self):
        test_string = "10:00"
        expect_answer = 'Time not quoted.'
        answer = validate_component_table_cell_values._time_is_quoted(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfTimeQuoted(self):
        test_string = "\'10:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._time_is_quoted(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfHoursAndMinutesNotColonSeparated(self):
        test_string = "\'1000\'"
        expect_answer = 'Hours and minutes should be colon separated.'
        answer = validate_component_table_cell_values._hours_and_minutes_colon_separated(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfHoursAndMinutesColonSeparated(self):
        test_string = "\'10:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._hours_and_minutes_colon_separated(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfHourStringALetter(self):
        test_string = "\'a:00\'"
        expect_answer = 'The hour provided is not an integer between 0 and 24.'
        answer = validate_component_table_cell_values._hours_int_less_than_or_equal_to_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfHourStringNegative(self):
        test_string = "\'-1:00\'"
        expect_answer = 'The hour provided is not an integer between 0 and 24.'
        answer = validate_component_table_cell_values._hours_int_less_than_or_equal_to_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfHourString24(self):
        test_string = "\'24:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._hours_int_less_than_or_equal_to_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfHourString2430(self):
        test_string = "\'24:30\'"
        expect_answer = 'The max input time should be 24:00.'
        answer = validate_component_table_cell_values._hours_int_less_than_or_equal_to_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfHourString23(self):
        test_string = "\'23:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._hours_int_less_than_or_equal_to_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfHourString00(self):
        test_string = "\'00:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._hours_int_less_than_or_equal_to_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfHourString12(self):
        test_string = "\'12:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._hours_int_less_than_or_equal_to_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfMinuteStringALetter(self):
        test_string = "\'00:a\'"
        expect_answer = 'The minute provided is not 0 or 30 min.'
        answer = validate_component_table_cell_values._minutes_int_0_or_30(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfMinuteStringNegative(self):
        test_string = "\'11:-30\'"
        expect_answer = 'The minute provided is not 0 or 30 min.'
        answer = validate_component_table_cell_values._minutes_int_0_or_30(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfMinuteString60(self):
        test_string = "\'23:60\'"
        expect_answer = 'The minute provided is not 0 or 30 min.'
        answer = validate_component_table_cell_values._minutes_int_0_or_30(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfMinuteString3(self):
        test_string = "\'23:3\'"
        expect_answer = 'The minute provided is not 0 or 30 min.'
        answer = validate_component_table_cell_values._minutes_int_0_or_30(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfMinuteString30(self):
        test_string = "\'23:30\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._minutes_int_0_or_30(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfMinuteString0(self):
        test_string = "\'00:0\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._minutes_int_0_or_30(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfMinuteString00(self):
        test_string = "\'00:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._minutes_int_0_or_30(test_string)
        self.assertEqual(answer, expect_answer)


class TestValidateNumericValues(unittest.TestCase):
    def testFailOnStringWithCharacter(self):
        test_string = "a"
        expect_answer = 'Could not convert the given value to a float.'
        answer = validate_component_table_cell_values._real_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnEmptyString(self):
        test_string = ""
        expect_answer = 'Could not convert the given value to a float.'
        answer = validate_component_table_cell_values._real_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnEmptySpace(self):
        test_string = ""
        expect_answer = 'Could not convert the given value to a float.'
        answer = validate_component_table_cell_values._real_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptInt(self):
        test_string = "1"
        expect_answer = ''
        answer = validate_component_table_cell_values._real_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptDec(self):
        test_string = '0.1'
        expect_answer = ''
        answer = validate_component_table_cell_values._real_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptSignedDec(self):
        test_string = '-0.1'
        expect_answer = ''
        answer = validate_component_table_cell_values._real_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnNaN(self):
        test_string = 'NaN'
        expect_answer = 'Value should be a real number.'
        answer = validate_component_table_cell_values._real_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnInf(self):
        test_string = 'inf'
        expect_answer = 'Value should be a real number.'
        answer = validate_component_table_cell_values._real_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnNegInf(self):
        test_string = '-inf'
        expect_answer = 'Value should be a real number.'
        answer = validate_component_table_cell_values._real_value(test_string)
        self.assertEqual(answer, expect_answer)


class TestValidateBooleanValues(unittest.TestCase):
    def testFailOnLowerCase(self):
        test_string = 'false'
        expect_answer = 'Value should be True or False.'
        answer = validate_component_table_cell_values._boolean(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnZero(self):
        test_string = '0'
        expect_answer = 'Value should be True or False.'
        answer = validate_component_table_cell_values._boolean(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnOne(self):
        test_string = '1'
        expect_answer = 'Value should be True or False.'
        answer = validate_component_table_cell_values._boolean(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptTrue(self):
        test_string = 'True'
        expect_answer = ''
        answer = validate_component_table_cell_values._boolean(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptFalse(self):
        test_string = 'False'
        expect_answer = ''
        answer = validate_component_table_cell_values._boolean(test_string)
        self.assertEqual(answer, expect_answer)


class TestValidateIntegerValues(unittest.TestCase):
    def testFailOnString(self):
        test_string = 'false'
        expect_answer = 'Could not convert the given value to an integer.'
        answer = validate_component_table_cell_values._non_negative_int(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnDec(self):
        test_string = '1.0'
        expect_answer = 'Could not convert the given value to an integer.'
        answer = validate_component_table_cell_values._non_negative_int(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailNegInt(self):
        test_string = '-1'
        expect_answer = 'Value should be an integer greater than or equal to zero.'
        answer = validate_component_table_cell_values._non_negative_int(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassOnInt(self):
        test_string = '1'
        expect_answer = ''
        answer = validate_component_table_cell_values._non_negative_int(test_string)
        self.assertEqual(answer, expect_answer)


class TestValidateRealNonNegatives(unittest.TestCase):
    def testFailOnString(self):
        test_string = 'false'
        expect_answer = 'Could not convert the given value to a float.'
        answer = validate_component_table_cell_values._real_non_negative_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailNegativeFloat(self):
        test_string = '-1'
        expect_answer = 'Value should be greater than or equal to zero.'
        answer = validate_component_table_cell_values._real_non_negative_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnNan(self):
        test_string = 'Nan'
        expect_answer = 'Value should be a real number.'
        answer = validate_component_table_cell_values._real_non_negative_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnInf(self):
        test_string = 'Inf'
        expect_answer = 'Value should be a real number.'
        answer = validate_component_table_cell_values._real_non_negative_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnNegInf(self):
        test_string = '-Inf'
        expect_answer = 'Value should be a real number.'
        answer = validate_component_table_cell_values._real_non_negative_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptPosInt(self):
        test_string = '1'
        expect_answer = ''
        answer = validate_component_table_cell_values._real_non_negative_value(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptZero(self):
        test_string = '0'
        expect_answer = ''
        answer = validate_component_table_cell_values._real_non_negative_value(test_string)
        self.assertEqual(answer, expect_answer)


class TestValidateRealNonNegativesAllowInf(unittest.TestCase):
    def testFailOnString(self):
        test_string = 'false'
        expect_answer = 'Could not convert the given value to a float.'
        answer = validate_component_table_cell_values._real_non_negative_value_allow_inf(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailNegativeFloat(self):
        test_string = '-1'
        expect_answer = 'Value should be greater than or equal to zero.'
        answer = validate_component_table_cell_values._real_non_negative_value_allow_inf(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnNan(self):
        test_string = 'Nan'
        expect_answer = 'Value should not be nan.'
        answer = validate_component_table_cell_values._real_non_negative_value_allow_inf(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnInf(self):
        test_string = 'Inf'
        expect_answer = 'Inf should be defined as \'inf\' (no quotes).'
        answer = validate_component_table_cell_values._real_non_negative_value_allow_inf(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnNegInf(self):
        test_string = '-Inf'
        expect_answer = 'Value should be greater than or equal to zero.'
        answer = validate_component_table_cell_values._real_non_negative_value_allow_inf(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptPosInt(self):
        test_string = '1'
        expect_answer = ''
        answer = validate_component_table_cell_values._real_non_negative_value_allow_inf(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptZero(self):
        test_string = '0'
        expect_answer = ''
        answer = validate_component_table_cell_values._real_non_negative_value_allow_inf(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptInf(self):
        test_string = '0'
        expect_answer = ''
        answer = validate_component_table_cell_values._real_non_negative_value_allow_inf(test_string)
        self.assertEqual(answer, expect_answer)


class TestValidateListOfInts(unittest.TestCase):
    def testFailNoSquareBrackets(self):
        test_string = '1 , 2'
        expect_answer = 'Inputs should be a list of integers enclosed in square brackets.'
        answer = validate_component_table_cell_values._list_of_ints(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailNotCommaSeparated(self):
        test_string = '[1  2]'
        expect_answer = 'Integers should be comma separated.'
        answer = validate_component_table_cell_values._list_of_ints(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnString(self):
        test_string = '[1,May]'
        expect_answer = 'Each month should be an integer between 1 and 12.'
        answer = validate_component_table_cell_values._list_of_ints(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnZero(self):
        test_string = '[1,0]'
        expect_answer = 'Each month should be an integer between 1 and 12.'
        answer = validate_component_table_cell_values._list_of_ints(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOn13(self):
        test_string = '[1,13]'
        expect_answer = 'Each month should be an integer between 1 and 12.'
        answer = validate_component_table_cell_values._list_of_ints(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnEmptySlot(self):
        test_string = '[1,]'
        expect_answer = 'Each month should be an integer between 1 and 12.'
        answer = validate_component_table_cell_values._list_of_ints(test_string)
        self.assertEqual(answer, expect_answer)

    def testAcceptOneMonth(self):
        test_string = '[1]'
        expect_answer = ''
        answer = validate_component_table_cell_values._list_of_ints(test_string)
        self.assertEqual(answer, expect_answer)

    def testAccept12Months(self):
        test_string = '[1,2,3,4,5,6,7,8,9,10,11,12]'
        expect_answer = ''
        answer = validate_component_table_cell_values._list_of_ints(test_string)
        self.assertEqual(answer, expect_answer)

