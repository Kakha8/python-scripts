import socket

def create_socket(ip, port):
    # Create TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server
    client_socket.connect((ip, port))

    return client_socket

def send_message(message, sock):
    sock.sendall(message.encode())



if __name__ == "__main__":


    try:
        while True:
            client_socket = create_socket("127.0.0.1", 65432)

            message = input("--> ")
            if not message.strip():
                continue  # skip empty input
            send_message(message, client_socket)

            data = client_socket.recv(1024)
            print("Received:", data.decode())

    except KeyboardInterrupt:
        print("\nExiting client...")

    finally:
        client_socket.close()