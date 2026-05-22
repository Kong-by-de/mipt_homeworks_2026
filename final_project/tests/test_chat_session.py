import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from chat_session import ChatSession


def test_add_message():
    session = ChatSession()
    session.add_message('user', 'привет')
    
    assert len(session.messages) == 1
    assert session.messages[0]['role'] == 'user'
    assert session.messages[0]['content'] == 'привет'


def test_get_history():
    session = ChatSession()
    session.add_message('user', 'msg1')
    session.add_message('assistant', 'msg2')
    
    history = session.get_history()
    
    assert len(history) == 2
    assert history[0]['content'] == 'msg1'
    assert history[1]['content'] == 'msg2'


def test_trim_by_message_count():
    session = ChatSession(limit_message=3)
    
    session.add_message('user', '1')
    session.add_message('user', '2')
    session.add_message('user', '3')
    session.add_message('user', '4')
    
    assert len(session.messages) == 3
    assert session.messages[0]['content'] == '2'


def test_trim_by_chars():
    session = ChatSession(limit_chars=20)
    
    session.add_message('user', 'a' * 15)
    session.add_message('user', 'b' * 10)
    
    total_chars = sum(len(msg['content']) for msg in session.messages)
    assert total_chars <= 20


def test_trim_both_limits():
    session = ChatSession(limit_message=5, limit_chars=50)
    
    for i in range(10):
        session.add_message('user', f'message {i}' * 5)
    
    assert len(session.messages) <= 5
    total_chars = sum(len(m['content']) for m in session.messages)
    assert total_chars <= 50


def test_clear():
    session = ChatSession()
    session.add_message('user', 'test')
    
    assert len(session.messages) == 1
    
    session.clear()
    
    assert len(session.messages) == 0


def test_file_reference_replaces_content(tmp_path):
    session = ChatSession()
    
    test_file = tmp_path / 'code.py'
    test_file.write_text('print("hello")')
    
    text = f'проверь код @::{test_file}::'
    result = session.process_file_references(text)
    
    assert 'print("hello")' in result
    assert '@::' not in result


def test_file_reference_handles_missing_file():
    session = ChatSession()
    
    result = session.process_file_references('файл @::nonexistent.txt::')
    
    assert 'Ошибка чтения файла' in result


def test_file_too_large(tmp_path):
    session = ChatSession()
    
    large_file = tmp_path / 'large.txt'
    with open(large_file, 'w') as f:
        f.write('x' * (16 * 1024 * 1024))
    
    text = f'@::{large_file}::'
    result = session.process_file_references(text)
    
    assert 'больше 15 МБ' in result


def test_multiple_file_references(tmp_path):
    session = ChatSession()
    
    file1 = tmp_path / 'file1.txt'
    file1.write_text('content1')
    
    file2 = tmp_path / 'file2.txt'
    file2.write_text('content2')
    
    text = f'Check @::{file1}:: and @::{file2}::'
    result = session.process_file_references(text)
    
    assert 'content1' in result
    assert 'content2' in result


def test_empty_limits():
    session = ChatSession()
    session.add_message('user', 'test')
    
    assert len(session.messages) == 1