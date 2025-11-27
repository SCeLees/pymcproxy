import socket
import threading
import json
import struct
import os
import io
import time

# 读取服务器配置
def load_servers():
    if os.path.exists('servers.json'):
        with open('servers.json', 'r') as f:
            return json.load(f)
    return []

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
        try:
            # 创建到远程服务器的连接
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((self.remote_host, self.remote_port))
            
            # 处理Minecraft协议握手阶段
            # 第一步：接收客户端握手包
            handshake_packet = self.read_packet(client_socket)
            if not handshake_packet:
                raise Exception("Failed to read handshake packet")
            
            # 解析握手包确定下一步操作
            next_state = self.parse_handshake(handshake_packet)
            
            if next_state == 1:  # 状态请求（服务器列表ping）
                # 转发握手包到远程服务器
                self.write_packet(remote_socket, handshake_packet)
                
                # 接收状态请求包
                request_packet = self.read_packet(client_socket)
                # 转发状态请求包
                self.write_packet(remote_socket, request_packet)
                
                # 接收远程服务器的响应
                response_packet = self.read_packet(remote_socket)
                
                # 修改响应中的MOTD
                modified_response = self.modify_motd(response_packet)
                
                # 发送修改后的响应给客户端
                self.write_packet(client_socket, modified_response)
                
                # 处理可能的ping包
                try:
                    ping_packet = self.read_packet(client_socket)
                    self.write_packet(remote_socket, ping_packet)
                    pong_packet = self.read_packet(remote_socket)
                    self.write_packet(client_socket, pong_packet)
                except:
                    pass  # 忽略ping/pong错误
                
            else:  # 登录请求（实际游戏连接）
                # 转发握手包
                self.write_packet(remote_socket, handshake_packet)
                
                # 直接转发所有后续数据
                self.forward_all_data(client_socket, remote_socket)
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            try:
                client_socket.close()
                remote_socket.close()
            except:
                pass
                
    def read_packet(self, sock):
        """读取一个Minecraft协议包"""
        try:
            # 读取长度前缀（VarInt）
            length_bytes = b""
            while True:
                byte = sock.recv(1)
                if not byte:
                    return None
                length_bytes += byte
                # 检查是否是VarInt的结束
                if byte[0] & 0x80 == 0:
                    break
                # 防止无限循环
                if len(length_bytes) > 5:
                    return None
            
            # 解析长度
            length, _ = self.unpack_varint(length_bytes)
            
            # 读取数据部分
            data = b""
            while len(data) < length:
                chunk = sock.recv(length - len(data))
                if not chunk:
                    break
                data += chunk
            
            return data
        except:
            return None
    
    def write_packet(self, sock, data):
        """写入一个Minecraft协议包"""
        try:
            # 计算数据长度并打包
            length_prefix = self.pack_varint(len(data))
            # 发送长度+数据
            sock.sendall(length_prefix + data)
            return True
        except:
            return False
    
    def unpack_varint(self, data):
        """解包VARINT (Minecraft协议)"""
        value = 0
        position = 0
        for byte in data:
            value |= (byte & 0x7F) << position
            position += 7
            if (byte & 0x80) == 0:
                break
        return value, len(data)
    
    def parse_handshake(self, packet):
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
        string_length, string_length_size = self.unpack_varint(packet[offset:])
        offset += string_length_size + string_length
        
        # 跳过服务器端口 (Unsigned Short)
        offset += 2
        
        # 读取下一个状态
        if offset < len(packet):
            next_state = packet[offset]
            return next_state
        
        return 2  # 默认为登录
    
    def modify_motd(self, packet):
        """修改状态响应中的MOTD"""
        if not packet or len(packet) < 2:
            return packet
        
        try:
            # 包ID应该是0x00
            if packet[0] != 0x00:
                return packet
            
            # 解析JSON响应
            offset = 1
            json_length, json_length_size = self.unpack_varint(packet[offset:])
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
            new_json_length = self.pack_varint(len(new_json_bytes))
            
            # 构造新包
            new_packet = b"\x00" + new_json_length + new_json_bytes
            return new_packet
            
        except Exception as e:
            print(f"Error modifying MOTD: {e}")
            return packet
    
    def forward_all_data(self, client_socket, remote_socket):
        """转发所有数据直到连接关闭"""
        # 创建两个线程来转发数据
        to_remote = threading.Thread(
            target=self.forward_data, 
            args=(client_socket, remote_socket)
        )
        to_local = threading.Thread(
            target=self.forward_data, 
            args=(remote_socket, client_socket)
        )
        
        to_remote.daemon = True
        to_local.daemon = True
        
        to_remote.start()
        to_local.start()
        
        # 等待线程结束
        to_remote.join()
        to_local.join()
    
    def pack_varint(self, value):
        """打包VARINT (Minecraft协议)"""
        data = b""
        while True:
            if value & 0x7F == value:
                data += bytes([value])
                break
            else:
                data += bytes([(value & 0x7F) | 0x80])
                value >>= 7
        return data
    
    def forward_data(self, source, destination):
        """在两个socket之间转发数据"""
        try:
            while True:
                data = source.recv(4096)
                if not data:
                    break
                destination.sendall(data)
        except:
            pass
        finally:
            try:
                source.close()
                destination.close()
            except:
                pass
                
    def stop(self):
        """停止代理服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

# 全局代理实例字典
proxies = {}

def start_proxy(server_id):
    """启动指定ID的代理"""
    servers = load_servers()
    
    for server in servers:
        if server['id'] == server_id:
            # 如果代理已在运行，先停止它
            if server_id in proxies:
                stop_proxy(server_id)
                
            # 创建并启动新的代理实例
            proxy = MinecraftProxy(
                local_port=server.get('local_port', 25565),
                remote_host=server['remote_host'],
                remote_port=server['remote_port'],
                motd=server.get('motd', ''),
                icon=server.get('icon', '')
            )
            
            proxies[server_id] = proxy
            
            # 在新线程中启动代理
            proxy_thread = threading.Thread(target=proxy.start)
            proxy_thread.daemon = True
            proxy_thread.start()
            
            return True
    return False

def stop_proxy(server_id):
    """停止指定ID的代理"""
    if server_id in proxies:
        proxies[server_id].stop()
        del proxies[server_id]
        return True
    return False

def stop_all_proxies():
    """停止所有代理"""
    for server_id in list(proxies.keys()):
        stop_proxy(server_id)