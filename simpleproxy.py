import socket
import threading
import json

class SimpleMinecraftProxy:
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
            
            # 创建两个线程来双向转发数据
            client_to_server = threading.Thread(
                target=self.forward_data, 
                args=(client_socket, remote_socket, True)
            )
            server_to_client = threading.Thread(
                target=self.forward_data, 
                args=(remote_socket, client_socket, False)
            )
            
            client_to_server.daemon = True
            server_to_client.daemon = True
            
            client_to_server.start()
            server_to_client.start()
            
            # 等待线程结束
            client_to_server.join()
            server_to_client.join()

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

    def forward_data(self, source, destination, is_client_to_server):
        """在两个socket之间转发数据"""
        try:
            while self.running:
                # 读取数据
                data = source.recv(4096)
                if not data:
                    break
                    
                # 如果是客户端到服务器的数据流且是状态请求阶段的第一个包
                if is_client_to_server and len(data) >= 2 and data[1] == 0x00:
                    # 检查是否是状态请求 (0x00 0x00)
                    if len(data) >= 2 and data[0] == 0x01 and data[1] == 0x00:
                        # 这是状态请求，我们需要拦截并修改响应
                        # 但为了简化，我们仍然转发，只是记录
                        print("Status request detected")
                
                # 转发数据
                destination.sendall(data)
                
        except Exception as e:
            if self.running:
                print(f"Error forwarding data: {e}")
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