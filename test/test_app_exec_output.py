"""
Tests :mod:`app` module
Command: exec
"""

import pytest

from taro_test_util import run_app
from tarotools.taro.jobs import runner
from tarotools.taro.test.observer import GenericObserver


@pytest.fixture()
def observer():
    observer = GenericObserver()
    runner.register_output_observer(observer)
    yield observer
    runner.deregister_output_observer(observer)


def test_output_observer(observer: GenericObserver):
    run_app('exec -mc echo future sound of london')
    assert observer.updates.get(timeout=2) == 'future sound of london'
