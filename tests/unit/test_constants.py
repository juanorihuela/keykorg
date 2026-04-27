from pathlib import Path
from unittest.mock import MagicMock

import pytest

from config.constants import SO_CATALOG


class TestSoCatalog:
    def test_debian_is_active(self):
        assert SO_CATALOG["debian"] == "active"

    def test_macos_is_pending(self):
        assert SO_CATALOG["macos"] == "pending"

    def test_all_values_are_valid_states(self):
        assert all(v in {"active", "pending"} for v in SO_CATALOG.values())


class TestMainAbortsOnPendingSo:
    def test_exits_with_1_when_so_is_pending(self, monkeypatch):
        import main as main_module

        mock_settings = MagicMock()
        mock_settings.is_pending = True
        mock_settings.so = "macos"
        mock_settings.log_level = "INFO"
        mock_settings.sounds_dir = Path("/tmp")

        monkeypatch.setattr("sys.argv", ["keykorg", "--so", "macos"])
        monkeypatch.setattr(main_module, "Settings", lambda so: mock_settings)
        monkeypatch.setattr(main_module.LogConfig, "setup", lambda level: None)
        monkeypatch.setattr(
            main_module, "NotificationService", MagicMock(return_value=MagicMock())
        )

        with pytest.raises(SystemExit) as exc_info:
            main_module.main()

        assert exc_info.value.code == 1
