# Coordinated Deadline-Driven Action Protocol

A small UDP protocol where a server tells a client to perform an action at a
specific future time. The client synchronizes its clock with the server, schedules the command against the server's clock, executes it at the deadline, and sends back a confirmation with the actual execution time so the server can measure the error.

**video link** : https://youtu.be/aaEHPIWAlVA  

## Running Locally

1. Clone the repo:

   ```bash
   git clone https://github.com/omar887/Coordinated-Deadline-Driven-Action-Protocol.git
   cd Coordinated-Deadline-Driven-Action-Protocol
   ```

2. Start the server in one terminal:
   ```bash
   python3 server.py
   ```

3. Start the client in a second terminal:

   ```bash
   python3 client.py
   ```

4. Go back to the server terminal and press **Enter** to send a command.
   The server schedules the action 500 ms in the future.

5. The client prints the received command, executes it at the deadline, and
   sends a confirmation. The server then prints the scheduled time, the
   actual execution time, and the execution error in µs/ms.

6. Stop the client with `Ctrl+C`.
