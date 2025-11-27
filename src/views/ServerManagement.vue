<template>
  <div class="server-management">
    <div class="page-header">
      <h1>服务器管理</h1>
      <button class="add-server-btn" @click="toggleAddForm">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
        </svg>
        {{ showAddForm ? '取消添加' : '添加服务器' }}
      </button>
    </div>
    
    <div class="add-server-form" v-if="showAddForm">
      <div class="form-card">
        <h2>{{ editingServer ? '编辑服务器' : '添加新服务器' }}</h2>
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
          
          <div class="form-group">
            <label for="autoStart">
              <input type="checkbox" id="autoStart" v-model="currentServer.autoStart">
              启动时自动开启代理
            </label>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="submit-btn">{{ editingServer ? '更新服务器' : '添加服务器' }}</button>
            <button type="button" class="cancel-btn" @click="cancelEdit" v-if="editingServer">取消</button>
          </div>
        </form>
      </div>
    </div>
    
    <div class="error-message" v-if="errorMessage">
      {{ errorMessage }}
    </div>
    <div class="servers-controls" v-if="servers.length > 0">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索服务器..." 
          class="search-input"
        >
      </div>
      <div class="items-per-page">
        <label for="itemsPerPage">每页显示:</label>
        <select id="itemsPerPage" v-model="itemsPerPage">
          <option value="5">5</option>
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
        </select>
      </div>
    </div>
    
    <div class="servers-list">
      <h2>已配置的服务器</h2>
      <div v-if="paginatedServers.length === 0" class="no-servers">
        <div class="no-servers-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zM4.5 7.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5z"/>
          </svg>
        </div>
        <p>没有找到匹配的服务器</p>
      </div>
      <div v-else class="server-cards">
        <div v-for="server in paginatedServers" :key="server.id" class="server-card">
          <div class="server-card-header">
            <h3 class="server-name">{{ server.name }}</h3>
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
              <div class="info-item" v-if="server.autoStart">
                <span class="info-label">自动启动:</span>
                <span class="info-value">是</span>
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
      
      <div class="pagination" v-if="totalPages > 1">
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1"
          @click="currentPage = 1"
        >
          首页
        </button>
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          上一页
        </button>
        <span class="pagination-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </span>
        <button 
          class="pagination-btn" 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          下一页
        </button>
        <button 
          class="pagination-btn" 
          :disabled="currentPage === totalPages"
          @click="currentPage = totalPages"
        >
          末页
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { getConfig } from '../configLoader.js'

export default {
  name: 'ServerManagement',
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
      showAddForm: false,
      searchQuery: '',
      currentPage: 1,
      itemsPerPage: 10,
      errorMessage: ''
    }
  },
  computed: {
    filteredServers() {
      const query = this.searchQuery.toLowerCase()
      return this.servers.filter(server => 
        server.name.toLowerCase().includes(query) ||
        server.remote_host.toLowerCase().includes(query)
      )
    },
    
    paginatedServers() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredServers.slice(start, end)
    },
    
    totalPages() {
      return Math.ceil(this.filteredServers.length / this.itemsPerPage)
    }
  },
  watch: {
    searchQuery() {
      this.currentPage = 1
    },
    itemsPerPage() {
      this.currentPage = 1
    }
  },
  async mounted() {
    await this.loadServers()
    // 降低服务器状态更新频率以优化性能
    this.serversInterval = setInterval(this.loadServers, 5000)
  },
  beforeUnmount() {
    if (this.serversInterval) {
      clearInterval(this.serversInterval)
    }
  },
  methods: {
    async loadServers() {
      try {
        const config = await getConfig();
        const response = await axios.get(`${config.api_base_url}/api/servers`)
        this.servers = response.data
        this.calculateTotalPages()
      } catch (error) {
        console.error('获取服务器列表失败:', error)
      }
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
        this.calculateTotalPages()
      } catch (error) {
        console.error('保存服务器失败:', error)
        const errorMsg = error.response?.data?.error || error.message || '未知错误'
        this.errorMessage = `保存服务器失败: ${errorMsg}`
        alert(`保存服务器失败: ${errorMsg}`)
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
        this.calculateTotalPages()
      } catch (error) {
        console.error('删除服务器失败:', error)
        const errorMsg = error.response?.data?.error || error.message || '未知错误'
        this.errorMessage = `删除服务器失败: ${errorMsg}`
        alert(`删除服务器失败: ${errorMsg}`)
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
        await this.loadServers()
      } catch (error) {
        console.error('切换代理状态失败:', error)
        const errorMsg = error.response?.data?.error || error.message || '未知错误'
        this.errorMessage = `切换代理状态失败: ${errorMsg}`
        alert(`切换代理状态失败: ${errorMsg}`)
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
    },
    
    calculateTotalPages() {
      // 确保当前页码在有效范围内
      const total = Math.ceil(this.filteredServers.length / this.itemsPerPage);
      if (this.currentPage > total && total > 0) {
        this.currentPage = total;
      } else if (total === 0) {
        this.currentPage = 1;
      }
    }
  }
}
</script>

