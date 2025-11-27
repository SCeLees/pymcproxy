<template>
  <div class="whitelist-blacklist">
    <div class="page-header">
      <h1>黑白名单管理</h1>
      <p class="page-description">记得保存喵 ~</p>
    </div>

    <div class="server-selector" v-if="servers.length > 0">
      <label for="serverSelect">选择服务器:</label>
      <select id="serverSelect" v-model="selectedServerId" @change="loadServerWhitelistBlacklist">
        <option v-for="server in servers" :key="server.id" :value="server.id">
          {{ server.name }} ({{ server.proxyRunning ? '运行中' : '已停止' }})
        </option>
      </select>
    </div>

    <div class="no-servers-message" v-else>
      <p>暂无服务器配置，请先添加服务器。</p>
    </div>

    <div class="whitelist-blacklist-config" v-if="selectedServer && servers.length > 0">
      <div class="config-card">
        <div class="card-header">
          <h2>{{ selectedServer.name }} - 黑白名单配置</h2>
        </div>

        <div class="card-body">
          <div class="mode-selection">
            <h3>名单模式</h3>
            <div class="radio-group">
              <label class="radio-option">
                <input 
                  type="radio" 
                  v-model="serverConfig.mode" 
                  value="none" 
                  @change="updateMode"
                >
                <span class="radio-label">无限制</span>
              </label>
              
              <label class="radio-option">
                <input 
                  type="radio" 
                  v-model="serverConfig.mode" 
                  value="whitelist" 
                  @change="updateMode"
                >
                <span class="radio-label">白名单模式</span>
              </label>
              
              <label class="radio-option">
                <input 
                  type="radio" 
                  v-model="serverConfig.mode" 
                  value="blacklist" 
                  @change="updateMode"
                >
                <span class="radio-label">黑名单模式</span>
              </label>
            </div>
          </div>

          <div class="player-list-section" v-if="serverConfig.mode !== 'none'">
            <h3>{{ serverConfig.mode === 'whitelist' ? '白名单' : '黑名单' }}玩家列表</h3>
            
            <div class="add-player-form">
              <div class="form-row">
                <input 
                  type="text" 
                  v-model="newPlayerName" 
                  placeholder="输入玩家ID"
                  @keyup.enter="addPlayer"
                >
                <button @click="addPlayer" class="add-player-btn">添加玩家</button>
                <input 
                  type="file" 
                  ref="fileInput" 
                  @change="handleFileImport" 
                  accept=".txt"
                  class="file-input"
                >
                <button @click="$refs.fileInput.click()" class="import-file-btn">从文件导入</button>
              </div>
              
              <div class="form-row kick-player-row">
                <input 
                  type="text" 
                  v-model="kickPlayerName" 
                  placeholder="输入要踢出的玩家ID"
                  @keyup.enter="kickPlayer"
                >
                <button @click="kickPlayer" class="kick-player-btn">踢出玩家</button>
                <input 
                  type="file" 
                  ref="kickFileInput" 
                  @change="handleKickFileImport" 
                  accept=".txt"
                  class="file-input"
                >
                <button @click="$refs.kickFileInput.click()" class="kick-file-btn">从文件踢出</button>
              </div>
            </div>

            <div class="player-list-controls" v-if="serverConfig.players.length > 10">
              <div class="items-per-page">
                <label for="itemsPerPage">每页显示:</label>
                <select id="itemsPerPage" v-model="itemsPerPage">
                  <option value="10">10</option>
                  <option value="25">25</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                </select>
              </div>
              <div class="pagination-controls">
                <button 
                  @click="currentPage--" 
                  :disabled="currentPage === 1"
                  class="pagination-btn"
                >
                  上一页
                </button>
                <span class="pagination-info">
                  第 {{ currentPage }} 页，共 {{ totalPages }} 页 (总计 {{ serverConfig.players.length }} 个玩家)
                </span>
                <button 
                  @click="currentPage++" 
                  :disabled="currentPage === totalPages"
                  class="pagination-btn"
                >
                  下一页
                </button>
              </div>
            </div>

            <div class="player-search-sort">
              <div class="search-box">
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="搜索玩家..." 
                  class="search-input"
                >
              </div>
              <div class="sort-controls">
                <button @click="sortPlayers" class="sort-btn">
                  <span v-if="sortOrder === 'default'">默认排序</span>
                  <span v-else-if="sortOrder === 'asc'">升序排列</span>
                  <span v-else>降序排列</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path v-if="sortOrder === 'default'" d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
                    <path v-else-if="sortOrder === 'asc'" d="M8 4a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-1 0v-9A.5.5 0 0 1 8 4zm3 3a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V7.5A.5.5 0 0 1 11 7z"/>
                    <path v-else d="M8 12a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 1 0v9a.5.5 0 0 1-.5.5zm-3-3a.5.5 0 0 1-.5-.5v-3a.5.5 0 0 1 1 0v3a.5.5 0 0 1-.5.5z"/>
                  </svg>
                </button>
              </div>
            </div>

            <div class="player-list">
              <div 
                v-for="(player, index) in displayedPlayers" 
                :key="getPlayerKey(player, index)" 
                class="player-item"
              >
                <span class="player-name">{{ player }}</span>
                <button @click="removePlayer(getActualIndex(index))" class="remove-player-btn">移除</button>
              </div>
              
              <div v-if="filteredPlayers.length === 0" class="no-players">
                <p v-if="searchQuery">未找到匹配的玩家</p>
                <p v-else>暂无玩家在{{ serverConfig.mode === 'whitelist' ? '白名单' : '黑名单' }}中</p>
              </div>
            </div>
            
            <div class="player-list-controls bottom-controls" v-if="serverConfig.players.length > 10">
              <div class="pagination-controls">
                <button 
                  @click="currentPage--" 
                  :disabled="currentPage === 1"
                  class="pagination-btn"
                >
                  上一页
                </button>
                <span class="pagination-info">
                  第 {{ currentPage }} 页，共 {{ totalPages }} 页 (总计 {{ serverConfig.players.length }} 个玩家)
                </span>
                <button 
                  @click="currentPage++" 
                  :disabled="currentPage === totalPages"
                  class="pagination-btn"
                >
                  下一页
                </button>
              </div>
            </div>
          </div>

          <div class="config-actions">
            <button @click="saveConfig" class="save-btn">保存配置</button>
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
  name: 'WhitelistBlacklist',
  data() {
    return {
      servers: [],
      selectedServerId: null,
      selectedServer: null,
      serverConfig: {
        mode: 'none',
        players: []
      },
      searchQuery: '',
      sortOrder: 'default',
      currentPage: 1,
      itemsPerPage: 10,
      kickFileName: ''
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.filteredPlayers.length / this.itemsPerPage)
    },
    
    filteredPlayers() {
      // 根据搜索查询过滤玩家
      if (!this.searchQuery) {
        return this.serverConfig.players
      }
      
      const query = this.searchQuery.toLowerCase()
      return this.serverConfig.players.filter(player => 
        player.toLowerCase().includes(query)
      )
    },
    
    sortedPlayers() {
      // 根据排序顺序排序玩家
      let players = [...this.filteredPlayers]
      
      if (this.sortOrder === 'asc') {
        players.sort()
      } else if (this.sortOrder === 'desc') {
        players.sort().reverse()
      }
      // 如果是默认顺序，则不排序
      
      return players
    },
    
    displayedPlayers() {
      const startIndex = (this.currentPage - 1) * this.itemsPerPage
      const endIndex = startIndex + this.itemsPerPage
      return this.sortedPlayers.slice(startIndex, endIndex)
    }
  },
  watch: {
    searchQuery() {
      // 搜索查询改变时重置到第一页
      this.currentPage = 1
    }
  },
  async mounted() {
    await this.loadServers()
    if (this.servers.length > 0) {
      this.selectedServerId = this.servers[0].id
      this.selectedServer = this.servers[0]
      await this.loadServerWhitelistBlacklist()
    }
  },
  methods: {
    async loadServers() {
      try {
        const config = await getConfig();
        const response = await axios.get(`${config.api_base_url}/api/servers`)
        this.servers = response.data
      } catch (error) {
        console.error('获取服务器列表失败:', error)
      }
    },

    async loadServerWhitelistBlacklist() {
      if (!this.selectedServerId) return
      
      try {
        const config = await getConfig();
        const response = await axios.get(`${config.api_base_url}/api/servers/${this.selectedServerId}/whitelist-blacklist`)
        this.serverConfig = response.data
        this.selectedServer = this.servers.find(s => s.id === this.selectedServerId)
        // 重置分页和其他状态
        this.currentPage = 1
        this.searchQuery = ''
        this.sortOrder = 'default'
      } catch (error) {
        console.error('获取黑白名单配置失败:', error)
        // 使用默认配置
        this.serverConfig = {
          mode: 'none',
          players: []
        }
      }
    },

    updateMode() {
      // 当模式改变时的处理逻辑
      // 重置分页
      this.currentPage = 1
    },

    getPlayerKey(player, index) {
      // 为每个玩家项生成唯一key
      return `${player}-${index}`
    },

    getActualIndex(index) {
      // 获取实际在玩家列表中的索引
      return this.sortedPlayers.indexOf(this.displayedPlayers[index])
    },

    addPlayer() {
      if (this.newPlayerName.trim() !== '') {
        const playerName = this.newPlayerName.trim()
        if (this.serverConfig.players.includes(playerName)) {
          alert(`玩家 ${playerName} 已经在名单中`)
          return
        }
        
        this.serverConfig.players.push(playerName)
        this.newPlayerName = ''
        // 如果添加后超出当前页，则跳转到最后一页
        if (this.filteredPlayers.length > this.currentPage * this.itemsPerPage) {
          this.currentPage = this.totalPages
        }
      }
    },

    removePlayer(index) {
      this.serverConfig.players.splice(index, 1)
      // 如果当前页变为空且不是第一页，则跳转到前一页
      if (this.displayedPlayers.length === 0 && this.currentPage > 1) {
        this.currentPage = Math.min(this.currentPage - 1, this.totalPages)
      }
    },

    kickPlayer() {
      if (this.kickPlayerName.trim() !== '') {
        const playerName = this.kickPlayerName.trim()
        const index = this.serverConfig.players.indexOf(playerName)
        
        if (index !== -1) {
          this.serverConfig.players.splice(index, 1)
          alert(`玩家 ${playerName} 已从名单中移除`)
          this.kickPlayerName = ''
          
          // 如果当前页变为空且不是第一页，则跳转到前一页
          if (this.displayedPlayers.length === 0 && this.currentPage > 1) {
            this.currentPage = Math.min(this.currentPage - 1, this.totalPages)
          }
        } else {
          alert(`未找到玩家 ${playerName}`)
        }
      }
    },

    sortPlayers() {
      // 循环切换排序顺序
      if (this.sortOrder === 'default') {
        this.sortOrder = 'asc'
      } else if (this.sortOrder === 'asc') {
        this.sortOrder = 'desc'
      } else {
        this.sortOrder = 'default'
      }
      // 重置到第一页
      this.currentPage = 1
    },

    handleFileImport(event) {
      const file = event.target.files[0]
      if (!file) return

      this.importFileName = file.name
      
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target.result
        const lines = content.split(/\r?\n/)
        let addedCount = 0
        let duplicateCount = 0
        
        lines.forEach(line => {
          const playerName = line.trim()
          if (playerName) {
            if (!this.serverConfig.players.includes(playerName)) {
              this.serverConfig.players.push(playerName)
              addedCount++
            } else {
              duplicateCount++
            }
          }
        })
        
        let message = `成功从文件导入 ${addedCount} 个玩家`
        if (duplicateCount > 0) {
          message += `，${duplicateCount} 个玩家已在名单中`
        }
        alert(message)
        
        // 重置文件输入
        event.target.value = ''
        this.importFileName = ''
        // 跳转到最后一页以查看新添加的玩家
        this.currentPage = this.totalPages
      }
      
      reader.readAsText(file)
    },

    handleKickFileImport(event) {
      const file = event.target.files[0]
      if (!file) return

      this.kickFileName = file.name
      
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target.result
        const lines = content.split(/\r?\n/)
        let kickedCount = 0
        let notFoundCount = 0
        
        lines.forEach(line => {
          const playerName = line.trim()
          if (playerName) {
            const index = this.serverConfig.players.indexOf(playerName)
            if (index !== -1) {
              this.serverConfig.players.splice(index, 1)
              kickedCount++
            } else {
              notFoundCount++
            }
          }
        })
        
        let message = `成功踢出 ${kickedCount} 个玩家`
        if (notFoundCount > 0) {
          message += `，${notFoundCount} 个玩家未在名单中找到`
        }
        alert(message)
        
        // 重置文件输入
        event.target.value = ''
        this.kickFileName = ''
        // 重新计算页数
        this.currentPage = Math.min(this.currentPage, this.totalPages)
      }
      
      reader.readAsText(file)
    },

    async saveConfig() {
      try {
        const config = await getConfig();
        await axios.put(
          `${config.api_base_url}/api/servers/${this.selectedServerId}/whitelist-blacklist`,
          this.serverConfig
        )
        alert('配置已保存')
      } catch (error) {
        console.error('保存配置失败:', error)
        alert('保存配置失败: ' + (error.response?.data?.error || error.message))
      }
    }
  }
}
</script>

