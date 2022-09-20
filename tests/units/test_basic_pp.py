from moto_bpp1 import Basic1PrettyPrinter


def test_Basic1PrettyPrinter_change_character_case_outside_of_double_quotes_only():
    assert (
        Basic1PrettyPrinter().makePretty('10 cls:Print "Hello":locate 10,1')
        == '10 CLS:PRINT "Hello":LOCATE 10,1'
    )


def test_Basic1PrettyPrinter_should_add_missing_line_number():
    assert (
        Basic1PrettyPrinter().makePretty('cls:Print "Hello":locate 10,1')
        == '10 CLS:PRINT "Hello":LOCATE 10,1'
    )


def test_Basic1PrettyPrinter_should_increment_automatic_line_numbers():
    lc = Basic1PrettyPrinter()
    assert (
        lc.makePretty('cls:Print "Hello":locate 10,1')
        == '10 CLS:PRINT "Hello":LOCATE 10,1'
    )
    assert (
        lc.makePretty('cls:Print "Hello":locate 10,1')
        == '20 CLS:PRINT "Hello":LOCATE 10,1'
    )


def test_Basic1PrettyPrinter_should_start_automatic_line_numbers_from_latest_line_number():
    lc = Basic1PrettyPrinter()
    assert (
        lc.makePretty('5 cls:Print "Hello":locate 10,1')
        == '5 CLS:PRINT "Hello":LOCATE 10,1'
    )
    assert (
        lc.makePretty('cls:Print "Hello":locate 10,1')
        == '15 CLS:PRINT "Hello":LOCATE 10,1'
    )


def test_Basic1PrettyPrinter_should_not_complains_when_line_number_is_smaller_than_previous_line_number():
    lc = Basic1PrettyPrinter()
    assert (
        lc.makePretty('cls:Print "Hello":locate 10,1')
        == '10 CLS:PRINT "Hello":LOCATE 10,1'
    )
    assert (
        lc.makePretty('5 cls:Print "Hello":locate 10,1')
        == '5 CLS:PRINT "Hello":LOCATE 10,1'
    )
    assert (
        lc.makePretty('cls:Print "Hello":locate 10,1')
        == '15 CLS:PRINT "Hello":LOCATE 10,1'
    )
