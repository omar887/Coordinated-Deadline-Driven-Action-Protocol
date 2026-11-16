from socket import *
import struct
import time
import heapq

server_ip = "127.0.0.1"
server_port = 5677

header = "!BBHIQQQ"
header_size = struct.calcsize(header)

VERSION = 1
SYNC_REQUEST = 1
SYNC_RESPONSE = 2
ACTION_COMMAND = 3
ACTION_CONFIRM = 4

SYNC_INTERVAL_US = 5_000_000
MIN_WAIT_S = 0.001

client_socket = socket(AF_INET, SOCK_DGRAM)


def now_us():
    return time.time_ns() // 1000


def send_message(msg_type, seq, t1=0, t2=0, t3=0, flags=0):
    packet = struct.pack(header, VERSION, msg_type, flags, seq, t1, t2, t3)
    client_socket.sendto(packet, (server_ip, server_port))


def compute_offset(t1, t2, t3, t4):
    return ((t2 - t1) + (t3 - t4)) // 2


seq_num = 1
t1 = now_us()
send_message(SYNC_REQUEST, seq_num, t1)

response, _ = client_socket.recvfrom(2048)
t4 = now_us()

response_fields = struct.unpack(header, response[:header_size])
t2 = response_fields[5]
t3 = response_fields[6]

offset = compute_offset(t1, t2, t3, t4)
print("Clock offset:", offset, "microseconds")

pending = []
sync_seq = None
sync_t1 = None
next_sync_time = now_us() + SYNC_INTERVAL_US

try:
    while True:
        while pending and pending[0][0] - offset <= now_us():
            target_server_time, command_seq, payload = heapq.heappop(pending)

            actual_server_time = now_us() + offset
            print("Executing action:", payload)

            send_message(ACTION_CONFIRM, command_seq, actual_server_time)
            print("Confirmation sent to server. Sequence:", command_seq)

        if now_us() >= next_sync_time:
            seq_num += 1
            sync_seq = seq_num
            sync_t1 = now_us()
            send_message(SYNC_REQUEST, sync_seq, sync_t1)
            next_sync_time = sync_t1 + SYNC_INTERVAL_US

        deadline = next_sync_time
        if pending:
            deadline = min(deadline, pending[0][0] - offset)

        wait = max((deadline - now_us()) / 1_000_000, MIN_WAIT_S)
        client_socket.settimeout(wait)

        try:
            packet, _ = client_socket.recvfrom(2048)
        except timeout:
            continue

        received_at = now_us()

        if len(packet) < header_size:
            continue

        fields = struct.unpack(header, packet[:header_size])
        msg_type = fields[1]
        packet_seq = fields[3]

        if msg_type == SYNC_RESPONSE:
            if packet_seq == sync_seq:
                offset = compute_offset(sync_t1, fields[5], fields[6], received_at)
                sync_seq = None
                print("Clock offset updated:", offset, "microseconds")

        elif msg_type == ACTION_COMMAND:
            target_server_time = fields[4]
            payload = packet[header_size:].decode()

            print("Received command:", payload)
            print("Sequence number:", packet_seq)

            if target_server_time - offset <= now_us():
                print("Command expired. Dropping command.")
            else:
                heapq.heappush(pending, (target_server_time, packet_seq, payload))

except KeyboardInterrupt:
    pass
finally:
    client_socket.close()
