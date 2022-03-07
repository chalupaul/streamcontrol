target_module = "streamcontrol.obsmanager"


def test_obs_websocket_manager_new(get_handler):
    """Should create an inner instance when called"""
    ows = get_handler(target_module)
    myt = ows.OBSWebSocketManager.__new__(ows.OBSWebSocketManager)
    assert isinstance(myt.instance, ows.OBSWebSocketManager)


def test_obs_websocket_manager_enter(get_handler):
    """Must return self"""
    ows = get_handler(target_module)
    enter_out = ows.OBSWebSocketManager.__enter__(ows)
    assert enter_out == ows


def test_obs_websocket_manager_exit(get_handler, mocker):
    """Must disconnect websocket"""
    ows = get_handler(target_module)
    exit_mock = mocker.Mock()
    ows.OBSWebSocketManager.__exit__(exit_mock, 1, 2, 3)
    assert exit_mock.disconnect.called


def test_obs_websocket_manager_init(get_handler, mocker):
    """Should connect websocket if not connected"""
    ows = get_handler(target_module)
    init_mock = mocker.Mock()
    init_mock.isConnected.return_value = False
    ows.OBSWebSocketManager.__init__(init_mock)
    assert init_mock.connect.called
    init_mock.reset_mock()
    init_mock.isConnected.return_value = True
    ows.OBSWebSocketManager.__init__(init_mock)
    assert init_mock.connect.called is False
