import socket
import threading
import json
import struct
import time

class MinecraftProxy:
    def __init__(self, local_port, remote_host, remote_port, motd="", icon=""):
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.motd = motd
        self.icon = icon
        self.running = False
        self.server_socket = None

    def start(self):
        """启动代理服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.local_port))
            self.server_socket.listen(5)
            self.running = True

            print(f"Minecraft proxy started on port {self.local_port}")
            print(f"Forwarding to {self.remote_host}:{self.remote_port}")

            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"New connection from {addr}")

                    # 为每个客户端连接创建一个新线程
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connections: {e}")

        except Exception as e:
            print(f"Failed to start proxy on port {self.local_port}: {e}")

    def handle_client(self, client_socket):
        """处理客户端连接"""
        remote_socket = None
        try:
            # 创建到远程服务器的连接
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((self.remote_host, self.remote_port))

            # 处理Minecraft协议握手阶段
            handshake_done = False
            status_mode = False
            
            # 首先接收握手包
            handshake_packet = self._recv_packet(client_socket)
            if not handshake_packet:
                return
                
            # 解析握手包
            next_state = self._parse_handshake(handshake_packet)
            if next_state == 1:  # 状态请求
                status_mode = True
            elif next_state == 2:  # 登录请求
                status_mode = False
            handshake_done = True
            
            # 转发握手包
            self._send_packet(remote_socket, handshake_packet)

            if status_mode:
                # 状态请求模式
                # 接收状态请求包 (必须是 0x00)
                status_request_packet = self._recv_packet(client_socket)
                if status_request_packet and len(status_request_packet) == 1 and status_request_packet[0] == 0x00:
                    # 转发状态请求包
                    self._send_packet(remote_socket, status_request_packet)
                    
                    # 接收服务器响应
                    server_response = self._recv_packet(remote_socket)
                    
                    # 修改MOTD
                    modified_response = self._modify_motd(server_response)
                    self._send_packet(client_socket, modified_response)
                    
                    # 等待并处理ping包
                    try:
                        ping_packet = self._recv_packet(client_socket)
                        if ping_packet and len(ping_packet) == 9 and ping_packet[0] == 0x01:
                            # 转发ping包
                            self._send_packet(remote_socket, ping_packet)
                            # 接收pong包
                            pong_packet = self._recv_packet(remote_socket)
                            # 转发pong包
                            self._send_packet(client_socket, pong_packet)
                    except Exception as e:
                        print(f"Ping/Pong handling error: {e}")
                
                # 状态请求处理完毕，关闭连接
                client_socket.close()
                remote_socket.close()
                return
            else:
                # 登录模式，直接转发所有数据
                self._forward_connection(client_socket, remote_socket)

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            try:
                if remote_socket:
                    remote_socket.close()
            except:
                pass

    def _recv_packet(self, sock):
        """接收Minecraft协议包"""
        try:
            # 读取长度前缀（VarInt）
            length = self._read_varint(sock)
            if length <= 0:
                return None

            # 读取数据部分
            data = sock.recv(length)
            return data
        except:
            return None

    def _send_packet(self, sock, data):
        """发送Minecraft协议包"""
        try:
            # 计算数据长度并打包
            length_prefix = self._write_varint(len(data))
            # 发送长度+数据
            sock.sendall(length_prefix + data)
            return True
        except:
            return False

    def _read_varint(self, sock):
        """读取VarInt"""
        value = 0
        position = 0
        while True:
            byte = ord(sock.recv(1))
            value |= (byte & 0x7F) << position
            position += 7
            if (byte & 0x80) == 0:
                break
        return value

    def _write_varint(self, value):
        """写入VarInt"""
        data = b""
        while True:
            if value & 0x7F == value:
                data += bytes([value])
                break
            else:
                data += bytes([(value & 0x7F) | 0x80])
                value >>= 7
        return data

    def _parse_handshake(self, packet):
        """解析握手包，返回下一个状态 (1=状态, 2=登录)"""
        if not packet or len(packet) < 2:
            return 2  # 默认为登录

        # 跳过包ID (0x00)
        offset = 1

        # 跳过协议版本 (VarInt)
        while offset < len(packet) and (packet[offset] & 0x80) != 0:
            offset += 1
        offset += 1

        # 跳过服务器地址 (String)
        if offset >= len(packet):
            return 2
        string_length, string_length_size = self._decode_varint(packet[offset:])
        offset += string_length_size + string_length

        # 跳过服务器端口 (Unsigned Short)
        offset += 2

        # 读取下一个状态
        if offset < len(packet):
            next_state = packet[offset]
            return next_state

        return 2  # 默认为登录

    def _decode_varint(self, data):
        """解码VarInt"""
        value = 0
        position = 0
        for i, byte in enumerate(data):
            value |= (byte & 0x7F) << position
            position += 7
            if (byte & 0x80) == 0:
                return value, i + 1
        return value, len(data)

    def _modify_motd(self, packet):
        """修改状态响应中的MOTD"""
        if not packet or len(packet) < 2:
            return packet

        try:
            # 包ID应该是0x00
            if packet[0] != 0x00:
                return packet

            # 解析JSON响应
            offset = 1
            json_length, json_length_size = self._decode_varint(packet[offset:])
            offset += json_length_size

            if offset + json_length > len(packet):
                return packet

            json_data = packet[offset:offset+json_length]
            status_response = json.loads(json_data.decode('utf-8'))

            # 修改MOTD
            if self.motd:
                status_response["description"] = {"text": self.motd}

            # 修改favicon
            if self.icon:
                status_response["favicon"] = self.icon

            # 重新打包
            new_json = json.dumps(status_response, ensure_ascii=True)
            new_json_bytes = new_json.encode('utf-8')
            new_json_length = self._write_varint(len(new_json_bytes))

            # 构造新包
            new_packet = b"\x00" + new_json_length + new_json_bytes
            return new_packet

        except Exception as e:
            print(f"Error modifying MOTD: {e}")
            return packet

    def _forward_connection(self, client_socket, remote_socket):
        """转发客户端和远程服务器之间的所有数据"""
        try:
            while self.running:
                # 从客户端读取数据
                client_data = self._recv_packet(client_socket)
                if not client_data:
                    break
                self._send_packet(remote_socket, client_data)
                
                # 从远程服务器读取数据
                remote_data = self._recv_packet(remote_socket)
                if not remote_data:
                    break
                self._send_packet(client_socket, remote_data)
        except Exception as e:
            print(f"Error forwarding data: {e}")

    def stop(self):
        """停止代理服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()


# 测试代码
if __name__ == "__main__":
    # 创建代理实例
    proxy = MinecraftProxy(
        local_port=25566,
        remote_host="127.0.0.1",
        remote_port=25565,
        motd="Custom MOTD from Proxy!",
        icon=""
    )
    
    # 启动代理
    try:
        proxy.start()
    except KeyboardInterrupt:
        print("Shutting down proxy...")
        proxy.stop()