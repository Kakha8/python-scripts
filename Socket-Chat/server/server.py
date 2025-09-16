import socket

if __name__=="__main__":
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind to IP and port
    server_socket.bind(("127.0.0.1", 65432))

    # Listen for incoming connections
    server_socket.listen()

    print("Server listening on port 65432...")

    # Accept a connection
    conn, addr = server_socket.accept()
    print("Connected by", addr)

    # Exchange data
    data = conn.recv(1024)  # Receive up to 1024 bytes
    conn.sendall(b"Hello, client!")

    # Close connection
    conn.close()