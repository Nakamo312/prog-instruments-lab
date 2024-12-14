import pytest
import logging
import socket
from unittest.mock import Mock, patch, MagicMock
from ..regex_processor import RegexProcessor
from ..logger import ChatLogger
from ..server import Server
from ..app import Start
from ..client import Client



@patch("socket.socket")
@patch("threading.Thread.start")
def test_server_accept_client(mock_thread_start, mock_socket):

    server = Server("127.0.0.1", 9000, "key123", "ServerNickname")

    mock_client_socket = Mock()
    mock_client_address = ("127.0.0.1", 12345)
    mock_socket_instance = mock_socket.return_value

    mock_socket_instance.accept.side_effect = [
        (mock_client_socket, mock_client_address),
        socket.error("Test Exception")          
    ]

    mock_client_socket.recv.side_effect = [
        b"TestAcc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        socket.error("Test Exception")            
    ]

    with patch.object(server, "handle_client") as mock_handle_client:
        with patch("logging.getLogger"):
            try:
                server.run()
            except socket.error as e:
                assert str(e) == "Test Exception"  

    assert mock_socket_instance.accept.call_count > 0, "accept не был вызван"
    mock_thread_start.assert_called_once()
    assert mock_client_socket in server.clients


@patch("socket.socket")
def test_client_connect_to_server(mock_socket):
    client = Client("127.0.0.1", 9000, "key123", "ClientNickname", Mock(), Mock())
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.connect.return_value = None 

    is_connected = client.connect_to_server()

    assert is_connected is True
    mock_socket_instance.connect.assert_called_once_with(("127.0.0.1", 9000))

@patch("socket.socket")
@patch("queue.Queue.put")
def test_client_receive_msg(mock_queue_put, mock_socket):
    mock_queue = Mock()
    client = Client(
        "127.0.0.1",
        9000,
        "key123",
        "ClientNickname",
        mock_queue,
        Mock()
    )
    client.socket = mock_socket.return_value
    client.socket.recv.side_effect = [
        b"MessageTestUser\x00\x00\x00\x00\x00\x00\x00\x00",
        b"",
    ]
    with patch("logging.getLogger"):
        client.receive_msg()
    mock_queue.put.assert_called_once_with("TestUser: Message")
    assert client.socket.recv.call_count == 2 


@patch("builtins.input", side_effect=["S", "key123"])
@patch("App.server.Server.run")
def test_start_server(mock_server_run, mock_input):
    with patch("logging.getLogger"):
        Start.main_start()

    mock_server_run.assert_called_once()


@patch("builtins.input", side_effect=["C", "key123", "ClientNickname"])
@patch("App.client.Client.connect_to_server", return_value=True)
@patch("App.client.Client.run")
def test_start_client(mock_client_run, mock_connect_to_server, mock_input):
    with patch("logging.getLogger"):
        Start.main_start()

    mock_connect_to_server.assert_called_once()
    mock_client_run.assert_called_once()