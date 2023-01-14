import paramanager as pm


def assert_value_exception(f, exception_expected=True):
    try:
        f()
        assert not exception_expected
    except ValueError:
        assert exception_expected


def test_default_allowed_chars():
    assert_value_exception(lambda: pm.ProtoParameter("This has spaces so should fail", 0.0))

    pm.ProtoParameter("test1_test", 0.0)

    assert_value_exception(lambda: pm.ProtoParameter("test1_test", 0.0), False)


def test_set_value():
    pp = pm.ProtoParameter("para", 0.0)
    pp.set_value("Hi_this_does_not_make_sense")
    assert pp().value == 0.0

    pp.set_value("0.1")
    assert pp().value == 0.1
