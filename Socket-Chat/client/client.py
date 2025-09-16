import socket



if __name__ == "__main__":
    # Create TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server
    client_socket.connect(("127.0.0.1", 65432))

    # Send and receive
    client_socket.sendall(b"Hello, server!")
    data = client_socket.recv(1024)

    print("Received:", data.decode())

    # Close
    client_socket.close()