target_module = "streamcontrol.main"


class BaseScheduler(object):
    pass


class GoodScheduler(BaseScheduler):
    pass


class BadScheduler(object):
    pass


class _MoreBadScheduler(BaseScheduler):
    pass


def test_get_schedulers(get_handler, mocker):
    """Should only find classes that inherit from BaseScheduler"""
    main = get_handler(target_module)
    scheduler_mock = mocker.Mock()
    scheduler_mock.BaseScheduler = BaseScheduler
    scheduler_mock.GoodScheduler = GoodScheduler
    scheduler_mock.BadScheduler = BadScheduler

    mocker.patch.object(main, "schedulers", scheduler_mock)
    schedulers = main.get_schedulers()
    assert scheduler_mock.GoodScheduler in schedulers
    assert scheduler_mock.BadScheduler not in schedulers


def test_get_schedulers_underscore(get_handler, mocker):
    """Should not include classes that start with _"""
    main = get_handler(target_module)
    scheduler_mock = mocker.Mock()
    scheduler_mock.BaseScheduler = BaseScheduler
    scheduler_mock.GoodScheduler = GoodScheduler
    scheduler_mock._MoreBadScheduler = _MoreBadScheduler
    mocker.patch.object(main, "schedulers", scheduler_mock)
    schedulers = main.get_schedulers()
    assert scheduler_mock.GoodScheduler in schedulers
    assert scheduler_mock._MoreBadScheduler not in schedulers


def test_main_raise_runtime_error(get_handler, mocker):
    main = get_handler(target_module)
    asyncio_mock = mocker.Mock()
    asyncio_mock.get_event_loop_policy().get_event_loop().run_forever = mocker.Mock(
        side_effect=KeyboardInterrupt
    )
    mocker.patch.object(main, "asyncio", asyncio_mock)
    mocker.patch.object(main.asyncio, "get_running_loop", side_effect=RuntimeError)
    mocker.patch.object(main.asyncio, "run_forever", side_effect=KeyboardInterrupt)
    scheduler_mock = mocker.Mock()
    mocker.patch.object(main, "get_schedulers", return_value=[scheduler_mock])
    mocker.patch.object(main, "log")
    main.main()
    """Should raise RuntimeError if async loop is not running"""
    asyncio_mock.get_running_loop.assert_called()
    """Should respond to KeyboardInterrupt and close"""
    asyncio_mock.get_event_loop_policy().get_event_loop().run_forever.assert_called()
    """Should register schedulers by calling them"""
    scheduler_mock.assert_called()