<style scoped>
.server-management {
  padding: 24px 0;
  width: 100%;
  color: #e2e8f0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  gap: 16px;
  flex-wrap: wrap;
}

.page-header h1 {
  font-size: 2rem;
  margin: 0;
}

.add-server-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #3dd598, #0ea371);
  color: #0f172a;
  border: none;
  padding: 12px 22px;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 12px 30px rgba(61, 213, 152, 0.35);
}

.add-server-btn:hover {
  transform: translateY(-1px);
}

.add-server-form {
  margin-bottom: 32px;
}

.form-card {
  background: var(--color-surface);
  border-radius: 20px;
  border: 1px solid var(--color-border);
  padding: 28px;
  box-shadow: var(--shadow-soft);
}

.form-card h2 {
  margin: 0 0 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: var(--color-muted);
}

.form-group input,
.form-group textarea {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid var(--color-border);
  background: rgba(15, 23, 42, 0.4);
  color: inherit;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.form-group input[type="checkbox"] {
  width: auto;
  accent-color: #3dd598;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: rgba(61, 213, 152, 0.6);
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.submit-btn,
.cancel-btn {
  padding: 12px 22px;
  border-radius: 999px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s ease;
}

.submit-btn {
  background: linear-gradient(135deg, #3dd598, #0ea371);
  color: #0f172a;
  box-shadow: 0 10px 24px rgba(61, 213, 152, 0.35);
}

.submit-btn:hover {
  transform: translateY(-1px);
}

.cancel-btn {
  background: transparent;
  color: var(--color-muted);
  border-color: var(--color-border);
}

.servers-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.search-box {
  flex: 1;
  min-width: 240px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: rgba(15, 23, 42, 0.4);
  color: inherit;
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-muted);
}

.items-per-page select {
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: inherit;
}

.servers-list h2 {
  font-size: 1.4rem;
  margin-bottom: 20px;
}

.error-message {
  background: rgba(248, 113, 113, 0.15);
  border: 1px solid rgba(248, 113, 113, 0.4);
  color: #fecaca;
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 16px;
}

.server-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.server-card {
  background: var(--color-surface);
  border-radius: 20px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
}

.server-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px;
  border-bottom: 1px solid var(--color-border);
}

.server-name {
  margin: 0;
  font-size: 1.2rem;
}

.server-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-running {
  color: #3dd598;
}

.status-running .status-indicator {
  background: #3dd598;
  box-shadow: 0 0 10px rgba(61, 213, 152, 0.8);
}

.status-stopped {
  color: #f87171;
}

.status-stopped .status-indicator {
  background: #f87171;
}

.server-card-body {
  padding: 22px;
}

.server-info {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.info-item {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: var(--color-muted);
}

.info-label {
  min-width: 90px;
  color: rgba(248, 250, 252, 0.75);
  font-weight: 600;
}

.info-value {
  color: #f8fafc;
  flex: 1;
}

.server-card-footer {
  padding: 0 22px 22px;
}

.server-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.action-btn {
  flex: 1;
  min-width: 140px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
  color: inherit;
  transition: border-color 0.2s ease;
}

.edit-btn {
  border-color: rgba(59, 130, 246, 0.4);
  color: #93c5fd;
}

.delete-btn {
  border-color: rgba(248, 113, 113, 0.4);
  color: #fecaca;
}

.toggle-proxy-btn {
  border-color: rgba(61, 213, 152, 0.4);
  color: #6ee7b7;
}

.stop-btn {
  border-color: rgba(248, 113, 113, 0.4);
  color: #fecaca;
}

.action-btn:hover {
  border-color: rgba(255, 255, 255, 0.7);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 18px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: rgba(15, 23, 42, 0.7);
  box-shadow: var(--shadow-soft);
  flex-wrap: wrap;
}

.pagination-btn {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.pagination-btn:hover:not(:disabled) {
  border-color: rgba(61, 213, 152, 0.6);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-info {
  color: var(--color-muted);
  font-size: 0.9rem;
}

@media (max-width: 900px) {
  .server-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-card,
  .server-card {
    padding: 20px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .servers-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    min-width: unset;
  }

  .server-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .pagination {
    border-radius: 18px;
  }
}
</style>