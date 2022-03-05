target_module = "streamcontrol.location"


def test_format_time_called_format(get_handler, mocker):
    """Should specify the proper output format"""
    loc = get_handler(target_module)
    m = mocker.Mock()
    loc.format_time(m)
    assert m.strftime.mock_calls[0].args[0] == "%I:%M %p"


def test_format_time_should_return_time(get_handler, mocker):
    """Should return the time specified"""
    loc = get_handler(target_module)
    m = mocker.Mock()
    m.strftime.return_value = "foo"
    t = loc.format_time(m)
    assert t == "foo"


def test_get_suntime_calls_sun(get_handler, mocker):
    """Should call sun() with proper arguments"""
    loc = get_handler(target_module)
    sun_mock = mocker.Mock(return_value={"foo": "bar"})
    mocker.patch.object(loc, "sun", sun_mock)
    dt = "foo"
    location = mocker.Mock()
    loc.get_suntime(dt, location)
    assert sun_mock.call_args.args[0] == location.observer
    assert sun_mock.mock_calls[0].kwargs["date"] == "foo"
    assert sun_mock.mock_calls[0].kwargs["tzinfo"] == location.timezone


def test_get_suntime_returns_sundata(get_handler, mocker):
    """Should return dict with injected tzinfo"""
    loc = get_handler(target_module)
    mocker.patch.object(loc, "sun", return_value={"foo": "bar"})
    tz = mocker.Mock()
    sun_time = loc.get_suntime(mocker.Mock(), tz)
    assert sun_time["foo"] == "bar"
    assert "tzinfo" in sun_time.keys()
    assert sun_time["tzinfo"] == tz.tzinfo
