<template>
  <div class="portal-container">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="title">
          <span class="greeting">浙江科技大学</span>
          <span class="highlight">和满仓</span>
        </h1>
        <p class="subtitle">智慧用餐 • 实时数据 • 智能推荐</p>
      </div>
      <div class="hero-decoration">
        <div class="floating-shape shape-1"></div>
        <div class="floating-shape shape-2"></div>
        <div class="floating-shape shape-3"></div>
      </div>
    </div>

    <el-row :gutter="30">
      <!-- Left Column: Traffic & Notices -->
      <el-col :span="8">
        <!-- Traffic Widget -->
        <div class="glass-card traffic-widget">
          <div class="widget-header">
            <div class="header-title">
              <span class="icon">🚦</span>
              <h3>实时人流</h3>
            </div>
            <el-tag :type="trafficStatusType" effect="dark" round class="status-tag">
              {{ trafficData.status }}
            </el-tag>
          </div>
          
          <div class="traffic-circle-container">
            <div class="liquid-circle" :class="trafficStatusClass">
              <div class="liquid" :style="{ top: (100 - trafficData.traffic) + '%' }"></div>
              <div class="content">
                <span class="percentage">{{ trafficData.traffic }}<small>%</small></span>
                <span class="label">占用率</span>
              </div>
            </div>
          </div>
          
          <div class="chart-container">
            <div ref="trafficChartRef" class="mini-chart"></div>
          </div>
        </div>

        <!-- Notices Widget -->
        <div class="glass-card notice-widget">
          <div class="widget-header">
            <div class="header-title">
              <span class="icon">📢</span>
              <h3>公告通知</h3>
            </div>
          </div>
          <div class="notice-list">
            <div class="notice-item warning">
              <div class="icon-box">⚠️</div>
              <div class="text">
                <strong>维护通知</strong>
                <p>二楼窗口正在进行设备升级维护。</p>
              </div>
            </div>
            <div class="notice-item new">
              <div class="icon-box">✨</div>
              <div class="text">
                <strong>新品上市</strong>
                <p>夏季特饮"杨枝甘露"今日上线！</p>
              </div>
            </div>
            <div class="notice-item promo">
              <div class="icon-box">🎁</div>
              <div class="text">
                <strong>光盘行动</strong>
                <p>参与光盘打卡满10次送酸奶。</p>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Right Column: Leaderboard -->
      <el-col :span="16">
        <div class="glass-card leaderboard-widget">
          <div class="widget-header">
            <div class="header-title">
              <span class="icon">🔥</span>
              <h3>热门榜单 TOP 10</h3>
            </div>
            <span class="update-time">更新于: {{ updateTime }}</span>
          </div>
          
          <!-- Podium for Top 3 -->
          <div class="podium-container" v-if="leaderboard.length >= 3">
            <div class="podium-item second">
              <div class="crown">🥈</div>
              <div class="avatar-wrapper">
                <div class="avatar">{{ leaderboard[1]?.name[0] }}</div>
                <div class="rank-badge">2</div>
              </div>
              <div class="info-card">
                <div class="name">{{ leaderboard[1]?.name }}</div>
                <div class="score">¥{{ leaderboard[1]?.price }}</div>
              </div>
              <div class="block"></div>
            </div>
            <div class="podium-item first">
              <div class="crown">👑</div>
              <div class="avatar-wrapper">
                <div class="avatar">{{ leaderboard[0]?.name[0] }}</div>
                <div class="rank-badge">1</div>
              </div>
              <div class="info-card">
                <div class="name">{{ leaderboard[0]?.name }}</div>
                <div class="score">¥{{ leaderboard[0]?.price }}</div>
              </div>
              <div class="block"></div>
            </div>
            <div class="podium-item third">
              <div class="crown">🥉</div>
              <div class="avatar-wrapper">
                <div class="avatar">{{ leaderboard[2]?.name[0] }}</div>
                <div class="rank-badge">3</div>
              </div>
              <div class="info-card">
                <div class="name">{{ leaderboard[2]?.name }}</div>
                <div class="score">¥{{ leaderboard[2]?.price }}</div>
              </div>
              <div class="block"></div>
            </div>
          </div>

          <!-- List for Rest -->
          <div class="leaderboard-list">
            <div 
              v-for="(dish, index) in leaderboard.slice(3)" 
              :key="dish._id" 
              class="rank-row"
            >
              <div class="rank-num">{{ index + 4 }}</div>
              <div class="dish-info">
                <div class="name">{{ dish.name }}</div>
                <div class="tags">
                  <span v-for="tag in dish.tags.slice(0, 2)" :key="tag" class="mini-tag">{{ tag }}</span>
                </div>
              </div>
              <div class="price">¥{{ dish.price }}</div>
              <div class="trend">
                <el-icon color="#ff7675"><Top /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Top } from '@element-plus/icons-vue'
import api from '../api'

const leaderboard = ref([])
const trafficData = ref({ traffic: 0, status: 'Loading', predicted_trend: [], hours: [] })
const updateTime = ref(new Date().toLocaleTimeString())
const trafficChartRef = ref(null)

