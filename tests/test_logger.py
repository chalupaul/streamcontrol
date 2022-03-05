target_module = "streamcontrol.log"


def test_logger_is_structlog(get_handler, mocker):
    """Exposes LOGGER as a structlog logger"""
    m = mocker.Mock()
    mocker.patch("structlog.get_logger", return_value=m)
    log = get_handler(target_module)
    assert log.LOGGER == m
