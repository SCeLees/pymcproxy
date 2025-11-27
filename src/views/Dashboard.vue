<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>仪表盘</h1>
      <div class="dashboard-actions">
        <button class="refresh-btn" @click="refreshData">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1h.5a.5.5 0 0 1 0 1H8z"/>
          </svg>
          刷新数据
        </button>
      </div>
    </div>
    
    <div class="stats-overview">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon bg-primary">
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
          <div class="stat-icon bg-success">
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
          <div class="stat-icon bg-info">
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
        
        <div class="stat-card">
          <div class="stat-icon bg-warning">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1H7zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
              <path fill-rule="evenodd" d="M5.216 14A2.238 2.238 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.325 6.325 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1h4.216z"/>
              <path d="M4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/>
            </svg>
          </div>
          <div class="stat-content">
            <h3>玩家数量</h3>
            <p class="stat-value">{{ Object.keys(playerStats).length }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="recent-activity">
      <h2>最近活动</h2>
      <div class="activity-controls" v-if="Object.keys(playerStats).length > 5">
        <div class="items-per-page">
          <label for="itemsPerPage">每页显示:</label>
          <select id="itemsPerPage" v-model="itemsPerPage">
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="25">25</option>
          </select>
        </div>
      </div>
      <div class="activity-list">
        <div v-if="Object.keys(playerStats).length === 0" class="no-activity">
          <p>暂无活动记录</p>
        </div>
        <div v-else class="activity-items">
          <div 
            v-for="(player, index) in displayedPlayers" 
            :key="player" 
            class="activity-item"
          >
            <div class="player-avatar">
              <span>{{ player.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="player-info">
              <h4>{{ player }}</h4>
              <p>连接 {{ playerStats[player].total_connections }} 次，累计在线 {{ formatDuration(playerStats[player].total_time) }}</p>
            </div>
            <div class="player-traffic">
              {{ formatBytes(playerStats[player].total_traffic) }}
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

export default {
  name: 'Dashboard',
  data() {
    return {
      appStats: {
        total_runtime: 0,
        total_connections: 0,
        total_traffic: 0
      },
      playerStats: {},
      currentPage: 1,
      itemsPerPage: 5
    }
  },
  computed: {
    sortedPlayerStats() {
      // 按连接次数排序玩家
      const sorted = {}
      Object.keys(this.playerStats)
        .sort((a, b) => this.playerStats[b].total_connections - this.playerStats[a].total_connections)
        .forEach(key => sorted[key] = this.playerStats[key])
      return sorted
    },
    
    displayedPlayers() {
      const players = Object.keys(this.sortedPlayerStats)
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return players.slice(start, end)
    },
    
    totalPages() {
      return Math.ceil(Object.keys(this.playerStats).length / this.itemsPerPage)
    }
  },
  async mounted() {
    await this.fetchStats()
    this.statsInterval = setInterval(this.fetchStats, 5000)
  },
  beforeUnmount() {
    if (this.statsInterval) {
      clearInterval(this.statsInterval)
    }
  },
  methods: {
    async fetchStats() {
      try {
        const response = await axios.get('http://localhost:5000/api/stats')
        this.appStats = response.data.app
        this.playerStats = response.data.players
      } catch (error) {
        console.error('获取统计数据失败:', error)
      }
    },
    
    async refreshData() {
      await this.fetchStats()
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
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 24px 0;
  width: 100%;
  color: #e2e8f0;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  gap: 16px;
  flex-wrap: wrap;
}

.dashboard-header h1 {
  font-size: 2rem;
  margin: 0;
}

.refresh-btn {
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

.refresh-btn:hover {
  transform: translateY(-1px);
}

.stats-overview {
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  background: var(--color-surface);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-soft);
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: rgba(61, 213, 152, 0.4);
}

.stat-icon {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 18px;
  color: white;
  background: linear-gradient(135deg, rgba(61, 213, 152, 0.25), rgba(14, 163, 113, 0.45));
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.bg-primary {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.4), rgba(14, 165, 233, 0.45));
}

.bg-success {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.45), rgba(16, 185, 129, 0.55));
}

.bg-info {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.45), rgba(99, 102, 241, 0.55));
}

.bg-warning {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.4), rgba(249, 115, 22, 0.5));
}

.stat-content h3 {
  font-size: 1rem;
  color: var(--color-muted);
  margin-bottom: 6px;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
}

.recent-activity h2 {
  font-size: 1.4rem;
  margin-bottom: 16px;
}

.activity-controls {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.items-per-page {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: var(--color-muted);
}

.items-per-page select {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: transparent;
  color: inherit;
  font-family: inherit;
}

.activity-list {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  padding: 24px;
  box-shadow: var(--shadow-soft);
  margin-bottom: 24px;
}

.no-activity {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-muted);
}

.activity-items {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid transparent;
  transition: border-color 0.3s ease;
}

.activity-item:hover {
  border-color: rgba(61, 213, 152, 0.35);
  background: rgba(61, 213, 152, 0.06);
}

.player-avatar {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  background: linear-gradient(135deg, #3dd598, #0ea371);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0f172a;
  font-weight: 700;
  font-size: 1.15rem;
  margin-right: 20px;
}

.player-info h4 {
  margin: 0 0 4px;
  font-size: 1.05rem;
}

.player-info p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-muted);
}

.player-traffic {
  font-weight: 600;
  margin-left: auto;
  min-width: 120px;
  display: flex;
  justify-content: center;
  text-align: center;
  padding: 10px 16px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 18px;
  background: rgba(15, 23, 42, 0.8);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-soft);
  flex-wrap: wrap;
}

.pagination-btn {
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: inherit;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  border-color: rgba(61, 213, 152, 0.6);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: var(--color-muted);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 16px 0;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .stat-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .stat-icon {
    margin-right: 0;
  }

  .activity-item {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .player-avatar {
    margin-right: 0;
  }

  .player-info {
    width: 100%;
  }

  .activity-controls {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .refresh-btn {
    width: 100%;
    justify-content: center;
  }

  .items-per-page select {
    width: 100%;
  }
}
</style>