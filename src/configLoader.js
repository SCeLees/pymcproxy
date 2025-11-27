// 配置加载器，从后端获取配置信息
let config = null;

// 默认配置
const defaultConfig = {
  api_base_url: 'http://localhost:5000'
};

// 获取配置信息
async function loadConfig() {
  try {
    const response = await fetch('http://localhost:5000/api/config');
    if (response.ok) {
      const frontendConfig = await response.json();
      config = {
        ...defaultConfig,
        ...frontendConfig
      };
    } else {
      // 如果获取配置失败，使用默认配置
      config = defaultConfig;
    }
  } catch (error) {
    console.warn('无法从后端获取配置，使用默认配置:', error);
    config = defaultConfig;
  }
  
  return config;
}

// 获取配置（如果尚未加载则先加载）
async function getConfig() {
  if (!config) {
    await loadConfig();
  }
  return config;
}

export { getConfig, loadConfig };