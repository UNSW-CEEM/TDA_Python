import unittest
import validate_component_table_cell_values


class TestValidateTimeWindows(unittest.TestCase):
    def testGoodTimeWindowOneSlot(self):
        test_string = "{\'T1\' : ['22:00', '23:00']}"
        expect_answer = ''
        answer = validate_component_table_cell_values.time_window(test_string)
        self.assertEqual(answer, expect_answer)

    def testGoodTimeWindowTwoSlot(self):
        test_string = "{\'T1\' : ['22:00', '23:00'], \'T1\' : ['22:00', '23:00']}"
        expect_answer = ''
        answer = validate_component_table_cell_values.time_window(test_string)
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
        expect_answer = 'Input not inclosed in curly braces.'
        answer = validate_component_table_cell_values._closed_curly_braces(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnJustFirstCurlyBrace(self):
        test_string = "{\"T1\" : ['22:00', '23:00']"
        expect_answer = 'Input not inclosed in curly braces.'
        answer = validate_component_table_cell_values._closed_curly_braces(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailOnJustSecondCurlyBrace(self):
        test_string = "\"T1\" : ['22:00', '23:00']}"
        expect_answer = 'Input not inclosed in curly braces.'
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
        expect_answer = 'Time window not quoted'
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
        expect_answer = 'The hour provided is not an integer between 0 and 23.'
        answer = validate_component_table_cell_values._hours_int_less_than_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfHourStringNegative(self):
        test_string = "\'-1:00\'"
        expect_answer = 'The hour provided is not an integer between 0 and 23.'
        answer = validate_component_table_cell_values._hours_int_less_than_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfHourString24(self):
        test_string = "\'24:00\'"
        expect_answer = 'The hour provided is not an integer between 0 and 23.'
        answer = validate_component_table_cell_values._hours_int_less_than_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfHourString23(self):
        test_string = "\'23:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._hours_int_less_than_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfHourString00(self):
        test_string = "\'00:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._hours_int_less_than_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfHourString12(self):
        test_string = "\'12:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._hours_int_less_than_24(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfMinuteStringALetter(self):
        test_string = "\'00:a\'"
        expect_answer = 'The minute provided is not an integer between 0 and 59.'
        answer = validate_component_table_cell_values._minutes_int_less_than_60(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfMinuteStringNegative(self):
        test_string = "\'11:-1\'"
        expect_answer = 'The minute provided is not an integer between 0 and 59.'
        answer = validate_component_table_cell_values._minutes_int_less_than_60(test_string)
        self.assertEqual(answer, expect_answer)

    def testFailIfMinuteString60(self):
        test_string = "\'23:60\'"
        expect_answer = 'The minute provided is not an integer between 0 and 59.'
        answer = validate_component_table_cell_values._minutes_int_less_than_60(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfMinuteString59(self):
        test_string = "\'23:59\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._minutes_int_less_than_60(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfMinuteString00(self):
        test_string = "\'00:00\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._minutes_int_less_than_60(test_string)
        self.assertEqual(answer, expect_answer)

    def testPassIfMinuteString12(self):
        test_string = "\'12:12\'"
        expect_answer = ''
        answer = validate_component_table_cell_values._minutes_int_less_than_60(test_string)
        self.assertEqual(answer, expect_answer)



