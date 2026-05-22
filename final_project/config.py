import os

import yaml


class Config:
    def __init__(self):
        self.api_key = None
        self.api_host = None
        self.limit_message = None
        self.limit_chars = None
        self.temperature = 0.7
        self.system_prompt = None

        # Сначала читаем из yaml, если файл есть
        self._load_from_yaml()
        # Переменные окружения имеют приоритет
        self._load_from_env()

    def _load_from_yaml(self):
        config_path = 'config.yaml'
        if not os.path.exists(config_path):
            return

        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if not data:
                return

            self.api_key = data.get('api_key')
            self.api_host = data.get('api_host')
            self.limit_message = data.get('limit_message')
            self.limit_chars = data.get('limit_chars')
            self.temperature = data.get('temperature', 0.7)
            self.system_prompt = data.get('system_prompt')

    def _load_from_env(self):
        if os.environ.get('API_KEY'):
            self.api_key = os.environ.get('API_KEY')

        if os.environ.get('API_HOST'):
            self.api_host = os.environ.get('API_HOST')

        if os.environ.get('LIMIT_MESSAGE'):
            self.limit_message = int(os.environ.get('LIMIT_MESSAGE'))

        if os.environ.get('LIMIT_CHARS'):
            self.limit_chars = int(os.environ.get('LIMIT_CHARS'))

        if os.environ.get('TEMPERATURE'):
            self.temperature = float(os.environ.get('TEMPERATURE'))

    def is_valid(self):
        # API ключ и хост обязательны для работы
        return self.api_key is not None and self.api_host is not None