import socket


def authentication_check(sock):
    my_authentication = b"1000111001011"
    check = sock.recv(1024)
    if my_authentication != check:
        print("Process failed")
        sock.close()
    else:
        print("Process succeed")


def change_cc_algo(sock):
    buffer = sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_CONGESTION, 8)
    buffer_decoded = buffer.decode().strip('\x00')
    print("Current cc algorithm:", buffer_decoded)
    cc_algos = ["reno", "cubic"]
    next_cc_algo = cc_algos[(cc_algos.index(buffer_decoded) + 1) % len(cc_algos)]
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CONGESTION, next_cc_algo.encode())
    print("New cc algorithm:", next_cc_algo)


def main():
    # Step 1: Open and read the file.
    with open("testFile.txt", "rb") as f:
        file_data = f.read()

    # Get the size of the file.
    size_of_file = len(file_data)
    print(f"The amount of bytes of the file is: {size_of_file}")

    # Find the size of each half.
    half_size_of_file = size_of_file // 2

    # Step 2: Create the TCP sender socket.
    ip = "127.0.0.1"
    port = 5555
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Define the receiver address.
    receiver_addr = (ip, port)
    receiver_prefix = f"{{{ip}:{port}}}"
    # Establish the connection with the receiver.
    try:
        sock.connect(receiver_addr)
    except socket.error as e:
        print("Error in the connection:", e)
        exit()
    print(f"{receiver_prefix} Connection established")

    # Sending to the receiver the size of the file in bytes such that he
    # will know how much he needs to receive for each half.
    sock.sendall(size_of_file.to_bytes(4, byteorder='big'))
    print("Sending to the receiver the size of the file.")

    # Sending the 2 parts of the file and changing the cc algorithm every iteration
    # until user choose to exit.
    while True:
        # Part 3: Sending the first half of the file.
        print("Sending part 1 of file")
        sock.sendall(file_data[:half_size_of_file])

        # Part 4: Checking authentication of the first half of the file.
        print("Authentication check")
        authentication_check(sock)

        # Part 5: Checking what cc algorithm we are using and changing to another cc algo
        change_cc_algo(sock)

        # Part 6: Send the second half of the file.
        print("Sending part 2 of the text")
        sock.sendall(file_data[half_size_of_file:])

        # Step 7: user decision: send the file again (Y) or exit (E).
        c = input("To send the file again please enter Y, to exit please enter E:\n")

        while c not in ('Y', 'E'):
            print("There is no such option, please enter again Y/E:")
            c = input()

        # if the decision is yes (send the file again)
        if c == 'Y':
            # Notify the receiver that the user chose to send the file again (1).
            sock.send(b'continue')

            # change back to cc algo.
            print("changing back the CC algo.")
            change_cc_algo(sock)

        else:
            # Notify the receiver that the user chose stop and close the connection.
            sock.send(b'exit')

            print("exiting...")
            break

            # Close the sender socket.
            sock.close()

            print("Connection closed.")


if __name__ == "__main__":
    main()
