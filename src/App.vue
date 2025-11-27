<template>
  <div id="app">
    <div class="app-container">
      <header class="app-header">
        <div class="header-content">
          <div class="header-left">
            <div class="header-logo">
              <div class="logo-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zM4.5 7.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5z"/>
                </svg>
              </div>
              <div>
                <h1 class="app-title">PyMCProxy</h1>
                <p class="app-subtitle">轻量级 Minecraft 代理与监控中心</p>
              </div>
            </div>
          </div>
          <div class="header-right">
            <div class="header-status">
              <div class="status-indicator" :class="{ 'status-online': isBackendOnline, 'status-offline': !isBackendOnline }">
                <span class="status-dot"></span>
                <span class="status-text">{{ isBackendOnline ? '后端在线' : '后端离线' }}</span>
              </div>
            </div>
            <button class="nav-toggle" @click="toggleNav" aria-label="切换导航" :aria-expanded="isNavOpen">
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        </div>
      </header>
      
      <nav class="app-navigation" :class="{ 'nav-open': isNavOpen }">
        <div class="nav-content">
          <router-link to="/" class="nav-item" active-class="active" @click="closeNav">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zM4.5 7.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5z"/>
            </svg>
            仪表盘
          </router-link>
          <router-link to="/servers" class="nav-item" active-class="active" @click="closeNav">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zM4.5 7.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5z"/>
            </svg>
            服务器管理
          </router-link>
          <router-link to="/whitelist-blacklist" class="nav-item" active-class="active" @click="closeNav">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>
            </svg>
            黑白名单
          </router-link>
          <router-link to="/statistics" class="nav-item" active-class="active" @click="closeNav">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2zm13 2.383-4.758 2.855L15 11.114v-5.73zm-.034 6.878L9.271 8.82 8 9.583 6.728 8.82l-5.694 3.44A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.739zM1 11.114l4.758-2.876L1 5.383v5.73z"/>
            </svg>
            统计信息
          </router-link>
        </div>
      </nav>
      <div class="nav-backdrop" v-if="isNavOpen" @click="toggleNav"></div>
      
      <main class="app-main">
        <router-view />
      </main>
      
      <footer class="app-footer">
        <div class="footer-content">
          <p>&copy; 2025 PyMCProxy</p>
          <div class="footer-links">
            <a href="#" @click.prevent="checkBackendStatus">检查连接</a>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { getConfig } from './configLoader.js'

export default {
  name: 'App',
  data() {
    return {
      isBackendOnline: true,
      isNavOpen: false
    }
  },
  watch: {
    $route() {
      this.closeNav()
    }
  },
  async mounted() {
    await this.checkBackendStatus()
    // 定期检查后端状态
    this.backendCheckInterval = setInterval(this.checkBackendStatus, 30000)
  },
  beforeUnmount() {
    if (this.backendCheckInterval) {
      clearInterval(this.backendCheckInterval)
    }
  },
  methods: {
    toggleNav() {
      this.isNavOpen = !this.isNavOpen
    },
    closeNav() {
      this.isNavOpen = false
    },
    async checkBackendStatus() {
      try {
        const config = await getConfig();
        await axios.get(`${config.api_base_url}/api/servers`, { timeout: 5000 })
        this.isBackendOnline = true
      } catch (error) {
        this.isBackendOnline = false
      }
    }
  }
}
</script>

<style>
:root {
  --color-bg: #0f172a;
  --color-bg-soft: #111c30;
  --color-surface: rgba(15, 23, 42, 0.85);
  --color-accent: #3dd598;
  --color-accent-strong: #0ea371;
  --color-muted: #9aa5b1;
  --color-border: rgba(148, 163, 184, 0.2);
  --shadow-soft: 0 25px 45px rgba(15, 23, 42, 0.25);
  --radius-lg: 20px;
  --radius-md: 14px;
  --radius-sm: 10px;
  --glass-bg: rgba(15, 23, 42, 0.65);
  --glass-border: rgba(255, 255, 255, 0.08);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: radial-gradient(circle at 10% 20%, #1d2b4d 0%, #0b1120 60%);
  color: #e2e8f0;
  line-height: 1.6;
  min-height: 100vh;
  padding: 20px 0 40px;
}

body::before {
  content: '';
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at 80% 20%, rgba(61, 213, 152, 0.2), transparent 55%);
  pointer-events: none;
  z-index: -1;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 32px 32px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  backdrop-filter: blur(18px);
}

.app-header {
  background: linear-gradient(135deg, rgba(22, 34, 63, 0.95), rgba(9, 80, 120, 0.9));
  color: white;
  padding: 28px 32px;
  border-radius: var(--radius-lg);
  margin-top: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.app-header::after {
  content: '';
  position: absolute;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: rgba(61, 213, 152, 0.18);
  filter: blur(80px);
  top: -80px;
  right: -60px;
}

.header-content {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 32px;
  z-index: 1;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 18px;
}

.logo-icon {
  background: rgba(255, 255, 255, 0.08);
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.logo-icon svg {
  color: var(--color-accent);
}

.app-title {
  font-size: 2rem;
  font-weight: 600;
  margin: 0;
}

.app-subtitle {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.75);
  font-size: 0.95rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-status {
  padding: 10px 18px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  font-size: 0.95rem;
}

.status-online {
  color: var(--color-accent);
}

.status-offline {
  color: #f87171;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
  background: currentColor;
}

.nav-toggle {
  display: none;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  cursor: pointer;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 0;
}

.nav-toggle span {
  width: 22px;
  height: 2px;
  background: white;
  border-radius: 1px;
}

.app-navigation {
  margin: 24px 0 32px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  position: sticky;
  top: 20px;
  z-index: 20;
}

.nav-content {
  display: flex;
  gap: 12px;
  padding: 12px;
  overflow-x: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 22px;
  text-decoration: none;
  color: var(--color-muted);
  font-weight: 500;
  border-radius: 999px;
  transition: 0.3s ease;
  border: 1px solid transparent;
  white-space: nowrap;
}

.nav-item svg {
  color: inherit;
}

.nav-item:hover {
  color: #f8fafc;
  border-color: rgba(248, 250, 252, 0.2);
}

.nav-item.active {
  color: #0f172a;
  background: linear-gradient(135deg, #3dd598, #0ea371);
  border-color: transparent;
  box-shadow: 0 12px 30px rgba(61, 213, 152, 0.35);
}

.nav-backdrop {
  display: none;
}

.app-main {
  flex: 1;
  margin-bottom: 40px;
}

.app-footer {
  margin-top: auto;
  padding: 28px 0 0;
  color: var(--color-muted);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.footer-links a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
}

.footer-links a:hover {
  text-decoration: underline;
}

@media (max-width: 1024px) {
  .app-container {
    padding: 0 20px 24px;
  }
}

@media (max-width: 768px) {
  body {
    padding: 10px 0 24px;
  }

  .app-header {
    padding: 24px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .nav-toggle {
    display: flex;
  }

  .app-navigation {
    position: fixed;
    top: 16px;
    right: 16px;
    left: 16px;
    transform: translateY(-140%);
    transition: transform 0.35s ease;
  }

  .app-navigation.nav-open {
    transform: translateY(0);
  }

  .nav-content {
    flex-direction: column;
    max-height: calc(100vh - 80px);
  }

  .nav-item {
    width: 100%;
    justify-content: center;
  }

  .nav-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(2, 6, 23, 0.55);
    backdrop-filter: blur(4px);
    z-index: 10;
  }

  .footer-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>