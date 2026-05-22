import os


class FileProcessor:
    def process_chunk_mode(
        self,
        user_prompt,
        filepath,
        mode='paragraph',
        chunk_size=1,
        auto=False,
        session=None,
        client=None,
    ):
        if not os.path.exists(filepath):
            print(f'[Ошибка: файл {filepath} не найден]')
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # разбиваем текст на чанки в зависимости от выбранного режима
        if mode == 'len':
            chunks = [
                content[i : i + chunk_size] for i in range(0, len(content), chunk_size)
            ]
        else:
            paragraphs = content.split('\n\n')
            chunks = []
            for i in range(0, len(paragraphs), chunk_size):
                chunk_paragraphs = paragraphs[i : i + chunk_size]
                chunks.append('\n\n'.join(chunk_paragraphs))

        print(f'\n[Найдено {len(chunks)} чанков. Начинаю обработку...]')

        results = []
        for idx, chunk in enumerate(chunks):
            print(f'\n=== Чанк {idx + 1}/{len(chunks)} ===')

            # формируем сообщение для модели
            prompt_text = f'{user_prompt}\n\nТекст:\n{chunk}'

            system_msg = {'role': 'system', 'content': 'Ты полезный ассистент.'}
            if session and session.messages and session.messages[0]['role'] == 'system':
                system_msg = session.messages[0]

            messages = [system_msg, {'role': 'user', 'content': prompt_text}]

            # отправляем запрос к LLM и получаем ответ
            response = client.ask(messages)
            if response:
                results.append(response)

            if not auto and idx < len(chunks) - 1:
                input('\n[Нажмите Enter для следующего чанка...]')

        print('\n[Обработка файла завершена]')
        return results