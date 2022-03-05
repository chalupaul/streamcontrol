import pytest

from streamcontrol import exceptions


def test_source_name_not_found():
    e = exceptions.SourceNameNotFound
    with pytest.raises(exceptions.SourceNameNotFound):
        raise (e)
