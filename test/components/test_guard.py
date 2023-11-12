
from components.guard import Guard
import pytest
import os
import sys

# Path to the src folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


@pytest.fixture()
def standard_guard():
    guard = Guard.start(k_big=2, k=5, sleep=2).proxy()
    yield guard
    guard.stop()


def test_get_system_mcl(monkeypatch, standard_guard):
    monkeypatch.setattr(standard_guard, "get_system_mcl", lambda: 60)
    assert standard_guard.get_system_mcl().get() == 60


def test_get_inbound_workload(monkeypatch, standard_guard):
    monkeypatch.setattr(standard_guard, "get_inbound_workload", lambda: 60)
    assert standard_guard.get_inbound_workload().get() == 60


# def test_scaling_request(monkeypatch, standard_guard):
#     monkeypatch.setattr(standard_guard, "get_system_mcl", lambda: 60)
#     monkeypatch.setattr(standard_guard, "get_inbound_workload", lambda: 90)

#     assert standard_guard.should_scale().get() == True
