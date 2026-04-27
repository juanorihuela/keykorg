from unittest.mock import MagicMock, patch

import pytest

from services.command_service import CommandService


@pytest.fixture
def notifier():
    return MagicMock()


@pytest.fixture
def svc(notifier):
    return CommandService(notifier)


class TestExecute:
    def test_happy_path_returns_true(self, svc):
        with patch("services.command_service.subprocess.Popen") as mock_popen:
            result = svc.execute("echo hello", "mypad")
        assert result is True
        mock_popen.assert_called_once_with(["echo", "hello"])

    def test_file_not_found_returns_false_and_warns(self, svc, notifier):
        with patch(
            "services.command_service.subprocess.Popen",
            side_effect=FileNotFoundError("not found"),
        ):
            result = svc.execute("nonexistent_cmd", "mypad")
        assert result is False
        notifier.notify_warning.assert_called_once_with("mypad", "Comando no encontrado")
        notifier.notify_alert.assert_not_called()

    def test_generic_error_returns_false_and_alerts(self, svc, notifier):
        with patch(
            "services.command_service.subprocess.Popen",
            side_effect=PermissionError("denied"),
        ):
            result = svc.execute("restricted_cmd", "mypad")
        assert result is False
        notifier.notify_alert.assert_called_once_with("mypad", "Error al ejecutar comando")
        notifier.notify_warning.assert_not_called()

    def test_empty_command_calls_popen_with_empty_list(self, svc):
        with patch("services.command_service.subprocess.Popen") as mock_popen:
            svc.execute("", "mypad")
        mock_popen.assert_called_once_with([])
