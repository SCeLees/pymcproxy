import socket
import threading
import json
import struct
import os
import time
import io
from logger import get_logger
from stats import stats_manager

# 获取logger实例
logger = get_logger()

class EnhancedMinecraftProxy:
    def __init__(self, local_port, remote_host, remote_port, motd="", icon_path="", server_id=None, server_name=None):
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.motd = motd
        self.icon_path = icon_path
        self.server_id = server_id  # 添加服务器ID用于加载黑白名单配置
        self.server_name = server_name  # 添加服务器名称用于日志
        self.running = False
        self.server_socket = None
        self.icon_data = None
        
        # 如果提供了图标路径，加载图标数据
        if icon_path and os.path.exists(os.path.join('server-icons', icon_path)):
            try:
                with open(os.path.join('server-icons', icon_path), "rb") as f:
                    import base64
                    icon_bytes = f.read()
                    self.icon_data = "data:image/png;base64," + base64.b64encode(icon_bytes).decode('utf-8')
            except Exception as e:
                logger.error(f"Error loading icon: {e}")

    def start(self):
        """启动代理服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 设置 socket 超时，以便能够定期检查 self.running 状态
            self.server_socket.settimeout(1.0)  # 1秒超时
            self.server_socket.bind(('localhost', self.local_port))
            self.server_socket.listen(5)
            self.running = True

            logger.info(f"Minecraft proxy started on port {self.local_port}")
            logger.info(f"Forwarding to {self.remote_host}:{self.remote_port}")

            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    logger.info(f"[{self.server_name or 'Unknown'}] New connection from {addr}")

                    # 为每个客户端连接创建一个新线程
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    # 超时是正常的，继续循环以检查 self.running 状态
                    continue
                except socket.error as e:
                    # 如果 running 为 False，说明是主动停止，退出循环
                    if not self.running:
                        break
                    else:
                        # 如果不是主动停止，记录错误
                        if self.running:
                            logger.error(f"Error accepting connections: {e}")
                except Exception as e:
                    if self.running:
                        logger.error(f"Unexpected error in server loop: {e}")

        except Exception as e:
            logger.error(f"Failed to start proxy on port {self.local_port}: {e}")
        finally:
            # 确保服务器套接字被关闭
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass

    def handle_client(self, client_socket, addr):
        """处理客户端连接"""
        remote_socket = None
        connection_start_time = time.time()
        player_name = "Unknown"
        bytes_transferred = 0
        
        try:
            # 创建到远程服务器的连接
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((self.remote_host, self.remote_port))
            
            # 处理初始握手阶段
            # 读取客户端的第一个包（应该是握手包）
            first_packet = self.recv_packet(client_socket)
            if not first_packet:
                return  # 客户端立即断开，不记录日志
                
            # 检查是否是握手包
            if len(first_packet) > 0 and first_packet[0] == 0x00:
                # 解析握手包确定下一步状态
                next_state = self.parse_handshake(first_packet)
                
                if next_state == 1:  # 状态请求（服务器列表ping）
                    self.handle_status_request(client_socket, remote_socket, first_packet)
                    logger.debug(f"[{self.server_name or 'Unknown'}] Status request from {addr} completed")
                    return
                else:  # 登录请求
                    # 处理登录流程以获取玩家名称
                    player_name = self.handle_login(client_socket, remote_socket, first_packet)
                    if player_name != "Unknown":
                        logger.info(f"[{self.server_name or 'Unknown'}] Player '{player_name}' joined from {addr}")
                    else:
                        logger.debug(f"[{self.server_name or 'Unknown'}] Connection from {addr} (player name unknown)")
            
            # 对于登录或其他情况，直接转发所有数据
            transferred = self.forward_all_data(client_socket, remote_socket, addr)
            bytes_transferred += transferred

        except Exception as e:
            logger.error(f"[{self.server_name or 'Unknown'}] Error handling client {addr}: {e}")
        finally:
            connection_time = time.time() - connection_start_time
            # 更新统计数据
            stats_manager.update_app_stats(connections=1, traffic=bytes_transferred)
            stats_manager.update_player_stats(player_name, traffic=bytes_transferred, connection_time=connection_time)
            
            try:
                client_socket.close()
            except:
                pass
            try:
                if remote_socket:
                    remote_socket.close()
            except:
                pass
            
            # 只对实际玩家连接记录断开日志，忽略短暂连接（如状态请求）
            if player_name != "Unknown" or connection_time > 0.1 or bytes_transferred > 0:
                if player_name != "Unknown":
                    logger.info(f"[{self.server_name or 'Unknown'}] Player '{player_name}' left from {addr}, session: {connection_time:.2f}s, {bytes_transferred} bytes")
                else:
                    logger.debug(f"[{self.server_name or 'Unknown'}] Client {addr} disconnected after {connection_time:.2f}s, {bytes_transferred} bytes")

    def is_player_allowed(self, player_name):
        """检查玩家是否被允许连接"""
        # 如果没有服务器ID，则允许所有玩家连接
        if self.server_id is None:
            return True
            
        # 加载黑白名单配置
        try:
            with open('config/whitelist_blacklist.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，允许所有玩家连接
            return True
        except Exception as e:
            logger.error(f"Error loading whitelist/blacklist config: {e}")
            return True
            
        server_config = config.get(str(self.server_id), {'mode': 'none', 'players': []})
        mode = server_config['mode']
        players = server_config['players']
        
        # 根据模式检查玩家是否被允许
        if mode == 'whitelist':
            # 白名单模式：只有在白名单中的玩家才被允许
            return player_name in players
        elif mode == 'blacklist':
            # 黑名单模式：只有不在黑名单中的玩家才被允许
            return player_name not in players
        else:
            # 无限制模式：允许所有玩家
            return True

    def handle_login(self, client_socket, remote_socket, handshake_packet):
        """处理登录流程并提取玩家名称"""
        try:
            # 转发握手包
            self.send_packet(remote_socket, handshake_packet)
            
            # 等待并读取登录开始包（应该包含玩家名称）
            login_start_packet = self.recv_packet(client_socket)
            if not login_start_packet:
                return "Unknown"
                
            # 检查是否是登录开始包 (0x00)
            if len(login_start_packet) > 0 and login_start_packet[0] == 0x00:
                # 解析玩家名称
                player_name = self.parse_login_start_packet(login_start_packet)
                if player_name:
                    # 检查玩家是否被允许连接
                    if not self.is_player_allowed(player_name):
                        logger.info(f"Player {player_name} denied access due to whitelist/blacklist rules")
                        # 直接关闭连接而不发送任何消息
                        return "Unknown"
                    
                    # 转发登录开始包
                    self.send_packet(remote_socket, login_start_packet)
                    return player_name
                    
            # 如果不是登录开始包，直接转发
            self.send_packet(remote_socket, login_start_packet)
            return "Unknown"
            
        except Exception as e:
            logger.error(f"Error in login handling: {e}")
            return "Unknown"

    def parse_login_start_packet(self, packet):
        """解析登录开始包以提取玩家名称"""
        try:
            # 包格式: [包ID: VarInt] [用户名: String]
            if len(packet) < 2 or packet[0] != 0x00:
                return None
                
            # 跳过包ID (0x00)
            offset = 1
            
            # 读取字符串长度 (VarInt)
            string_length = 0
            string_length_size = 0
            while True:
                if offset >= len(packet):
                    return None
                byte = packet[offset]
                string_length |= (byte & 0x7F) << (7 * string_length_size)
                string_length_size += 1
                offset += 1
                if (byte & 0x80) == 0 or string_length_size > 5:
                    break
                    
            # 读取用户名
            if offset + string_length <= len(packet):
                username_bytes = packet[offset:offset+string_length]
                username = username_bytes.decode('utf-8')
                return username
                
            return None
        except Exception as e:
            logger.error(f"Error parsing login start packet: {e}")
            return None

    def handle_status_request(self, client_socket, remote_socket, handshake_packet):
        """处理状态请求（服务器列表ping）"""
        try:
            # 转发握手包
            self.send_packet(remote_socket, handshake_packet)
            
            # 读取状态请求包
            status_request = self.recv_packet(client_socket)
            if not status_request or len(status_request) != 1 or status_request[0] != 0x00:
                return
                
            # 转发状态请求
            self.send_packet(remote_socket, status_request)
            
            # 读取服务器响应
            server_response = self.recv_packet(remote_socket)
            if not server_response:
                return
                
            # 修改响应中的MOTD和图标
            modified_response = self.modify_status_response(server_response)
            
            # 发送修改后的响应
            self.send_packet(client_socket, modified_response)
            
            # 处理ping/pong
            ping_packet = self.recv_packet(client_socket)
            if ping_packet and len(ping_packet) == 9 and ping_packet[0] == 0x01:
                self.send_packet(remote_socket, ping_packet)
                pong_packet = self.recv_packet(remote_socket)
                self.send_packet(client_socket, pong_packet)
                
        except Exception as e:
            logger.error(f"Error in status request handling: {e}")
        finally:
            try:
                client_socket.close()
                remote_socket.close()
            except:
                pass

    def forward_all_data(self, client_socket, remote_socket, addr):
        """转发所有数据（登录和游戏阶段）"""
        bytes_transferred = 0
        try:
            while self.running:
                # 使用select来同时监听两个socket
                import select
                ready, _, _ = select.select([client_socket, remote_socket], [], [], 1.0)
                
                if not ready:
                    continue
                    
                for sock in ready:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            return bytes_transferred
                            
                        if sock is client_socket:
                            remote_socket.sendall(data)
                        else:
                            client_socket.sendall(data)
                            
                        bytes_transferred += len(data)
                    except:
                        return bytes_transferred
        except Exception as e:
            logger.error(f"Error forwarding data for client {addr}: {e}")
        finally:
            logger.info(f"Client {addr} disconnected, transferred {bytes_transferred} bytes")
            
        return bytes_transferred

    def recv_packet(self, sock):
        """接收Minecraft协议包"""
        try:
            # 读取长度前缀（VarInt）
            length_bytes = b""
            while True:
                byte = sock.recv(1)
                if not byte:
                    return None
                length_bytes += byte
                if byte[0] & 0x80 == 0:
                    break
                if len(length_bytes) > 5:
                    return None
            
            length = self.decode_varint(length_bytes)
            if length <= 0:
                return None

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

    def send_packet(self, sock, data):
        """发送Minecraft协议包"""
        try:
            # 计算数据长度并打包
            length_prefix = self.encode_varint(len(data))
            # 发送长度+数据
            sock.sendall(length_prefix + data)
            return len(length_prefix) + len(data)
        except:
            return 0

    def decode_varint(self, data):
        """解码VarInt"""
        value = 0
        position = 0
        for byte in data:
            value |= (byte & 0x7F) << position
            position += 7
            if (byte & 0x80) == 0:
                break
        return value

    def encode_varint(self, value):
        """编码VarInt"""
        data = b""
        while True:
            if value & 0x7F == value:
                data += bytes([value])
                break
            else:
                data += bytes([(value & 0x7F) | 0x80])
                value >>= 7
        return data

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
        string_length, string_length_size = self.decode_varint_from_bytes(packet[offset:])
        offset += string_length_size + string_length

        # 跳过服务器端口 (Unsigned Short)
        offset += 2

        # 读取下一个状态
        if offset < len(packet):
            next_state = packet[offset]
            return next_state

        return 2  # 默认为登录

    def decode_varint_from_bytes(self, data):
        """从字节数据中解码VarInt"""
        value = 0
        position = 0
        size = 0
        for byte in data:
            value |= (byte & 0x7F) << position
            position += 7
            size += 1
            if (byte & 0x80) == 0:
                break
        return value, size

    def modify_status_response(self, packet):
        """修改状态响应中的MOTD和图标"""
        if not packet or len(packet) < 2:
            return packet

        try:
            # 包ID应该是0x00
            if packet[0] != 0x00:
                return packet

            # 解析JSON响应
            offset = 1
            json_length, json_length_size = self.decode_varint_from_bytes(packet[offset:])
            offset += json_length_size

            if offset + json_length > len(packet):
                return packet

            json_data = packet[offset:offset+json_length]
            status_response = json.loads(json_data.decode('utf-8'))

            # 修改MOTD
            if self.motd:
                status_response["description"] = {"text": self.motd}

            # 修改favicon
            if self.icon_data:
                status_response["favicon"] = self.icon_data

            # 重新打包
            new_json = json.dumps(status_response, ensure_ascii=True)
            new_json_bytes = new_json.encode('utf-8')
            new_json_length = self.encode_varint(len(new_json_bytes))

            # 构造新包
            new_packet = b"\x00" + new_json_length + new_json_bytes
            return new_packet

        except Exception as e:
            logger.error(f"Error modifying status response: {e}")
            return packet

    def stop(self):
        """停止代理服务器"""
        self.running = False
        if self.server_socket:
            try:
                # 使用 shutdown 来中断任何阻塞的 accept() 调用
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass  # 如果 socket 已经关闭，忽略错误
            self.server_socket.close()