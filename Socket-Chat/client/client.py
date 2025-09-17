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

    ip = input("Enter server IP: ")
    port = input("Enter TCP port: ") #65432

    try:
        while True:
            client_socket = create_socket(ip, int(port))

            message = input("Client --> ")
            if not message.strip():
                continue  # skip empty input
            send_message(message, client_socket)

            data = client_socket.recv(1024)
            print("Server:", data.decode())

    except KeyboardInterrupt:
        print("\nExiting client...")

    finally:
        client_socket.close()