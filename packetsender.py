import socket
import asyncio

from packetbuilder import packetbuilder

class UDPHandler:
    def __init__(self):
        self.packet_builder = packetbuilder()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind(("0.0.0.0", 21200))
        self.slimevr_port = 6969
        self.broadcast_ip = "255.255.255.255"
        self.slimevr_ip = self.broadcast_ip

    async def heartbeat(self):
        while True:
            if self.slimevr_ip != self.broadcast_ip:
                packet = self.packet_builder.heartbeat_packet
                self.send_packet(packet)
            await asyncio.sleep(0.8)

    async def reset(self):
        self.send_packet(self.packet_builder.reset_packet())

    def send_packet(self, packet):
        self.socket.sendto(packet, (self.slimevr_ip, self.slimevr_port))

    async def handshake(self, imu_type, board_type, mcu_type):
        self.slimevr_ip = self.broadcast_ip

        result = ""
        while result == "":
            await asyncio.sleep(0.5)
            packet = self.packet_builder.build_handshake_packet(imu_type, board_type, mcu_type)
            self.send_packet(packet)

            result = await self.listen_for_handshake()

            
        #print("Server was found!")
        return "Found server:\n" + result


    async def listen_for_handshake(self):
        timeout = 10  # Timeout in seconds
        end_time = asyncio.get_event_loop().time() + timeout

        while True:
            if asyncio.get_event_loop().time() > end_time:
                return ""  # Return empty string to indicate timeout

            try:
                self.socket.settimeout(end_time - asyncio.get_event_loop().time())  # Set timeout for receiving data
                data, address = self.socket.recvfrom(1024)
            except socket.timeout:
                return ""  # Return empty string to indicate timeout

            received_message = data.decode("utf-8", "ignore") 

            if "Hey OVR =D 5" in received_message:
                self.slimevr_ip = address[0]  # Update slimevrIp with the sender's IP address
                return self.slimevr_ip
    
    async def add_imu(self, imu_type):
        if self.slimevr_ip == self.broadcast_ip:
            #print("SlimeVR Server not found!")
            return "Server not found"

        packet = self.packet_builder.build_imu_packet(imu_type)
        self.send_packet(packet)

        return "Added IMU"

    async def rotate_imu(self, imu_id, rotation):
        if self.slimevr_ip == self.broadcast_ip:
            return "Server not found"
        packet = self.packet_builder.build_rotation_packet(imu_id, rotation)
        self.send_packet(packet)
        return f"Rotated IMU {imu_id}"
