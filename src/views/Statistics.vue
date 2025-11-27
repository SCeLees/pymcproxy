<template>
  <div class="statistics">
    <div class="page-header">
      <h1>统计信息</h1>
      <div class="page-actions">
        <button class="refresh-btn" @click="refreshData">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1h.5a.5.5 0 0 1 0 1H8z"/>
          </svg>
          刷新数据
        </button>
      </div>
    </div>
    
    <div class="stats-overview">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-header">
            <h2>系统统计</h2>
          </div>
          <div class="card-body">
            <div class="system-stats">
              <div class="stat-item">
                <span class="stat-label">总运行时间:</span>
                <span class="stat-value">{{ formatDuration(appStats.total_runtime) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">总连接数:</span>
                <span class="stat-value">{{ appStats.total_connections }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">总流量:</span>
                <span class="stat-value">{{ formatBytes(appStats.total_traffic) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="player-stats-section">
      <div class="section-header">
        <h2>玩家统计</h2>
        <div class="section-info">
          共 {{ Object.keys(playerStats).length }} 名玩家
        </div>
      </div>
      
      <div class="stats-controls">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索玩家..." 
            class="search-input"
          >
        </div>
        <div class="items-per-page">
          <label for="itemsPerPage">每页显示:</label>
          <select id="itemsPerPage" v-model="itemsPerPage">
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>
      
      <div class="stats-table-container">
        <div class="table-responsive">
          <table class="stats-table">
            <thead>
              <tr>
                <th @click="sort('player')" class="sortable">
                  玩家ID
                  <span class="sort-indicator" :class="getSortClass('player')"></span>
                </th>
                <th @click="sort('connections')" class="sortable">
                  连接次数
                  <span class="sort-indicator" :class="getSortClass('connections')"></span>
                </th>
                <th @click="sort('time')" class="sortable">
                  在线时间
                  <span class="sort-indicator" :class="getSortClass('time')"></span>
                </th>
                <th @click="sort('traffic')" class="sortable">
                  消耗流量
                  <span class="sort-indicator" :class="getSortClass('traffic')"></span>
                </th>
                <th @click="sort('avgTime')" class="sortable">
                  平均连接时长
                  <span class="sort-indicator" :class="getSortClass('avgTime')"></span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="paginatedPlayers.length === 0">
                <td colspan="5" class="no-data">暂无玩家数据</td>
              </tr>
              <tr 
                v-for="player in paginatedPlayers" 
                :key="player"
                class="player-row"
              >
                <td data-label="玩家ID">
                  <div class="player-info">
                    <div class="player-avatar">
                      <span>{{ player.charAt(0).toUpperCase() }}</span>
                    </div>
                    <span class="player-name">{{ player }}</span>
                  </div>
                </td>
                <td data-label="连接次数">{{ playerStats[player].total_connections }}</td>
                <td data-label="在线时间">{{ formatDuration(playerStats[player].total_time) }}</td>
                <td data-label="消耗流量">{{ formatBytes(playerStats[player].total_traffic) }}</td>
                <td data-label="平均连接时长">{{ formatDuration(playerStats[player].total_time / playerStats[player].total_connections) }}</td>
              </tr>
            </tbody>
          </table>
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
    
    <div class="charts-section">
      <div class="section-header">
        <h2>数据图表</h2>
        <div class="chart-controls">
          <div class="chart-type-selector">
            <label for="topPlayers">显示前:</label>
            <select id="topPlayers" v-model="topPlayersCount">
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="15">15</option>
              <option value="20">20</option>
            </select>
            <span>名玩家</span>
          </div>
        </div>
      </div>
      
      <div class="charts-container">
        <div class="chart-card">
          <h3>玩家连接次数分布</h3>
          <div class="chart-wrapper">
            <canvas ref="connectionsChart"></canvas>
          </div>
        </div>
        
        <div class="chart-card">
          <h3>玩家在线时间分布</h3>
          <div class="chart-wrapper">
            <canvas ref="timeChart"></canvas>
          </div>
        </div>
        
        <div class="chart-card">
          <h3>玩家消耗流量分布</h3>
          <div class="chart-wrapper">
            <canvas ref="trafficChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Chart from 'chart.js/auto'

export default {
  name: 'Statistics',
  data() {
    return {
      appStats: {
        total_runtime: 0,
        total_connections: 0,
        total_traffic: 0
      },
      playerStats: {},
      searchQuery: '',
      sortKey: 'traffic',
      sortOrder: -1, // -1 for descending, 1 for ascending
      currentPage: 1,
      itemsPerPage: 25,
      topPlayersCount: 10,
      connectionsChart: null,
      timeChart: null,
      trafficChart: null
    }
  },
  computed: {
    filteredPlayers() {
      const query = this.searchQuery.toLowerCase()
      return Object.keys(this.playerStats).filter(player => 
        player.toLowerCase().includes(query)
      )
    },
    
    sortedPlayers() {
      const players = [...this.filteredPlayers]
      return players.sort((a, b) => {
        let modifier = this.sortOrder
        switch (this.sortKey) {
          case 'player':
            return a.localeCompare(b) * modifier
          case 'connections':
            return (this.playerStats[a].total_connections - this.playerStats[b].total_connections) * modifier
          case 'time':
            return (this.playerStats[a].total_time - this.playerStats[b].total_time) * modifier
          case 'traffic':
            return (this.playerStats[a].total_traffic - this.playerStats[b].total_traffic) * modifier
          case 'avgTime':
            const avgA = this.playerStats[a].total_time / this.playerStats[a].total_connections
            const avgB = this.playerStats[b].total_time / this.playerStats[b].total_connections
            return (avgA - avgB) * modifier
          default:
            return 0
        }
      })
    },
    
    paginatedPlayers() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.sortedPlayers.slice(start, end)
    },
    
    totalPages() {
      return Math.ceil(this.sortedPlayers.length / this.itemsPerPage)
    },
    
    topPlayersByConnections() {
      return Object.keys(this.playerStats)
        .sort((a, b) => this.playerStats[b].total_connections - this.playerStats[a].total_connections)
        .slice(0, this.topPlayersCount)
    },
    
    topPlayersByTime() {
      return Object.keys(this.playerStats)
        .sort((a, b) => this.playerStats[b].total_time - this.playerStats[a].total_time)
        .slice(0, this.topPlayersCount)
    },
    
    topPlayersByTraffic() {
      return Object.keys(this.playerStats)
        .sort((a, b) => this.playerStats[b].total_traffic - this.playerStats[a].total_traffic)
        .slice(0, this.topPlayersCount)
    }
  },
  watch: {
    searchQuery() {
      this.currentPage = 1
    },
    itemsPerPage() {
      this.currentPage = 1
    },
    topPlayersCount() {
      this.updateCharts()
    },
    chartType() {  // 添加对图表类型变化的监听
      this.updateCharts()
    },
    playerStats: {
      handler() {
        this.updateCharts()
      },
      deep: true
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
    if (this.connectionsChart) {
      this.connectionsChart.destroy()
    }
    if (this.timeChart) {
      this.timeChart.destroy()
    }
    if (this.trafficChart) {
      this.trafficChart.destroy()
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
    
    sort(key) {
      if (this.sortKey === key) {
        this.sortOrder = -this.sortOrder
      } else {
        this.sortKey = key
        this.sortOrder = -1
      }
      this.currentPage = 1
    },
    
    getSortClass(key) {
      if (this.sortKey !== key) {
        return 'sort-none'
      }
      return this.sortOrder > 0 ? 'sort-asc' : 'sort-desc'
    },
    
    formatDuration(seconds) {
      if (isNaN(seconds) || seconds === 0) return '0秒'
      
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
    
    updateCharts() {
      this.$nextTick(() => {
        this.updateConnectionsChart()
        this.updateTimeChart()
        this.updateTrafficChart()
      })
    },
    
    updateConnectionsChart() {
      if (this.connectionsChart) {
        this.connectionsChart.destroy()
      }
      
      const ctx = this.$refs.connectionsChart.getContext('2d')
      const players = this.topPlayersByConnections
      const data = players.map(player => this.playerStats[player].total_connections)
      
      // 玩家连接次数分布使用水平条形图，便于比较不同玩家的活跃度差异
      const chartConfig = {
        type: 'bar',
        data: {
          labels: players,
          datasets: [{
            label: '连接次数',
            data: data,
            backgroundColor: [
              '#FF6384',
              '#36A2EB',
              '#FFCE56',
              '#4BC0C0',
              '#9966FF',
              '#FF9F40',
              '#8AC926',
              '#1982C4',
              '#6A4C93',
              '#F15BB5',
              '#00BBF9',
              '#00F5D4',
              '#9B5DE5',
              '#FEE440',
              '#00BBF9'
            ],
            borderColor: '#fff',
            borderWidth: 2
          }]
        },
        options: {
          indexAxis: 'y', // 水平条形图
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  return `${context.label}: ${context.raw} 次连接`
                }
              }
            }
          }
        }
      }
      
      this.connectionsChart = new Chart(ctx, chartConfig)
    },
    
    updateTimeChart() {
      if (this.timeChart) {
        this.timeChart.destroy()
      }
      
      const ctx = this.$refs.timeChart.getContext('2d')
      const players = this.topPlayersByTime
      const data = players.map(player => this.playerStats[player].total_time)
      
      // 玩家在线时间分布使用垂直条形图，便于展示时长对比
      const chartConfig = {
        type: 'bar',
        data: {
          labels: players,
          datasets: [{
            label: '在线时间 (分钟)',
            data: data.map(t => t/60), // 转换为分钟
            backgroundColor: [
              '#FF6384',
              '#36A2EB',
              '#FFCE56',
              '#4BC0C0',
              '#9966FF',
              '#FF9F40',
              '#8AC926',
              '#1982C4',
              '#6A4C93',
              '#F15BB5',
              '#00BBF9',
              '#00F5D4',
              '#9B5DE5',
              '#FEE440',
              '#00BBF9'
            ],
            borderColor: '#fff',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  return `${context.label}: ${this.formatDuration(context.raw*60)}`
                }
              }
            }
          }
        }
      }
      
      this.timeChart = new Chart(ctx, chartConfig)
    },
    
    updateTrafficChart() {
      if (this.trafficChart) {
        this.trafficChart.destroy()
      }
      
      const ctx = this.$refs.trafficChart.getContext('2d')
      const players = this.topPlayersByTraffic
      const data = players.map(player => this.playerStats[player].total_traffic)
      
      // 玩家消耗流量分布使用环形图，便于直观显示流量占比情况
      const chartConfig = {
        type: 'doughnut',
        data: {
          labels: players,
          datasets: [{
            data: data,
            backgroundColor: [
              '#FF6384',
              '#36A2EB',
              '#FFCE56',
              '#4BC0C0',
              '#9966FF',
              '#FF9F40',
              '#8AC926',
              '#1982C4',
              '#6A4C93',
              '#F15BB5',
              '#00BBF9',
              '#00F5D4',
              '#9B5DE5',
              '#FEE440',
              '#00BBF9'
            ],
            borderColor: '#fff',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  return `${context.label}: ${this.formatBytes(context.raw)}`
                }
              }
            }
          }
        }
      }
      
      this.trafficChart = new Chart(ctx, chartConfig)
    }
  }
}
</script>

