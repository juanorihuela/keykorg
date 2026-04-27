from pathlib import Path

import pytest

from config.settings import Settings

_ENV_BASE = "MIDI_DEVICE=hw:1,0,0\nSOUNDS_DIR=sounds\nCOMMANDS_FILE=commands.yml\n"


@pytest.fixture
def setup_debian(tmp_path, monkeypatch):
    monkeypatch.setattr("config.settings.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("config.settings.get_host_so", lambda: "debian")
    (tmp_path / ".env.debian").write_text(_ENV_BASE)
    return tmp_path


@pytest.fixture
def debian_settings(setup_debian):
    return Settings("debian")


class TestValidateSo:
    def test_unknown_so_raises_value_error(self, tmp_path, monkeypatch):
        monkeypatch.setattr("config.settings.PROJECT_ROOT", tmp_path)
        monkeypatch.setattr("config.settings.get_host_so", lambda: None)
        with pytest.raises(ValueError, match="windows"):
            Settings("windows")

    def test_host_mismatch_raises_value_error(self, tmp_path, monkeypatch):
        monkeypatch.setattr("config.settings.PROJECT_ROOT", tmp_path)
        monkeypatch.setattr("config.settings.get_host_so", lambda: "debian")
        with pytest.raises(ValueError, match="debian"):
            Settings("macos")

    def test_valid_so_matching_host_does_not_raise(self, setup_debian):
        Settings("debian")

    def test_host_none_allows_any_catalog_so(self, tmp_path, monkeypatch):
        monkeypatch.setattr("config.settings.PROJECT_ROOT", tmp_path)
        monkeypatch.setattr("config.settings.get_host_so", lambda: None)
        (tmp_path / ".env.macos").write_text(_ENV_BASE)
        Settings("macos")


class TestInit:
    def test_missing_env_file_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr("config.settings.PROJECT_ROOT", tmp_path)
        monkeypatch.setattr("config.settings.get_host_so", lambda: "debian")
        with pytest.raises(FileNotFoundError):
            Settings("debian")

    def test_fields_have_correct_types(self, debian_settings, tmp_path):
        assert debian_settings.midi_device == "hw:1,0,0"
        assert isinstance(debian_settings.sounds_dir, Path)
        assert isinstance(debian_settings.commands_file, Path)

    def test_log_level_defaults_to_info(self, debian_settings):
        assert debian_settings.log_level == "INFO"

    def test_is_pending_false_for_active_so(self, debian_settings):
        assert debian_settings.is_pending is False

    def test_is_pending_true_for_pending_so(self, tmp_path, monkeypatch):
        monkeypatch.setattr("config.settings.PROJECT_ROOT", tmp_path)
        monkeypatch.setattr("config.settings.get_host_so", lambda: None)
        (tmp_path / ".env.macos").write_text(_ENV_BASE)
        assert Settings("macos").is_pending is True


class TestLoadPadMap:
    def test_missing_commands_file_raises(self, debian_settings):
        with pytest.raises(FileNotFoundError):
            debian_settings.load_pad_map()

    def test_malformed_yaml_raises(self, debian_settings, tmp_path):
        (tmp_path / "commands.yml").write_text("[")
        with pytest.raises(ValueError, match="YAML malformado"):
            debian_settings.load_pad_map()

    def test_without_imports_returns_pads(self, debian_settings, tmp_path):
        (tmp_path / "commands.yml").write_text(
            "pads:\n  1:\n    name: test\n    type: simple\n    command: echo hello\n"
        )
        pad_map = debian_settings.load_pad_map()
        assert 1 in pad_map
        assert pad_map[1]["name"] == "test"

    def test_with_imports_merges_all_pads(self, debian_settings, tmp_path):
        (tmp_path / "a.yml").write_text(
            "pads:\n  1:\n    name: pad_a\n    type: simple\n    command: echo a\n"
        )
        (tmp_path / "b.yml").write_text(
            "pads:\n  2:\n    name: pad_b\n    type: simple\n    command: echo b\n"
        )
        (tmp_path / "commands.yml").write_text("imports:\n  - a.yml\n  - b.yml\n")
        pad_map = debian_settings.load_pad_map()
        assert 1 in pad_map
        assert 2 in pad_map

    def test_imports_last_file_wins_on_collision(self, debian_settings, tmp_path):
        (tmp_path / "a.yml").write_text(
            "pads:\n  1:\n    name: first\n    type: simple\n    command: echo a\n"
        )
        (tmp_path / "b.yml").write_text(
            "pads:\n  1:\n    name: last\n    type: simple\n    command: echo b\n"
        )
        (tmp_path / "commands.yml").write_text("imports:\n  - a.yml\n  - b.yml\n")
        pad_map = debian_settings.load_pad_map()
        assert pad_map[1]["name"] == "last"
