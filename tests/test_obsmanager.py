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
    init_mock.is_connected.return_value = False
    ows.OBSWebSocketManager.__init__(init_mock)
    assert init_mock.connect.called
    init_mock.reset_mock()
    init_mock.is_connected.return_value = True
    ows.OBSWebSocketManager.__init__(init_mock)
    assert init_mock.connect.called is False


def test_obs_websocket_manager_is_connected(get_handler, mocker):
    ows = get_handler(target_module)
    connect_mock = mocker.Mock()
    """Should return true if connected"""
    assert ows.OBSWebSocketManager.is_connected(connect_mock)
    """Should return false if None"""
    connect_mock.ws = None
    assert not ows.OBSWebSocketManager.is_connected(connect_mock)
    """Should return false if ws not found"""
    mocker.patch.object(ows, "hasattr", return_value=False)
    assert not ows.OBSWebSocketManager.is_connected(connect_mock)


def test_obs_websocket_manager_connect(get_handler, mocker):
    ows = get_handler(target_module)
    ws_mock = mocker.Mock()
    mocker.patch.object(ows, "obsws", return_value=ws_mock)
    """Should not connect if already connected"""
    ws_mock.is_connected.return_value = True
    ows.OBSWebSocketManager.connect(ws_mock)
    ws_mock.ws.connect.assert_not_called()
    """Should connect if not connected"""
    ws_mock.is_connected.return_value = False
    ows.OBSWebSocketManager.connect(ws_mock)
    ws_mock.ws.connect.assert_called()


def test_obs_websocket_manager_disconnect(get_handler, mocker):
    ows = get_handler(target_module)
    disconnect_mock = mocker.Mock()
    """Should not not disconnect if not connected"""
    disconnect_mock.is_connected.return_value = False
    ows.OBSWebSocketManager.disconnect(disconnect_mock)
    disconnect_mock.ws.disconnect.assert_not_called()
    """Should disconnect if connected"""
    disconnect_mock.is_connected.return_value = True
    ows.OBSWebSocketManager.disconnect(disconnect_mock)
    disconnect_mock.ws.disconnect.assert_called()
