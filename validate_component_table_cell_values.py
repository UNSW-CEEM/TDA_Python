

def time_window(given_string):
    given_string = given_string.replace(' ', '')
    for check in top_level_time_window_checks:
        check_answer = check(given_string)
        if check_answer != '':
            return check_answer
    check_answer = _elements_comma_separated(given_string)
    if check_answer != '':
        return check_answer
    given_string = given_string[1:-1].replace('],', ']],')
    for element in given_string.split('],'):
        for check in element_level_checks:
            check_answer = check(element)
            if check_answer != '':
                return check_answer
        element = element.replace(':[', ':[[')
        for time_string in element.split(':[')[1][1:-1].split(','):
            for time_check in time_string_checks:
                check_answer = time_check(time_string)
                if check_answer != '':
                    return check_answer
    return ''


def _elements_comma_separated(given_string):
    if ']' not in given_string:
        return 'Time window not enclosed in brackets.'
    if '[' not in given_string:
        return 'Time window not enclosed in brackets.'
    if given_string.count('[') != given_string.count(']'):
        return 'Time window not enclosed in brackets.'
    if '],}' in given_string:
        return 'Incorrect trailing comma.'
    if given_string.count(']') - 1 != given_string.count('],'):
        return 'Time windows not comma separated.'
    return ''


def _not_empty_string(test_string):
    if test_string != '':
        return ''
    else:
        return 'Blank input provided.'


def _closed_curly_braces(test_string):
    if test_string[0] == '{' and test_string[-1] == '}':
        return ''
    else:
        return 'Input not enclosed in curly braces.'


def _non_blank_inside_curly_braces(test_string):
    string_without_curly_braces = test_string[1:-1]
    if string_without_curly_braces != '':
        return ''
    else:
        return 'Blank input provided inside curly braces.'


top_level_time_window_checks = [_not_empty_string, _closed_curly_braces,
                                _non_blank_inside_curly_braces]


def _colon_separated(test_string):
    if ':[' in test_string:
        return ''
    else:
        return 'Time window names and values should be separated by a colon (:).'


def _time_window_inside_square_brackets(element_string):
    if '[' not in element_string:
        return 'Time window not inside square brackets.'
    element_string = element_string.replace(':[', ':[[')
    time_window_string = element_string.split(':[')[1]
    if time_window_string[0] == '[' and time_window_string[-1] == ']':
        return ''
    else:
        return 'Time window not inside square brackets.'


def _time_window_has_name(element_string):
    element_string = element_string.replace(':[', ':[[')
    element_string = element_string.split(':[')[0]
    if element_string.split(':')[0] != '':
        return ''
    else:
        return 'Time window without name provided.'


def _window_name_quoted(element_string):
    element_string = element_string.replace(':[', ':[[')
    name_with_quotes = element_string.split(':[')[0]
    if name_with_quotes[0] == '\'' and name_with_quotes[-1] == '\'':
        return ''
    else:
        return 'Time window name not quoted.'


def _window_name_not_blank_inside_quotes(element_string):
    element_string = element_string.replace(':[', ':[[')
    name_without_quotes = element_string.split(':[')[0][1:-1]
    if name_without_quotes != '':
        return ''
    else:
        return 'Blank window name provided inside quotes.'


def _time_window_has_two_elements(element_string):
    element_string = element_string.replace(':[', ':[[')
    time_window_string_no_brackets = element_string.split(':[')[1][1:-1]
    if len(time_window_string_no_brackets.split(',')) == 2:
        return ''
    else:
        return 'Time window should have two times, separated by a comma.'


element_level_checks = [_colon_separated, _time_window_inside_square_brackets,
                        _time_window_has_name, _window_name_quoted,
                        _window_name_not_blank_inside_quotes,
                        _time_window_has_two_elements]


def _time_is_quoted(time_string):
    time_string = time_string.strip()
    if time_string[0] == '\'' and time_string[-1] == '\'':
        return ''
    else:
        return 'Time not quoted.'


def _hours_and_minutes_colon_separated(time_string):
    time_string = time_string.strip()[1:-1]
    if ':' in time_string:
        return ''
    else:
        return 'Hours and minutes should be colon separated.'


def _hours_int_less_than_24(time_string):
    hour_string = time_string.strip()[1:-1].split(':')[0]
    if hour_string.isdigit() and 0 <= int(hour_string) <= 23:
        return ''
    else:
        return 'The hour provided is not an integer between 0 and 23.'


def _minutes_int_less_than_60(time_string):
    hour_string = time_string.strip()[1:-1].split(':')[1]
    if hour_string.isdigit() and 0 <= int(hour_string) <= 59:
        return ''
    else:
        return 'The minute provided is not an integer between 0 and 59.'


time_string_checks = [_time_is_quoted, _hours_and_minutes_colon_separated,
                      _hours_int_less_than_24, _minutes_int_less_than_60]