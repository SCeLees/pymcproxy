<template>
  <div class="server-list">
    <div class="dashboard-section">
      <div class="dashboard-header">
        <h2>仪表盘</h2>
        <div class="dashboard-refresh">
          <span class="last-updated">最后更新: {{ lastUpdated }}</span>
        </div>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zM4.5 7.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5z"/>
            </svg>
          </div>
          <div class="stat-content">
            <h3>运行时间</h3>
            <p class="stat-value">{{ formatDuration(appStats.total_runtime) }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2zm13 2.383-4.758 2.855L15 11.114v-5.73zm-.034 6.878L9.271 8.82 8 9.583 6.728 8.82l-5.694 3.44A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.739zM1 11.114l4.758-2.876L1 5.383v5.73z"/>
            </svg>
          </div>
          <div class="stat-content">
            <h3>总连接数</h3>
            <p class="stat-value">{{ appStats.total_connections }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 2a.5.5 0 0 1 .5.5V4a.5.5 0 0 1-1 0V2.5A.5.5 0 0 1 8 2zM3.732 3.732a.5.5 0 0 1 .707 0l.915.914a.5.5 0 1 1-.708.708l-.914-.915a.5.5 0 0 1 0-.707zM2 8a.5.5 0 0 1 .5-.5h1.586a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 8zm9.5 0a.5.5 0 0 1 .5-.5h1.5a.5.5 0 0 1 0 1H12a.5.5 0 0 1-.5-.5zm.754-4.246a.389.389 0 0 0-.527-.02L7.547 7.31A.91.91 0 1 0 8.85 8.569l3.434-4.297a.389.389 0 0 0-.029-.518z"/>
              <path fill-rule="evenodd" d="M6.664 15.889A8 8 0 1 1 9.336.11a8 8 0 0 1-2.672 15.78zm-4.665-4.283A11.945 11.945 0 0 1 8 10c2.186 0 4.236.585 6.001 1.606a7 7 0 1 0-12.002 0z"/>
            </svg>
          </div>
          <div class="stat-content">
            <h3>总流量</h3>
            <p class="stat-value">{{ formatBytes(appStats.total_traffic) }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="player-stats-section" v-if="Object.keys(playerStats).length > 0">
      <h2>玩家统计</h2>
      <div class="player-stats-table-container">
        <div class="table-responsive">
          <table class="player-stats-table">
            <thead>
              <tr>
                <th>玩家ID</th>
                <th>连接次数</th>
                <th>在线时间</th>
                <th>消耗流量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(stats, player) in playerStats" :key="player">
                <td data-label="玩家ID">{{ player }}</td>
                <td data-label="连接次数">{{ stats.total_connections }}</td>
                <td data-label="在线时间">{{ formatDuration(stats.total_time) }}</td>
                <td data-label="消耗流量">{{ formatBytes(stats.total_traffic) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <div class="section-divider"></div>
    
    <div class="servers-section">
      <div class="section-header">
        <h2>服务器管理</h2>
        <button class="add-server-btn" @click="toggleAddForm">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
          </svg>
          {{ showAddForm ? '取消添加' : '添加服务器' }}
        </button>
      </div>
      
      <div class="add-server-form" v-if="showAddForm">
        <div class="form-card">
          <h3>{{ editingServer ? '编辑服务器' : '添加新服务器' }}</h3>
          <form @submit.prevent="saveServer">
            <div class="form-row">
              <div class="form-group">
                <label for="name">服务器名称</label>
                <input type="text" id="name" v-model="currentServer.name" required placeholder="例如: 生存服务器">
              </div>
              
              <div class="form-group">
                <label for="remoteHost">远程主机</label>
                <input type="text" id="remoteHost" v-model="currentServer.remote_host" required placeholder="例如: 192.168.1.100">
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="remotePort">远程端口</label>
                <input type="number" id="remotePort" v-model.number="currentServer.remote_port" required placeholder="例如: 25565">
              </div>
              
              <div class="form-group">
                <label for="localPort">本地端口</label>
                <input type="number" id="localPort" v-model.number="currentServer.local_port" required placeholder="例如: 25566">
              </div>
            </div>
            
            <div class="form-group">
              <label for="motd">MOTD (服务器描述)</label>
              <textarea id="motd" v-model="currentServer.motd" placeholder="例如: 欢迎来到我的Minecraft服务器！"></textarea>
            </div>
            
            <div class="form-group">
              <label for="iconPath">服务器图标路径</label>
              <input type="text" id="iconPath" v-model="currentServer.icon_path" placeholder="例如: server-icon.png">
            </div>
            
            <div class="form-actions">
              <button type="submit" class="submit-btn">{{ editingServer ? '更新服务器' : '添加服务器' }}</button>
              <button type="button" class="cancel-btn" @click="cancelEdit" v-if="editingServer">取消</button>
            </div>
          </form>
        </div>
      </div>
      
      <div class="servers-list">
        <h3>已配置的服务器</h3>
        <div v-if="servers.length === 0" class="no-servers">
          <div class="no-servers-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zM4.5 7.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5z"/>
            </svg>
          </div>
          <p>暂无配置的服务器</p>
          <button class="add-first-server-btn" @click="toggleAddForm">添加第一个服务器</button>
        </div>
        <div v-else class="server-cards">
          <div v-for="server in servers" :key="server.id" class="server-card">
            <div class="server-card-header">
              <h4 class="server-name">{{ server.name }}</h4>
              <div class="server-status" :class="{ 'status-running': server.proxyRunning, 'status-stopped': !server.proxyRunning }">
                <span class="status-indicator"></span>
                {{ server.proxyRunning ? '运行中' : '已停止' }}
              </div>
            </div>
            
            <div class="server-card-body">
              <div class="server-info">
                <div class="info-item">
                  <span class="info-label">远程地址:</span>
                  <span class="info-value">{{ server.remote_host }}:{{ server.remote_port }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">本地端口:</span>
                  <span class="info-value">{{ server.local_port }}</span>
                </div>
                <div class="info-item" v-if="server.motd">
                  <span class="info-label">MOTD:</span>
                  <span class="info-value">{{ server.motd }}</span>
                </div>
                <div class="info-item" v-if="server.icon_path">
                  <span class="info-label">图标路径:</span>
                  <span class="info-value">{{ server.icon_path }}</span>
                </div>
              </div>
            </div>
            
            <div class="server-card-footer">
              <div class="server-actions">
                <button class="action-btn edit-btn" @click="editServer(server)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                  </svg>
                  编辑
                </button>
                <button class="action-btn delete-btn" @click="deleteServer(server.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                    <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                  </svg>
                  删除
                </button>
                <button 
                  class="action-btn toggle-proxy-btn" 
                  :class="{ 'start-btn': !server.proxyRunning, 'stop-btn': server.proxyRunning }"
                  @click="toggleProxy(server)"
                >
                  <svg v-if="!server.proxyRunning" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5 3.5h6A1.5 1.5 0 0 1 12.5 5v6a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 11V5A1.5 1.5 0 0 1 5 3.5z"/>
                  </svg>
                  {{ server.proxyRunning ? '停止代理' : '启动代理' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { getConfig } from '../configLoader.js'

export default {
  name: 'ServerList',
  data() {
    return {
      servers: [],
      currentServer: {
        name: '',
        remote_host: '',
        remote_port: 25565,
        local_port: 25565,
        motd: '',
        icon_path: '',
        autoStart: false
      },
      editingServer: null,
      showAddForm: false
    }
  },
  
  async mounted() {
    await this.refreshAllData()
    // 定期更新统计数据
    this.statsInterval = setInterval(this.fetchStats, 5000)
    // 定期更新服务器状态
    this.serversInterval = setInterval(this.fetchServers, 3000)
  },
  beforeUnmount() {
    // 清除定时器
    if (this.statsInterval) {
      clearInterval(this.statsInterval)
    }
    if (this.serversInterval) {
      clearInterval(this.serversInterval)
    }
  },
  methods: {
    async refreshAllData() {
      await Promise.all([
        this.fetchServers(),
        this.fetchStats()
      ])
      this.lastUpdated = new Date().toLocaleTimeString()
    },
    
    async fetchServers() {
      try {
        const response = await axios.get('http://localhost:5000/api/servers')
        this.servers = response.data
      } catch (error) {
        console.error('获取服务器列表失败:', error)
      }
    },
    
    async fetchStats() {
      try {
        const response = await axios.get('http://localhost:5000/api/stats')
        this.appStats = response.data.app
        this.playerStats = response.data.players
      } catch (error) {
        console.error('获取统计数据失败:', error)
      }
    },
    
    formatDuration(seconds) {
      const hrs = Math.floor(seconds / 3600)
      const mins = Math.floor((seconds % 3600) / 60)
      const secs = Math.floor(seconds % 60)
      
      let result = ''
      if (hrs > 0) result += `${hrs}小时`
      if (mins > 0) result += `${mins}分钟`
      if (secs > 0 || result === '') result += `${secs}秒`
      
      return result
    },
    
    formatBytes(bytes) {
      if (bytes === 0) return '0 Bytes'
      
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    
    toggleAddForm() {
      this.showAddForm = !this.showAddForm
      if (!this.showAddForm) {
        this.resetForm()
      }
    },
    
    async saveServer() {
      try {
        const config = await getConfig();
        if (this.editingServer) {
          // 更新服务器
          const response = await axios.put(`${config.api_base_url}/api/servers/${this.editingServer.id}`, this.currentServer)
          const index = this.servers.findIndex(s => s.id === this.editingServer.id)
          this.servers[index] = response.data
        } else {
          // 添加新服务器
          const response = await axios.post(`${config.api_base_url}/api/servers`, this.currentServer)
          this.servers.push(response.data)
        }
        
        this.resetForm()
        this.showAddForm = false
      } catch (error) {
        console.error('保存服务器失败:', error)
        alert('保存服务器失败: ' + (error.response?.data?.error || error.message))
      }
    },
    
    editServer(server) {
      this.editingServer = server
      this.currentServer = { ...server }
      this.showAddForm = true
    },
    
    cancelEdit() {
      this.resetForm()
    },
    
    async deleteServer(serverId) {
      if (!confirm('确定要删除这个服务器吗？')) return
      
      try {
        const config = await getConfig();
        await axios.delete(`${config.api_base_url}/api/servers/${serverId}`)
        this.servers = this.servers.filter(server => server.id !== serverId)
        this.resetForm()
      } catch (error) {
        console.error('删除服务器失败:', error)
        alert('删除服务器失败: ' + (error.response?.data?.error || error.message))
      }
    },
    
    async toggleProxy(server) {
      try {
        const config = await getConfig();
        if (server.proxyRunning) {
          // 停止代理
          await axios.post(`${config.api_base_url}/api/servers/${server.id}/stop`)
        } else {
          // 启动代理
          await axios.post(`${config.api_base_url}/api/servers/${server.id}/start`)
        }
        
        // 重新加载服务器列表以更新状态
        await this.fetchServers()
      } catch (error) {
        console.error('切换代理状态失败:', error)
        alert('切换代理状态失败: ' + (error.response?.data?.error || error.message))
      }
    },
    
    resetForm() {
      this.currentServer = {
        name: '',
        remote_host: '',
        remote_port: 25565,
        local_port: 25565,
        motd: '',
        icon_path: '',
        autoStart: false
      };
      this.editingServer = null;
      this.showAddForm = false;
    }
  }
}
</script>

<style scoped>
.server-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 仪表盘样式 */
.dashboard-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 25px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.dashboard-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0;
}

.last-updated {
  color: #6c757d;
  font-size: 0.9rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  background: #e3f2fd;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: #2196f3;
}

.stat-content h3 {
  font-size: 1rem;
  color: #6c757d;
  margin: 0 0 5px 0;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: #2c3e50;
}

/* 玩家统计样式 */
.player-stats-section h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.player-stats-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.table-responsive {
  overflow-x: auto;
}

.player-stats-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.player-stats-table thead {
  background: #f1f3f4;
}

.player-stats-table th {
  padding: 15px 20px;
  text-align: left;
  font-weight: 600;
  color: #5f6368;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.player-stats-table td {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  color: #202124;
}

.player-stats-table tbody tr:hover {
  background: #f8f9fa;
}

/* 分隔线 */
.section-divider {
  height: 1px;
  background: #eaeaea;
  margin: 10px 0;
}

/* 服务器管理样式 */
.servers-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 25px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0;
}

.add-server-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #42b983;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s ease;
}

.add-server-btn:hover {
  background: #359c6d;
}

/* 表单样式 */
.add-server-form {
  margin-bottom: 30px;
}

.form-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 25px;
}

.form-card h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #5f6368;
}

.form-group input,
.form-group textarea {
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: inherit;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.submit-btn,
.cancel-btn {
  padding: 12px 25px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.submit-btn {
  background: #42b983;
  color: white;
}

.submit-btn:hover {
  background: #359c6d;
}

.cancel-btn {
  background: #e9ecef;
  color: #495057;
}

.cancel-btn:hover {
  background: #dee2e6;
}

/* 服务器卡片样式 */
.servers-list h3 {
  font-size: 1.25rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.no-servers {
  text-align: center;
  padding: 50px 20px;
  color: #6c757d;
}

.no-servers-icon {
  margin-bottom: 20px;
  color: #ced4da;
}

.no-servers p {
  font-size: 1.1rem;
  margin-bottom: 20px;
}

.add-first-server-btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s ease;
}

.add-first-server-btn:hover {
  background: #359c6d;
}

.server-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}

.server-card {
  border: 1px solid #eaeaea;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s ease;
}

.server-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.server-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #eaeaea;
}

.server-name {
  margin: 0;
  font-size: 1.2rem;
  color: #2c3e50;
}

.server-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.status-running .status-indicator {
  background: #4CAF50;
}

.status-stopped .status-indicator {
  background: #f44336;
}

.status-running {
  color: #4CAF50;
}

.status-stopped {
  color: #f44336;
}

.server-card-body {
  padding: 20px;
}

.server-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.info-label {
  font-weight: 500;
  color: #5f6368;
  min-width: 80px;
}

.info-value {
  color: #202124;
  flex: 1;
}

.server-card-footer {
  padding: 0 20px 20px;
}

.server-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.edit-btn {
  background: #e3f2fd;
  color: #1976d2;
}

.edit-btn:hover {
  background: #bbdefb;
}

.delete-btn {
  background: #ffebee;
  color: #d32f2f;
}

.delete-btn:hover {
  background: #ffcdd2;
}

.toggle-proxy-btn {
  background: #e8f5e9;
  color: #388e3c;
}

.toggle-proxy-btn:hover {
  background: #c8e6c9;
}

.stop-btn {
  background: #ffebee;
  color: #d32f2f;
}

.stop-btn:hover {
  background: #ffcdd2;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-header,
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .server-cards {
    grid-template-columns: 1fr;
  }
  
  .server-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .server-actions {
    width: 100%;
    justify-content: stretch;
  }
  
  .action-btn {
    flex: 1;
    justify-content: center;
  }
  
  .dashboard-section,
  .servers-section {
    padding: 20px 15px;
  }
  
  .form-card {
    padding: 20px 15px;
  }
}
</style>