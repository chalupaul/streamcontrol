from unittest.mock import mock_open

target_module = "streamcontrol.templates"


def test_text_template_init(get_handler, mocker):
    tpl = get_handler(target_module)
    tpl_mock = mocker.Mock()
    env_mock = mocker.Mock()
    env_mock.get_template.return_value = "foo"
    mocker.patch.object(tpl, "Environment", return_value=env_mock)
    mocker.patch.object(tpl, "FileSystemLoader")
    tpl.TextTemplate.__init__(tpl_mock, "foobar")
    """Should append .jinja to filenames"""
    assert env_mock.get_template.call_args.args[0] == "foobar.jinja"
    """Should add self.template"""
    assert tpl_mock.template == "foo"


def test_text_template_render(get_handler, mocker):
    """Should pass all kwargs to template"""
    tpl = get_handler(target_module)
    tpl_mock = mocker.Mock()
    tpl.TextTemplate.render(tpl_mock, foo="bar", bin="baz")
    kwargs = tpl_mock.template.render.mock_calls[0].kwargs
    assert kwargs["foo"] == "bar"
    assert kwargs["bin"] == "baz"


def test_text_template_render_to_file(get_handler, mocker):
    tpl = get_handler(target_module)
    tpl_mock = mocker.Mock()
    open_mock = mock_open()
    mocker.patch.object(tpl, "open", open_mock)
    mocker.patch.object(tpl.config, "text_path", "foopath")
    tpl.TextTemplate.render_to_file(tpl_mock, "foofile", foo="bar", bin="baz")
    # print(dir(open_mock))
    file_loc, mode = open_mock.call_args.args
    kwargs = tpl_mock.method_calls[0].kwargs
    """Should pass in same args to template"""
    assert kwargs["foo"] == "bar"
    assert kwargs["bin"] == "baz"
    """Should append the file to the path for outputs"""
    assert file_loc == "foopath\\foofile"
    """Should actually be able to write"""
    assert mode == "w+"