const trafficStatusType = computed(() => {
  const s = trafficData.value.status
  if (s === '空闲') return 'success'
  if (s === '繁忙') return 'warning'
  return 'danger'
})

const trafficStatusClass = computed(() => {
  const s = trafficData.value.status
  if (s === '空闲') return 'status-green'
  if (s === '繁忙') return 'status-orange'
  return 'status-red'
})

const getTrafficColor = (val) => {
  if (val < 50) return 'var(--success-color)'
  if (val < 80) return 'var(--warning-color)'
  return 'var(--danger-color)'
}

const initTrafficChart = () => {
  if (!trafficChartRef.value || !trafficData.value.predicted_trend) return
  
  const currentHour = new Date().getHours()
  const currentHourStr = `${currentHour}点`
  const fullData = trafficData.value.predicted_trend
  
  // Split data
  const pastData = fullData.map((val, idx) => idx <= currentHour ? val : null)
  const futureData = fullData.map((val, idx) => idx >= currentHour ? val : null)
  
  const chart = echarts.init(trafficChartRef.value)
  chart.setOption({
    tooltip: { 
      trigger: 'axis', 
      formatter: (params) => {
        // Find the series that has a value (either past or future)
        const item = params.find(p => p.value !== null && p.value !== undefined)
        return item ? `${item.name}: ${item.value}人` : ''
      }
    },
    grid: { left: '0%', right: '5%', bottom: '0%', top: '10%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: trafficData.value.hours,
      show: true,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { interval: 3, color: '#94a3b8', fontSize: 10 }
    },
    yAxis: { show: false },
    series: [
      {
        data: pastData,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: '#94a3b8' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(148, 163, 184, 0.5)' },
            { offset: 1, color: 'rgba(148, 163, 184, 0.0)' }
          ])
        }
      },
      {
        data: futureData,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: '#6366f1', type: 'dashed' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(99, 102, 241, 0.5)' },
            { offset: 1, color: 'rgba(99, 102, 241, 0.0)' }
          ])
        },
        markLine: {
          symbol: ['none', 'none'],
          label: { show: false },
          lineStyle: { color: '#ef4444', type: 'solid', width: 1 },
          data: [
            { xAxis: currentHourStr }
          ]
        }
      }
    ]
  })
}

const fetchData = async () => {
  try {
    const [lbRes, tfRes] = await Promise.all([
      api.get('/portal/leaderboard'),
      api.get('/portal/traffic_prediction')
    ])
    leaderboard.value = lbRes.data
    trafficData.value = tfRes.data
    updateTime.value = new Date().toLocaleTimeString()
    
    nextTick(() => {
      initTrafficChart()
    })
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchData()
  fetchData()
  setInterval(fetchData, 30000)
  
  window.addEventListener('resize', () => {
    if (trafficChartRef.value) echarts.getInstanceByDom(trafficChartRef.value)?.resize()
  })
})
</script>

<style scoped>
.portal-container {
  padding-bottom: 40px;
}

/* Hero Section */
.hero-section {
  position: relative;
  padding: 20px 0 60px;
  margin-bottom: 20px;
}

