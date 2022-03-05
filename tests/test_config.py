target_module = "streamcontrol.config"

config_sample = {
    "obs_host": "foo",
    "obs_port": 1337,
    "obs_password": "bar",
}

config_baseline = {
    "obs_host": "localhost",
    "obs_port": 4444,
    "obs_password": "secret",
    "text_path": "/tmp",
}


def test_Config_defaults(get_handler, mocker):
    """returns proper default values without config"""
    config = get_handler(target_module)
    mocker.patch.object(config, "dotenv_values", return_value={})
    c = config.Config()
    assert c.obs_host == config_baseline["obs_host"]
    assert c.obs_port == config_baseline["obs_port"]
    assert c.obs_password == config_baseline["obs_password"]
    assert c.text_path == config_baseline["text_path"]


def test_Config_dotenv_overwrite(get_handler, mocker):
    """dotenv values should overwrite baseline"""
    config = get_handler(target_module)
    mocker.patch.object(config, "dotenv_values", return_value=config_sample)
    c = config.Config()
    assert c.obs_host == "foo"
    assert c.obs_port == 1337
    assert c.obs_password == "bar"
    assert c.text_path == "/tmp"
