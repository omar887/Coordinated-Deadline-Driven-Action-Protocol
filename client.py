from socket import *
import struct
import time
import heapq

server_ip = "127.0.0.1"
server_port = 5677

header = "!BBHIQQQ"
header_size = struct.calcsize(header)

client_socket = socket(AF_INET, SOCK_DGRAM)


def now_us():
    return time.time() * 1000000


seq_num = 1
t1 = int(now_us())

init_packet = struct.pack(header, 1, 1, 0, seq_num, t1, 0, 0)
client_socket.sendto(init_packet, (server_ip, server_port))

response, _ = client_socket.recvfrom(2048)
t4 = int(now_us())

response_fields = struct.unpack(header, response[:header_size])
t2 = response_fields[5]
t3 = response_fields[6]

offset = ((t2 - t1) + (t3 - t4)) / 2
print("Clock offset:", offset, "microseconds")

pending = []

try:
    while True:
        while pending and pending[0][0] <= now_us():
            target_local_time, command_seq, payload = heapq.heappop(pending)

            print("Executing action:", payload)
            actual_local_time = now_us()
            actual_server_time = int(actual_local_time + offset)

            confirmation = (
                f"ACTION_CONFIRM | "
                f"Sequence: {command_seq} | "
                f"Execution time: {actual_server_time}"
            )
            client_socket.sendto(confirmation.encode(), (server_ip, server_port))
            print("Confirmation sent to server. Sequence:", command_seq)

        if pending:
            wait = max((pending[0][0] - now_us()) / 1000000, 0.000001)
        else:
            wait = None

        client_socket.settimeout(wait)

        try:
            packet, _ = client_socket.recvfrom(2048)
        except timeout:
            continue

        if len(packet) < header_size:
            continue

        command_fields = struct.unpack(header, packet[:header_size])
        command_seq = command_fields[3]
        target_server_time = command_fields[4]
        payload = packet[header_size:].decode()

        print("Received command:", payload)
        print("Sequence number:", command_seq)

        target_local_time = target_server_time - offset

        if target_local_time <= now_us():
            print("Command expired. Dropping command.")
        else:
            heapq.heappush(pending, (target_local_time, command_seq, payload))

except KeyboardInterrupt:
    pass
finally:
    client_socket.close()