.title {
  font-family: 'Outfit', sans-serif;
  font-size: 4.5rem;
  margin: 0;
  line-height: 1;
  display: flex;
  flex-direction: column;
  text-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.title .greeting {
  font-weight: 300;
  color: var(--text-primary);
  animation: slideInLeft 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.title .highlight {
  font-weight: 800;
  background: linear-gradient(120deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: slideInRight 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.subtitle {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin-top: 20px;
  letter-spacing: 1px;
  animation: fadeIn 1s ease-out 0.5s backwards;
  font-weight: 500;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  z-index: -1;
  opacity: 0.5;
  animation: float 8s ease-in-out infinite alternate;
}

.shape-1 {
  width: 300px;
  height: 300px;
  background: var(--primary-light);
  top: -50px;
  right: 5%;
}

.shape-2 {
  width: 200px;
  height: 200px;
  background: var(--secondary-color);
  bottom: 10%;
  right: 25%;
  animation-delay: 2s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  background: var(--success-color);
  top: 20%;
  left: 40%;
  animation-delay: -2s;
  opacity: 0.3;
}

/* Widgets Common */
.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 24px 24px 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title .icon {
  font-size: 1.5rem;
}

.widget-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

/* Traffic Widget */
.traffic-widget {
  padding-bottom: 24px;
  margin-bottom: 30px;
}

.traffic-circle-container {
  display: flex;
  justify-content: center;
  padding: 20px 0 40px;
}

.liquid-circle {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  border: 6px solid rgba(255,255,255,0.5);
  position: relative;
  overflow: hidden;
  background: rgba(255,255,255,0.2);
  box-shadow: inset 0 0 30px rgba(0,0,0,0.05), 0 10px 30px rgba(0,0,0,0.1);
}

.liquid {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--primary-color);
  transition: top 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.liquid::before, .liquid::after {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
  background: rgba(255,255,255,0.4);
  border-radius: 40%;
  /* animation: wave 6s linear infinite; Removed spinning animation */
}

.liquid::after {
  border-radius: 35%;
  background: rgba(255,255,255,0.2);
  /* animation: wave 8s linear infinite; Removed spinning animation */
}

.status-green .liquid { background: var(--success-color); }
.status-orange .liquid { background: var(--warning-color); }
.status-red .liquid { background: var(--danger-color); }

@keyframes wave {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.liquid-circle .content {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  color: var(--text-primary);
}

.percentage {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1;
}

.percentage small {
  font-size: 1.5rem;
  opacity: 0.6;
}

.label {
  font-size: 0.9rem;
  font-weight: 600;
  opacity: 0.7;
  margin-top: 5px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.chart-container {
  padding: 0 24px;
  height: 120px;
  margin-top: 10px;
}

.mini-chart {
  width: 100%;
  height: 100%;
}

/* Notice Widget */
.notice-list {
  padding: 0 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.notice-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border-radius: 16px;
  background: rgba(255,255,255,0.5);
  border: 1px solid rgba(255,255,255,0.6);
  transition: all 0.3s ease;
}

.notice-item:hover {
  transform: translateX(5px);
  background: rgba(255,255,255,0.8);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.icon-box {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  background: white;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.notice-item .text strong {
  display: block;
  margin-bottom: 4px;
  font-size: 1rem;
  color: var(--text-primary);
}

.notice-item .text p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.notice-item.warning .icon-box { background: #fff7ed; color: #f59e0b; }
.notice-item.new .icon-box { background: #ecfdf5; color: #10b981; }
.notice-item.promo .icon-box { background: #fef2f2; color: #ef4444; }

/* Leaderboard Widget */
.leaderboard-widget {
  min-height: 600px;
}

.podium-container {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  height: 300px;
  margin-bottom: 40px;
  padding-top: 20px;
  gap: 20px;
}

.podium-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 120px;
}

.avatar-wrapper {
  position: relative;
  margin-bottom: 15px;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.5rem;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
  border: 3px solid white;
}

.rank-badge {
  position: absolute;
  bottom: -5px;
  right: -5px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--text-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
  border: 2px solid white;
}

.crown {
  position: absolute;
  top: -40px;
  font-size: 2.5rem;
  animation: bounce 2s infinite;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
}

.info-card {
  background: rgba(255,255,255,0.9);
  padding: 8px 12px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  width: 100%;
  z-index: 2;
}

.info-card .name {
  font-weight: 700;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-card .score {
  font-size: 0.85rem;
  color: var(--primary-color);
  font-weight: 600;
}

.block {
  width: 100%;
  border-radius: 16px 16px 0 0;
  position: relative;
  overflow: hidden;
}

.block::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(to bottom, rgba(255,255,255,0.2), transparent);
}

.first .block { 
  height: 140px; 
  background: linear-gradient(135deg, #fbbf24, #d97706);
  box-shadow: 0 10px 30px rgba(251, 191, 36, 0.3);
}
.second .block { 
  height: 100px; 
  background: linear-gradient(135deg, #94a3b8, #64748b);
  box-shadow: 0 10px 30px rgba(148, 163, 184, 0.3);
}
.third .block { 
  height: 80px; 
  background: linear-gradient(135deg, #f87171, #dc2626);
  box-shadow: 0 10px 30px rgba(248, 113, 113, 0.3);
}

.first .avatar { width: 80px; height: 80px; font-size: 2rem; border-color: #fbbf24; }
.second .avatar { border-color: #94a3b8; }
.third .avatar { border-color: #f87171; }

.leaderboard-list {
  padding: 0 30px 30px;
}

.rank-row {
  display: flex;
  align-items: center;
  padding: 16px;
  border-radius: 16px;
  margin-bottom: 10px;
  background: rgba(255,255,255,0.4);
  border: 1px solid rgba(255,255,255,0.4);
  transition: all 0.2s;
}

.rank-row:hover {
  background: rgba(255,255,255,0.8);
  transform: scale(1.01) translateX(5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.rank-num {
  width: 30px;
  font-weight: 700;
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.dish-info {
  flex-grow: 1;
}

.dish-info .name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 4px;
}

.mini-tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  border-radius: 6px;
  margin-right: 6px;
  font-weight: 500;
}

.price {
  font-weight: 700;
  color: var(--text-primary);
  margin-right: 20px;
  font-size: 1.1rem;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .title {
    font-size: 3rem;
  }
  
  .hero-section {
    padding: 10px 0 30px;
  }
  
  .el-col {
    width: 100% !important;
    flex: 0 0 100% !important;
    max-width: 100% !important;
  }
  
  .traffic-widget, .notice-widget {
    margin-bottom: 20px;
  }
  
  .podium-container {
    height: auto;
    align-items: flex-end;
    padding-top: 40px;
    gap: 10px;
  }
  
  .podium-item {
    width: 30%;
  }
  
  .avatar {
    width: 48px;
    height: 48px;
    font-size: 1.2rem;
  }
  
  .first .avatar {
    width: 64px;
    height: 64px;
  }
  
  .info-card .name {
    font-size: 0.8rem;
  }
  
  .leaderboard-list {
    padding: 0 15px 20px;
  }
}
</style>
