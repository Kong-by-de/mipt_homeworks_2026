import sys

from config import Config
from chat_session import ChatSession
from file_processor import FileProcessor
from llm_client import LLMClient


def show_help():
    print('\nДоступные команды:')
    print('  /reset       - очистить историю чата')
    print('  /file_chunk  - режим обработки файла по частям')
    print('  \\q          - выйти из программы')
    print('  @::путь::    - прикрепить файл к сообщению')


def parse_file_chunk_command(args):
    filepath = None
    mode = 'paragraph'
    chunk_size = 1
    auto = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('paragraph='):
            mode = 'paragraph'
            chunk_size = int(arg.split('=')[1])
        elif arg.startswith('len='):
            mode = 'len'
            chunk_size = int(arg.split('=')[1])
        elif arg == '-y':
            auto = True
        elif not arg.startswith('-') and not arg.startswith('='):
            if filepath is None:
                filepath = arg
        i += 1

    return filepath, mode, chunk_size, auto


def main():
    cfg = Config()

    if not cfg.is_valid():
        print('[Ошибка] Не найдена конфигурация.')
        print('Создайте config.yaml или установите переменные окружения:')
        print('  API_KEY - ваш API ключ')
        print('  API_HOST - адрес сервера (например, http://localhost:11434/v1/)')
        sys.exit(1)

    session = ChatSession(
        limit_message=cfg.limit_message,
        limit_chars=cfg.limit_chars,
    )

    client = LLMClient(
        cfg.api_key,
        cfg.api_host,
        cfg.temperature,
    )

    file_proc = FileProcessor()

    if cfg.system_prompt:
        session.add_message('system', cfg.system_prompt)

    show_help()

    while True:
        try:
            user_input = input('\n>>> ').strip()
        except EOFError:
            break

        if not user_input:
            continue

        if user_input == '\\q':
            print('\n[Выход из программы]')
            break

        if user_input == '/reset':
            session.clear()
            if cfg.system_prompt:
                session.add_message('system', cfg.system_prompt)
            continue

        if user_input.startswith('/file_chunk'):
            parts = user_input.split()
            filepath, mode, chunk_size, auto = parse_file_chunk_command(parts[1:])

            if not filepath:
                filepath = input('Введите путь к файлу: ').strip()

            user_prompt = input('Что нужно сделать с каждым фрагментом? ').strip()

            file_proc.process_chunk_mode(
                user_prompt, filepath, mode, chunk_size, auto, session, client
            )
            continue

        processed_text = session.process_file_references(user_input)
        session.add_message('user', processed_text)

        print('\n[Ассистент]: ', end='', flush=True)

        response = client.ask(session.get_history(), stream=True)

        if response:
            session.add_message('assistant', response)


if __name__ == '__main__':
    main()