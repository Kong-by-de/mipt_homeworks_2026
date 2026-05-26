import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from config import Config


def test_config_loads_defaults(monkeypatch):
    monkeypatch.setattr(os.path, 'exists', lambda x: False)
    monkeypatch.delenv('API_KEY', raising=False)
    monkeypatch.delenv('API_HOST', raising=False)
    
    cfg = Config()
    assert cfg.temperature == 0.7
    assert cfg.api_key is None
    assert cfg.api_host is None


def test_config_from_yaml(tmp_path, monkeypatch):
    monkeypatch.delenv('API_KEY', raising=False)
    monkeypatch.delenv('API_HOST', raising=False)
    
    config_file = tmp_path / 'config.yaml'
    config_file.write_text(
        'api_key: yaml_key\n'
        'api_host: http://yaml_host\n'
        'temperature: 0.8\n'
        'limit_message: 15\n'
    )
    
    monkeypatch.chdir(tmp_path)
    cfg = Config()
    
    assert cfg.api_key == 'yaml_key'
    assert cfg.api_host == 'http://yaml_host'
    assert cfg.temperature == 0.8
    assert cfg.limit_message == 15


def test_config_from_env(monkeypatch):
    monkeypatch.setattr(os.path, 'exists', lambda x: False)
    monkeypatch.setenv('API_KEY', 'env_key')
    monkeypatch.setenv('API_HOST', 'http://env_host')
    monkeypatch.setenv('TEMPERATURE', '0.9')
    monkeypatch.setenv('LIMIT_MESSAGE', '25')
    
    cfg = Config()
    
    assert cfg.api_key == 'env_key'
    assert cfg.api_host == 'http://env_host'
    assert cfg.temperature == 0.9
    assert cfg.limit_message == 25


def test_config_env_overrides_yaml(tmp_path, monkeypatch):
    config_file = tmp_path / 'config.yaml'
    config_file.write_text(
        'api_key: yaml_key\n'
        'api_host: http://yaml_host\n'
    )
    
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('API_KEY', 'env_key')
    
    cfg = Config()
    
    assert cfg.api_key == 'env_key'
    assert cfg.api_host == 'http://yaml_host'


def test_config_is_valid():
    cfg = Config()
    cfg.api_key = 'test_key'
    cfg.api_host = 'http://test'
    
    assert cfg.is_valid() is True


def test_config_is_invalid():
    cfg = Config()
    cfg.api_key = None
    cfg.api_host = 'http://test'
    
    assert cfg.is_valid() is False
    
    cfg.api_key = 'test_key'
    cfg.api_host = None
    
    assert cfg.is_valid() is False