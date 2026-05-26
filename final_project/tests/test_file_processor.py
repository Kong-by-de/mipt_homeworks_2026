import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch
from file_processor import FileProcessor


def test_file_processor_init():
    proc = FileProcessor()
    assert proc is not None


def test_file_processor_nonexistent_file(capsys):
    proc = FileProcessor()
    
    proc.process_chunk_mode(
        user_prompt='test',
        filepath='/nonexistent/file.txt',
        mode='paragraph',
        chunk_size=1,
        auto=True,
        session=None,
        client=None,
    )
    
    captured = capsys.readouterr()
    assert 'не найден' in captured.out


def test_file_processor_paragraph_mode(tmp_path):
    test_file = tmp_path / 'test.txt'
    test_file.write_text('Paragraph 1\n\nParagraph 2\n\nParagraph 3')
    
    mock_client = Mock()
    mock_client.ask.return_value = 'response'
    
    mock_session = Mock()
    mock_session.messages = [{'role': 'system', 'content': 'sys'}]
    
    proc = FileProcessor()
    
    with patch('builtins.input', return_value=''):
        with patch('builtins.print'):
            result = proc.process_chunk_mode(
                user_prompt='summarize',
                filepath=str(test_file),
                mode='paragraph',
                chunk_size=2,
                auto=True,
                session=mock_session,
                client=mock_client,
            )
    
    assert result is not None


def test_file_processor_len_mode(tmp_path):
    test_file = tmp_path / 'test.txt'
    test_file.write_text('a' * 100)
    
    mock_client = Mock()
    mock_client.ask.return_value = 'response'
    
    proc = FileProcessor()
    
    with patch('builtins.print'):
        result = proc.process_chunk_mode(
            user_prompt='test',
            filepath=str(test_file),
            mode='len',
            chunk_size=50,
            auto=True,
            session=None,
            client=mock_client,
        )
    
    assert result is not None


def test_file_processor_empty_file(tmp_path):
    test_file = tmp_path / 'empty.txt'
    test_file.write_text('')
    
    mock_client = Mock()
    mock_client.ask.return_value = 'response'
    
    proc = FileProcessor()
    
    with patch('builtins.print'):
        result = proc.process_chunk_mode(
            user_prompt='test',
            filepath=str(test_file),
            mode='paragraph',
            chunk_size=1,
            auto=True,
            session=None,
            client=mock_client,
        )
    
    assert result is not None