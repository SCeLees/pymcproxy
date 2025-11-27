from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import threading
from enhancedproxy import EnhancedMinecraftProxy as MinecraftProxy
from logger import get_logger
from stats import stats_manager

# 获取logger实例
logger = get_logger()

app = Flask(__name__)
CORS(app)

# 数据存储文件
SERVERS_FILE = 'config/servers.json'
CONFIG_FILE = 'config/config.json'

# 初始化服务器数据文件
def init_servers_file():
    if not os.path.exists(SERVERS_FILE):
        with open(SERVERS_FILE, 'w') as f:
            json.dump([], f)

# 读取配置文件
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        # 默认配置
        return {
            "backend": {
                "host": "0.0.0.0",
                "port": 5000
            },
            "frontend": {
                "api_base_url": "http://localhost:5000"
            }
        }

# 读取服务器列表
def load_servers():
    init_servers_file()
    with open(SERVERS_FILE, 'r') as f:
        return json.load(f)

# 保存服务器列表
def save_servers(servers):
    with open(SERVERS_FILE, 'w') as f:
        json.dump(servers, f, indent=2)

# 获取服务器列表
@app.route('/api/servers', methods=['GET'])
def get_servers():
    servers = load_servers()
    # 添加代理运行状态
    for server in servers:
        server_id = server['id']
        server['proxyRunning'] = server_id in proxies and proxies[server_id].running
    return jsonify(servers)

# 添加新服务器
@app.route('/api/servers', methods=['POST'])
def add_server():
    servers = load_servers()
    new_server = request.json
    
    # 验证必要字段
    if not new_server.get('name') or not new_server.get('remote_host') or not new_server.get('remote_port'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 分配ID
    new_server['id'] = len(servers) + 1
    new_server['local_port'] = new_server.get('local_port', 25565)
    
    servers.append(new_server)
    save_servers(servers)
    
    logger.info(f"Added new server: {new_server['name']} (ID: {new_server['id']})")
    
    # 添加代理运行状态
    new_server['proxyRunning'] = False
    
    return jsonify(new_server), 201

# 更新服务器
@app.route('/api/servers/<int:server_id>', methods=['PUT'])
def update_server(server_id):
    servers = load_servers()
    updated_server = request.json
    
    # 查找服务器
    for i, server in enumerate(servers):
        if server['id'] == server_id:
            # 检查代理是否正在运行
            was_running = server_id in proxies and proxies[server_id].running
            
            # 记录变更
            old_config = dict(servers[i])
            servers[i].update(updated_server)
            save_servers(servers)
            
            # 记录更新日志
            logger.info(f"Updated server {server_id}: {old_config} -> {servers[i]}")
            
            # 如果代理正在运行，重启它以应用新配置
            if was_running:
                start_proxy(server_id)
                logger.info(f"Restarted proxy for server {server_id} to apply updates")
            
            # 添加代理运行状态
            servers[i]['proxyRunning'] = was_running
            
            return jsonify(servers[i])
    
    return jsonify({'error': 'Server not found'}), 404

# 删除服务器
@app.route('/api/servers/<int:server_id>', methods=['DELETE'])
def delete_server(server_id):
    servers = load_servers()
    
    # 查找服务器
    for i, server in enumerate(servers):
        if server['id'] == server_id:
            server_name = server['name']
            del servers[i]
            save_servers(servers)
            logger.info(f"Deleted server: {server_name} (ID: {server_id})")
            return '', 204
    
    return jsonify({'error': 'Server not found'}), 404

# 获取统计数据
@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(stats_manager.get_stats())

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
                icon_path=server.get('icon_path', ''),
                server_id=server_id,  # 传递服务器ID
                server_name=server.get('name', 'Unknown')  # 传递服务器名称
            )
            
            proxies[server_id] = proxy
            
            # 在新线程中启动代理
            proxy_thread = threading.Thread(target=proxy.start)
            proxy_thread.daemon = True
            proxy_thread.start()
            
            logger.info(f"[{server['name']}] Proxy started on port {server.get('local_port', 25565)}")
            
            return True
    
    logger.warning(f"Server with ID {server_id} not found")
    return False

def stop_proxy(server_id):
    """停止指定ID的代理"""
    if server_id in proxies:
        # 获取服务器名称用于日志
        proxy_instance = proxies[server_id]
        server_name = getattr(proxy_instance, 'server_name', 'Unknown')
        proxies[server_id].stop()
        del proxies[server_id]
        logger.info(f"[{server_name}] Proxy stopped")
        return True
    else:
        logger.warning(f"No proxy running for server {server_id}")
    return False

def stop_all_proxies():
    """停止所有代理"""
    for server_id in list(proxies.keys()):
        stop_proxy(server_id)
    if len(proxies) > 0:
        logger.info("Stopped all proxies")

