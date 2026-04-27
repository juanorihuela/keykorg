import shlex
from unittest.mock import MagicMock, call, patch

import pytest

from services.sequence_service import SequenceService


@pytest.fixture
def notifier():
    return MagicMock()


@pytest.fixture
def svc(notifier):
    return SequenceService(notifier)


class TestExecute:
    def test_empty_steps_returns_true(self, svc):
        assert svc.execute([], "test") is True

    def test_steps_executed_in_order(self, svc):
        steps = [
            {"action": "open", "app": "app1"},
            {"action": "open", "app": "app2"},
            {"action": "open", "app": "app3"},
        ]
        with patch("services.sequence_service.subprocess.Popen") as mock_popen:
            assert svc.execute(steps, "test") is True
            assert mock_popen.call_count == 3
            assert mock_popen.call_args_list == [
                call(["app1"]),
                call(["app2"]),
                call(["app3"]),
            ]

    def test_error_in_step_n_returns_false_and_alerts(self, svc, notifier):
        call_count = {"n": 0}

        def popen_side_effect(args):
            call_count["n"] += 1
            if call_count["n"] == 3:
                raise OSError("not found")

        steps = [
            {"action": "open", "app": "app1"},
            {"action": "open", "app": "app2"},
            {"action": "open", "app": "app3"},
        ]
        with patch(
            "services.sequence_service.subprocess.Popen", side_effect=popen_side_effect
        ):
            result = svc.execute(steps, "mypad")

        assert result is False
        assert call_count["n"] == 3
        notifier.notify_alert.assert_called_once_with("mypad", "Error en secuencia")


class TestRunStep:
    def test_open_calls_popen_with_parsed_args(self, svc):
        with patch("services.sequence_service.subprocess.Popen") as mock_popen:
            svc._run_step({"action": "open", "app": "firefox --new-window"})
        mock_popen.assert_called_once_with(["firefox", "--new-window"])

    def test_delay_calls_sleep_with_float(self, svc):
        with patch("services.sequence_service.time.sleep") as mock_sleep:
            svc._run_step({"action": "delay", "seconds": 2.5})
        mock_sleep.assert_called_once_with(2.5)

    def test_shell_without_wait_calls_popen(self, svc):
        with patch("services.sequence_service.subprocess.Popen") as mock_popen:
            svc._run_step({"action": "shell", "command": "ls -la", "wait": False})
        mock_popen.assert_called_once_with(shlex.split("ls -la"))

    def test_shell_with_wait_delegates_to_run_blocking(self, svc):
        with patch.object(svc, "_run_blocking") as mock_blocking:
            svc._run_step(
                {
                    "action": "shell",
                    "command": "long_task.sh",
                    "wait": True,
                    "wait_threshold": 5,
                }
            )
        mock_blocking.assert_called_once_with("long_task.sh", 5)

    def test_notify_with_sound_plays_sound(self, svc, notifier):
        svc._run_step({"action": "notify", "sound": "alert.wav"})
        notifier.play_sound.assert_called_once_with("alert.wav")

    def test_notify_with_message_calls_notify_send(self, svc):
        with patch("services.sequence_service.subprocess.Popen") as mock_popen:
            svc._run_step({"action": "notify", "message": "done"})
        mock_popen.assert_called_once_with(["notify-send", "done"])

    def test_unknown_action_does_not_raise(self, svc):
        with patch("services.sequence_service.subprocess.Popen") as mock_popen:
            svc._run_step({"action": "unknown_xyz"})
        mock_popen.assert_not_called()
