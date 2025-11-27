# PyMCProxy

一个功能丰富的 Minecraft 服务器代理工具，支持多服务器管理、状态监控和高级代理功能。

## Demo 演示

视频：施工中🚧

演示站点：施工中🚧


## 功能特性

- **多服务器管理**：支持同时管理多个 Minecraft 服务器
- **实时状态监控**：提供服务器连接数、流量、在线玩家等统计数据
- **代理功能**：支持端口转发、MOTD 自定义、服务器图标设置
- **黑白名单系统**：支持按玩家名称控制访问权限
- **Web 管理界面**：直观的前端界面，便于操作和监控
- **详细日志记录**：记录所有连接、玩家活动和系统操作

## 技术架构

- **后端**：Python Flask API
- **前端**：Vue.js 管理界面
- **代理核心**：基于 Socket 的 Minecraft 协议转发

## 使用方法

### 环境要求

- Python 3.7+
- Node.js 14+

### 启动后端

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动后端服务器：
```bash
python app.py
```

服务器默认运行在 `http://localhost:5000`

### 启动前端

1. 安装前端依赖：
```bash
npm install
```

2. 启动前端开发服务器：
```bash
npm run dev
```

### 配置文件

- `config/servers.json`：服务器配置
- `config/config.json`：系统配置
- `config/whitelist_blacklist.json`：黑白名单配置
- `logs/`：日志文件目录

## 主要功能

### 服务器管理
- 添加/编辑/删除 Minecraft 服务器
- 启动/停止代理服务
- 自定义 MOTD 和服务器图标
- 设置自动启动选项

### 监控功能
- 实时显示服务器运行状态
- 统计连接数、流量、在线时间
- 玩家活动记录与统计

### 访问控制
- 黑白名单系统
- 支持按玩家名称控制访问权限

## API 接口

- `GET /api/servers` - 获取服务器列表
- `POST /api/servers` - 添加服务器
- `PUT /api/servers/{id}` - 更新服务器
- `DELETE /api/servers/{id}` - 删除服务器
- `POST /api/servers/{id}/start` - 启动代理
- `POST /api/servers/{id}/stop` - 停止代理
- `GET /api/stats` - 获取统计数据

## 日志系统

系统会自动创建日志文件，按日期命名，保存在 `logs/` 目录下。日志包含：

- 服务器启动/停止记录
- 玩家连接/断开记录
- API 调用记录
- 错误和警告信息

## 文件结构

```
PyMinecraftServerProxy/
├── app.py              # 主后端服务器
├── enhancedproxy.py    # 代理核心实现
├── logger.py           # 日志系统
├── stats.py            # 统计功能
├── config/             # 配置文件
│   ├── servers.json
│   ├── config.json
│   └── whitelist_blacklist.json
├── logs/               # 日志文件
├── src/                # 前端源码
└── requirements.txt    # Python 依赖
```

## TODO

- [ ] 前端添加账户密码登录，身份验证
- [ ] 后端 API 加密功能
- [施工中🚧] 自定义主题，亮色主题
- [ ] 数据导出功能 - 将统计数据导出为 Excel 或 CSV 格式
- [ ] 多语言支持
- [ ] 服务器配置备份与恢复功能

## 许可证

此项目仅供学习和参考使用。