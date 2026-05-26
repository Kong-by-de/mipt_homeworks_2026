import os
import re


class ChatSession:
    def __init__(self, limit_message=None, limit_chars=None):
        self.messages = []
        self.limit_message = limit_message
        self.limit_chars = limit_chars

    def add_message(self, role, content):
        # Если одно сообщение само больше лимита символов, обрезаем слева
        if self.limit_chars and len(content) > self.limit_chars:
            content = content[-self.limit_chars:]

        self.messages.append({'role': role, 'content': content})
        self._trim_history()

    def _trim_history(self):
        # Сначала проверяем лимит по количеству сообщений
        if self.limit_message:
            while len(self.messages) > self.limit_message:
                self.messages.pop(0)

        # Потом проверяем лимит по общему количеству символов
        if self.limit_chars:
            total_len = sum(len(msg['content']) for msg in self.messages)
            while total_len > self.limit_chars and len(self.messages) > 1:
                removed = self.messages.pop(0)
                total_len -= len(removed['content'])

    def get_history(self):
        return self.messages.copy()

    def clear(self):
        self.messages.clear()
        # Очищаем экран консоли - работает и на Windows, и на Unix
        os.system('cls' if os.name == 'nt' else 'clear')

    def process_file_references(self, text):
        # Ищем все вхождения @::путь:: в тексте
        pattern = r'@::(.*?)::'
        matches = re.findall(pattern, text)

        for filepath in matches:
            try:
                # Проверяем размер файла перед чтением (15 МБ = 15 * 1024 * 1024 байт)
                file_size = os.path.getsize(filepath)
                if file_size > 15 * 1024 * 1024:
                    replacement = f'\n[Ошибка: файл {filepath} больше 15 МБ]'
                else:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        replacement = '\n' + content
            except Exception as e:
                # Если файл не удалось прочитать, вставляем сообщение об ошибке
                replacement = f'\n[Ошибка чтения файла: {e}]'

            # Заменяем @::path:: на содержимое файла или сообщение об ошибке
            text = text.replace(f'@::{filepath}::', replacement)

        return text