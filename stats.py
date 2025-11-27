import json
import os
import threading
from datetime import datetime
from logger import get_logger

logger = get_logger()

class StatsManager:
    def __init__(self, stats_file='config/stats.json'):
        self.stats_file = stats_file
        self.lock = threading.Lock()
        self.stats = self.load_stats()
        
    def load_stats(self):
        """加载统计数据"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading stats: {e}")
                return self.get_default_stats()
        else:
            return self.get_default_stats()
            
    def get_default_stats(self):
        """获取默认统计数据"""
        return {
            "app": {
                "start_time": datetime.now().isoformat(),
                "total_runtime": 0,  # 总运行时间(秒)
                "total_connections": 0,  # 总连接数
                "total_traffic": 0  # 总流量(字节)
            },
            "players": {}  # 玩家统计数据
        }
        
    def save_stats(self):
        """保存统计数据"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
            
    def update_app_stats(self, connections=0, traffic=0):
        """更新应用统计数据"""
        with self.lock:
            self.stats["app"]["total_connections"] += connections
            self.stats["app"]["total_traffic"] += traffic
            self.save_stats()
            
    def update_player_stats(self, player_name, traffic=0, connection_time=0):
        """更新玩家统计数据"""
        with self.lock:
            if player_name not in self.stats["players"]:
                self.stats["players"][player_name] = {
                    "total_connections": 0,
                    "total_traffic": 0,
                    "total_time": 0
                }
                
            self.stats["players"][player_name]["total_connections"] += 1
            self.stats["players"][player_name]["total_traffic"] += traffic
            self.stats["players"][player_name]["total_time"] += connection_time
            self.save_stats()
            
    def get_stats(self):
        """获取统计数据"""
        with self.lock:
            # 更新总运行时间
            start_time = datetime.fromisoformat(self.stats["app"]["start_time"])
            self.stats["app"]["total_runtime"] = (datetime.now() - start_time).total_seconds()
            return dict(self.stats)
            
    def reset_app_start_time(self):
        """重置应用启动时间"""
        with self.lock:
            self.stats["app"]["start_time"] = datetime.now().isoformat()
            self.save_stats()

# 创建全局统计管理器实例
stats_manager = StatsManager()