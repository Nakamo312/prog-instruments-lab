import pytest
import socket
import queue
from unittest.mock import Mock, patch, MagicMock
from ..server import Server
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
    
@pytest.fixture
def mock_socket():
    """Fixture to mock socket."""
    with patch('socket.socket') as mock_socket_class:
        mock_socket_instance = MagicMock() 
        mock_socket_class.return_value = mock_socket_instance
        yield mock_socket_instance


@pytest.fixture
def client(mock_socket):
    """Fixture to create a Client instance with mocked socket and queue."""
    client = Client(ip_adr='127.0.0.1', port=12345, key='secret_key', nickname='testuser', 
                    queue=queue.Queue(), queue_send=queue.Queue())
    client.socket = mock_socket
    return client

def test_send_msg(client):
    """Test the send_msg method."""
    message = "Hello, Server!"
    client.queue_send.put(message)
    assert not client.queue_send.empty(), "Queue is empty, message was not added"
    client.send_msg(exit_after_one=True)
    expected_message = (
        message.encode("utf-8") + 
        b'\x00' * (16 - len(client.nickname)) +
        client.nickname.encode("utf-8")
    )

    client.socket.send.assert_called_once_with(expected_message)