<style scoped>
.statistics {
  padding: 24px 0;
  width: 100%;
  color: #e2e8f0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
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
  box-shadow: 0 12px 30px rgba(61, 213, 152, 0.35);
}

.stats-overview {
  margin-bottom: 32px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.overview-card {
  background: var(--color-surface);
  border-radius: 20px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.card-body {
  padding: 22px 24px;
}

.system-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-label {
  color: var(--color-muted);
}

.stat-value {
  font-weight: 700;
  font-size: 1.1rem;
}

.player-stats-section,
.charts-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-info {
  color: var(--color-muted);
}

.stats-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  flex-wrap: wrap;
  gap: 12px;
}

.search-box {
  flex: 1;
  min-width: 260px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid var(--color-border);
  background: rgba(15, 23, 42, 0.45);
  color: inherit;
}

.items-per-page {
  display: inline-flex;
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

.stats-table-container {
  background: var(--color-surface);
  border-radius: 24px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.table-responsive {
  overflow-x: auto;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 720px;
  color: inherit;
}

.stats-table thead {
  background: rgba(15, 23, 42, 0.6);
}

.stats-table th {
  padding: 16px 18px;
  text-align: left;
  font-size: 0.8rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-muted);
  cursor: pointer;
  position: relative;
}

.stats-table th.sortable:hover {
  background: rgba(255, 255, 255, 0.03);
}

.sort-indicator {
  position: absolute;
  right: 12px;
  top: 50%;
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  transform: translateY(-50%);
}

.sort-asc {
  border-bottom: 5px solid #9ca3af;
}

.sort-desc {
  border-top: 5px solid #9ca3af;
}

.sort-none {
  border-top: 5px solid rgba(148, 163, 184, 0.4);
  border-bottom: 5px solid rgba(148, 163, 184, 0.4);
}

.stats-table td {
  padding: 16px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.stats-table tbody tr:hover {
  background: rgba(61, 213, 152, 0.05);
}

.player-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.player-avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, #3dd598, #0ea371);
  color: #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.pagination-btn {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: inherit;
}

.pagination-btn:hover:not(:disabled) {
  border-color: rgba(61, 213, 152, 0.6);
}

.pagination-btn:disabled {
  opacity: 0.4;
}

.pagination-info {
  color: var(--color-muted);
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.chart-card {
  background: var(--color-surface);
  border-radius: 20px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-soft);
  padding: 20px;
}

.chart-card h3 {
  text-align: center;
  margin: 0 0 16px;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--color-muted);
}

.chart-type-selector select {
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: inherit;
}

.chart-wrapper {
  height: 280px;
}

@media (max-width: 768px) {
  .statistics {
    padding: 16px 0;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-controls,
  .section-header,
  .chart-controls {
    flex-direction: column;
    align-items: flex-start;
  }

  .pagination {
    flex-wrap: wrap;
  }
}
</style>