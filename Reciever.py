import socket
import time
from Sender import change_cc_algo


def main():
    ip = '127.0.0.1'
    port = 5555

    # Step 1: creating the TCP receiver socket.
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("TCP socket created successfully.")

    # bind the receiver_socket to ip and port.
    receiver_socket.bind((ip, port))
    print("bind successfully")

    # Step 2: waiting for incoming connections by listen() function and accept them by accept() func
    receiver_socket.listen()
    print("Listening...")

    sender_socket, sender_addr = receiver_socket.accept()
    print("Connection accepted!")

    # receiving from the sender the size of the file such that we will know the size of each half of file.
    size_bytes = sender_socket.recv(4)
    file_size = int.from_bytes(size_bytes, byteorder='big')
    print(f"The size of the file is: {file_size}")

    # define 2 lists that will save the times of each half.
    time_half1 = []
    time_half2 = []

    # We start a loop to receive the 2 parts of the file.
    while True:
        buffer = receiver_socket.getsockopt(socket.IPPROTO_TCP, socket.TCP_CONGESTION, 8)
        print("Current cc algorithm:", buffer.decode())
        print("Ready to receive the first half of the file.")

        # measure the time of receive of the first half of the file
        before_recv_time_half1 = time.time()

        # Step 3: receiving the first half.
        total_bytes_received = 0
        while total_bytes_received < (file_size // 2):
            buffer_reply = sender_socket.recv(file_size // 2)
            total_bytes_received += len(buffer_reply)

        # Step 4: measure the time of receiving the first half.
        after_recv_time_half1 = time.time()

        # Step 5: save the time it took to receive it.
        time_half1.append(after_recv_time_half1 - before_recv_time_half1)
        print("The first half has received successfully.")

        # Step 6: send authentication to sender.
        sender_socket.sendall(b"1000111001011")

        # Changing the cc algorithm.
        change_cc_algo(receiver_socket)

        print("Ready to receive the second half of the file.")

        # measure the time of receive of the second half of the file
        before_recv_time_half2 = time.time()

        # Step 7: receiving the second half.
        total_bytes_received = 0
        while total_bytes_received < (file_size // 2):
            buffer_reply = sender_socket.recv(file_size // 2)
            total_bytes_received += len(buffer_reply)

        # Step 8: measure the time of receiving the second half.
        after_recv_time_half2 = time.time()

        # Step 9: save the time it took to receive it.
        time_half2.append(after_recv_time_half2 - before_recv_time_half2)
        print("The second half has received successfully.")

        # changing the cc algorithm just in case the user will choose to continue.
        change_cc_algo(receiver_socket)

        # Step 10: if got an 'exit' message from the sender we close the connection.
        # else, continue to receive files.
        data = sender_socket.recv(1024)
        if data == b'exit':
            print("The sender told us to exit")
            print(f"Times for receiving the first half: {time_half1}")
            print(f"Average time for receiving the first half: {sum(time_half1) / len(time_half1)}")
            print(f"Times for receiving the second half: {time_half2}")
            print(f"Average time for receiving the second half: {sum(time_half2) / len(time_half2)}")

            receiver_socket.close()
            break


if __name__ == "__main__":
    main()