# 启动代理
@app.route('/api/servers/<int:server_id>/start', methods=['POST'])
def start_proxy_route(server_id):
    servers = load_servers()
    server_name = "Unknown"
    for server in servers:
        if server['id'] == server_id:
            server_name = server.get('name', 'Unknown')
            break
    
    logger.info(f"[{server_name}] Starting proxy (API)")
    try:
        if start_proxy(server_id):
            logger.info(f"[{server_name}] Proxy started successfully (API)")
            return jsonify({'message': f'Proxy started for server {server_id}'})
        else:
            logger.warning(f"[{server_name}] Failed to start: Server not found (API)")
            return jsonify({'error': 'Server not found'}), 404
    except Exception as e:
        logger.error(f"[{server_name}] Error starting proxy: {e} (API)")
        return jsonify({'error': str(e)}), 500

# 停止代理
@app.route('/api/servers/<int:server_id>/stop', methods=['POST'])
def stop_proxy_route(server_id):
    servers = load_servers()
    server_name = "Unknown"
    for server in servers:
        if server['id'] == server_id:
            server_name = server.get('name', 'Unknown')
            break
    
    logger.info(f"[{server_name}] Stopping proxy (API)")
    try:
        if stop_proxy(server_id):
            logger.info(f"[{server_name}] Proxy stopped successfully (API)")
            return jsonify({'message': f'Proxy stopped for server {server_id}'})
        else:
            logger.warning(f"[{server_name}] Failed to stop: Proxy not running (API)")
            return jsonify({'error': 'Proxy not running for this server'}), 404
    except Exception as e:
        logger.error(f"[{server_name}] Error stopping proxy: {e} (API)")
        return jsonify({'error': str(e)}), 500

# 在文件顶部导入之后添加
WHITELIST_BLACKLIST_FILE = 'config/whitelist_blacklist.json'

# 添加新的函数用于处理黑白名单配置
def init_whitelist_blacklist_file():
    """初始化黑白名单配置文件"""
    if not os.path.exists(WHITELIST_BLACKLIST_FILE):
        # 创建一个空的配置文件
        with open(WHITELIST_BLACKLIST_FILE, 'w') as f:
            json.dump({}, f)

def load_whitelist_blacklist_config():
    """加载黑白名单配置"""
    init_whitelist_blacklist_file()
    with open(WHITELIST_BLACKLIST_FILE, 'r') as f:
        return json.load(f)

def save_whitelist_blacklist_config(config):
    """保存黑白名单配置"""
    with open(WHITELIST_BLACKLIST_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# 在文件末尾添加新的API端点，但在 if __name__ == '__main__': 之前

# 获取指定服务器的黑白名单配置
@app.route('/api/servers/<int:server_id>/whitelist-blacklist', methods=['GET'])
def get_server_whitelist_blacklist(server_id):
    config = load_whitelist_blacklist_config()
    server_config = config.get(str(server_id), {
        'mode': 'none',
        'players': []
    })
    return jsonify(server_config)

# 更新指定服务器的黑白名单配置
@app.route('/api/servers/<int:server_id>/whitelist-blacklist', methods=['PUT'])
def update_server_whitelist_blacklist(server_id):
    config = load_whitelist_blacklist_config()
    updated_config = request.json
    
    # 验证输入
    if 'mode' not in updated_config or 'players' not in updated_config:
        return jsonify({'error': 'Missing required fields: mode and players'}), 400
    
    if updated_config['mode'] not in ['none', 'whitelist', 'blacklist']:
        return jsonify({'error': 'Invalid mode. Must be one of: none, whitelist, blacklist'}), 400
    
    # 更新配置
    config[str(server_id)] = {
        'mode': updated_config['mode'],
        'players': updated_config['players']
    }
    
    save_whitelist_blacklist_config(config)
    logger.info(f"Updated whitelist/blacklist config for server {server_id}")
    
    return jsonify(config[str(server_id)])

# 获取配置信息
@app.route('/api/config', methods=['GET'])
def get_config():
    config = load_config()
    # 只返回前端需要的部分
    return jsonify(config.get('frontend', {}))

if __name__ == '__main__':
    try:
        # 加载配置
        config = load_config()
        backend_config = config.get('backend', {})
        host = backend_config.get('host', '0.0.0.0')
        port = backend_config.get('port', 5000)
        
        stats_manager.reset_app_start_time()  # 重置启动时间
        logger.info("Starting Minecraft Proxy Manager")
        
        # 启动时自动启动标记为运行的代理
        servers = load_servers()
        for server in servers:
            if server.get('autoStart', False):
                start_proxy(server['id'])
                logger.info(f"Auto-started proxy for server '{server['name']}'")
        
        app.run(host=host, port=port, debug=False)
    finally:
        # 停止所有代理
        stop_all_proxies()
        logger.info("Minecraft Proxy Manager shutdown")