from typing import ClassVar
from unittest.mock import MagicMock

import pytest

from handlers.pad_handler import PadHandler
from tests.conftest import make_pad_event


@pytest.fixture
def services():
    return {
        "command_service": MagicMock(),
        "sequence_service": MagicMock(),
        "notification_service": MagicMock(),
    }


def make_handler(pad_map: dict, services: dict) -> PadHandler:
    return PadHandler(
        pad_map=pad_map,
        command_service=services["command_service"],
        sequence_service=services["sequence_service"],
        notification_service=services["notification_service"],
    )


class TestUnmappedPad:
    def test_warns_and_does_not_dispatch(self, services):
        handler = make_handler({}, services)
        handler.handle(make_pad_event(pad_id=99))

        notif = services["notification_service"]
        notif.notify_warning.assert_called_once_with("Pad sin mapear", "pad_id=99")
        services["command_service"].execute.assert_not_called()
        services["sequence_service"].execute.assert_not_called()
        notif.notify_done.assert_not_called()


class TestSimpleType:
    def _pad_map(self, **extra):
        return {
            1: {"name": "test_pad", "type": "simple", "command": "echo hello", **extra}
        }

    def test_happy_path(self, services):
        services["command_service"].execute.return_value = True
        make_handler(self._pad_map(), services).handle(make_pad_event())

        services["command_service"].execute.assert_called_once_with(
            "echo hello", "test_pad"
        )
        services["notification_service"].notify_done.assert_called_once_with(
            "test_pad", skip_notify=False, skip_sound=False
        )

    def test_execute_fails_skips_notify_done(self, services):
        services["command_service"].execute.return_value = False
        make_handler(self._pad_map(), services).handle(make_pad_event())

        services["notification_service"].notify_done.assert_not_called()

    def test_skip_notify_flag_passed_through(self, services):
        services["command_service"].execute.return_value = True
        make_handler(self._pad_map(skip_notify=True), services).handle(make_pad_event())

        services["notification_service"].notify_done.assert_called_once_with(
            "test_pad", skip_notify=True, skip_sound=False
        )

    def test_skip_sound_flag_passed_through(self, services):
        services["command_service"].execute.return_value = True
        make_handler(self._pad_map(skip_sound=True), services).handle(make_pad_event())

        services["notification_service"].notify_done.assert_called_once_with(
            "test_pad", skip_notify=False, skip_sound=True
        )


class TestSequenceType:
    _steps: ClassVar = [{"action": "open", "app": "firefox"}]
    _pad_map: ClassVar = {1: {"name": "seq_pad", "type": "sequence", "steps": _steps}}

    def test_notify_sequence_called_before_dispatch(self, services):
        call_order = []
        services["notification_service"].notify_sequence.side_effect = lambda: (
            call_order.append("notify_sequence")
        )
        services["sequence_service"].execute.side_effect = lambda steps, name: (
            call_order.append("execute") or True
        )

        make_handler(self._pad_map, services).handle(make_pad_event())

        assert call_order == ["notify_sequence", "execute"]
        services["notification_service"].notify_done.assert_called_once()

    def test_execute_fails_no_notify_done(self, services):
        services["sequence_service"].execute.return_value = False
        make_handler(self._pad_map, services).handle(make_pad_event())

        services["notification_service"].notify_sequence.assert_called_once()
        services["notification_service"].notify_done.assert_not_called()


class TestUnknownType:
    def test_warns_and_does_not_dispatch(self, services):
        pad_map = {1: {"name": "bad_pad", "type": "foobar"}}
        make_handler(pad_map, services).handle(make_pad_event())

        services["notification_service"].notify_warning.assert_called_once()
        services["notification_service"].notify_done.assert_not_called()
        services["command_service"].execute.assert_not_called()
        services["sequence_service"].execute.assert_not_called()