<style scoped>
.whitelist-blacklist {
  padding: 24px 0;
  width: 100%;
  color: #e2e8f0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 2rem;
  margin: 0 0 8px;
}

.page-description {
  color: var(--color-muted);
  margin: 0;
}

.server-selector,
.no-servers-message,
.config-card {
  background: var(--color-surface);
  border-radius: 20px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-soft);
  padding: 24px;
  margin-bottom: 24px;
}

.server-selector {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.server-selector label {
  font-weight: 600;
  color: #f8fafc;
}

.server-selector select {
  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid var(--color-border);
  background: rgba(15, 23, 42, 0.45);
  color: inherit;
  min-width: 220px;
}

.no-servers-message {
  text-align: center;
  color: var(--color-muted);
}

.card-header h2 {
  margin: 0 0 4px;
}

.card-body {
  padding-top: 16px;
}

.mode-selection {
  margin-bottom: 28px;
  padding: 18px;
  border-radius: 16px;
  border: 1px dashed rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.4);
}

.mode-selection h3 {
  margin: 0 0 14px;
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.radio-option {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.03);
  cursor: pointer;
}

.radio-option input[type="radio"] {
  accent-color: var(--color-accent);
}

.player-list-section h3 {
  margin: 0 0 16px;
}

.add-player-form {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.form-row input {
  flex: 1;
  min-width: 220px;
  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid var(--color-border);
  background: rgba(15, 23, 42, 0.45);
  color: inherit;
}

.file-input {
  display: none;
}

.kick-player-row {
  margin-top: 8px;
}

.add-player-btn,
.import-file-btn,
.kick-player-btn,
.kick-file-btn {
  padding: 12px 18px;
  border-radius: 14px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s ease;
}

.add-player-btn {
  background: linear-gradient(135deg, #3dd598, #0ea371);
  color: #0f172a;
  box-shadow: 0 10px 24px rgba(61, 213, 152, 0.35);
}

.import-file-btn,
.kick-file-btn {
  background: rgba(148, 163, 184, 0.2);
  color: #d7dde5;
  border-color: transparent;
}

.kick-player-btn {
  background: rgba(248, 113, 113, 0.15);
  border-color: rgba(248, 113, 113, 0.4);
  color: #fecaca;
}

.add-player-btn:hover,
.import-file-btn:hover,
.kick-player-btn:hover,
.kick-file-btn:hover {
  transform: translateY(-1px);
}

.player-list-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.items-per-page {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--color-muted);
}

.items-per-page select {
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: inherit;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination-btn {
  padding: 8px 14px;
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
  white-space: nowrap;
}

.player-search-sort {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.search-box {
  flex: 1;
  min-width: 220px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid var(--color-border);
  background: rgba(15, 23, 42, 0.45);
  color: inherit;
}

.sort-controls {
  display: flex;
  align-items: center;
}

.sort-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 14px;
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.03);
  color: inherit;
}

.player-list {
  border: 1px solid var(--color-border);
  border-radius: 16px;
  max-height: 400px;
  overflow-y: auto;
  background: rgba(15, 23, 42, 0.35);
}

.player-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.player-item:last-child {
  border-bottom: none;
}

.player-name {
  font-weight: 500;
  color: #f8fafc;
  word-break: break-all;
}

.remove-player-btn {
  padding: 8px 14px;
  border-radius: 12px;
  border: 1px solid rgba(248, 113, 113, 0.4);
  background: rgba(248, 113, 113, 0.15);
  color: #fecaca;
  cursor: pointer;
}

.no-players {
  padding: 28px;
  text-align: center;
  color: var(--color-muted);
}

.config-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.save-btn {
  padding: 12px 28px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #3dd598, #0ea371);
  color: #0f172a;
  font-weight: 700;
  box-shadow: 0 12px 30px rgba(61, 213, 152, 0.35);
  cursor: pointer;
}

@media (max-width: 768px) {
  .whitelist-blacklist {
    padding: 16px 0;
  }

  .server-selector {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-row {
    flex-direction: column;
  }

  .player-list-controls,
  .player-search-sort {
    flex-direction: column;
    align-items: stretch;
  }

  .pagination-controls {
    justify-content: center;
  }
}
</style>