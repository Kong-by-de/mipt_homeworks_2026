import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch
from llm_client import LLMClient


def test_llm_client_init():
    client = LLMClient(
        api_key='test_key',
        api_host='http://test',
        temperature=0.8,
    )
    
    assert client.temperature == 0.8
    assert client.client is not None


def test_llm_client_ask_non_stream():
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = 'test response'
    
    with patch('llm_client.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        client = LLMClient(api_key='key', api_host='http://test')
        result = client.ask([{'role': 'user', 'content': 'hi'}], stream=False)
        
        assert result == 'test response'


def test_llm_client_ask_stream():
    mock_chunk1 = Mock()
    mock_chunk1.choices = [Mock()]
    mock_chunk1.choices[0].delta = Mock()
    mock_chunk1.choices[0].delta.content = 'Hello '
    
    mock_chunk2 = Mock()
    mock_chunk2.choices = [Mock()]
    mock_chunk2.choices[0].delta = Mock()
    mock_chunk2.choices[0].delta.content = 'World'
    
    mock_response = [mock_chunk1, mock_chunk2]
    
    with patch('llm_client.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        client = LLMClient(api_key='key', api_host='http://test')
        
        with patch('builtins.print'):
            result = client.ask([{'role': 'user', 'content': 'hi'}], stream=True)
            
            assert 'Hello ' in result
            assert 'World' in result


def test_llm_client_keyboard_interrupt():
    with patch('llm_client.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = KeyboardInterrupt()
        
        client = LLMClient(api_key='key', api_host='http://test')
        
        with patch('builtins.print'):
            result = client.ask([{'role': 'user', 'content': 'hi'}])
            assert result is None


def test_llm_client_exception():
    with patch('llm_client.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = Exception('API Error')
        
        client = LLMClient(api_key='key', api_host='http://test')
        
        with patch('builtins.print'):
            result = client.ask([{'role': 'user', 'content': 'hi'}])
            assert result is None