<template>
  <div class="admin-container" v-loading.fullscreen.lock="loading" element-loading-text="数据加载中..." element-loading-background="rgba(248, 250, 252, 0.8)">
    <div class="dashboard-header">
      <div class="header-content">
        <h1>智慧食堂数据大屏</h1>
        <p>多维数据分析 • 实时监控 • 决策支持</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" round>
          <el-icon class="mr-1"><Download /></el-icon> 导出报表
        </el-button>
      </div>
    </div>
    
    <!-- Quick Stats Row -->
    <el-row :gutter="24" class="stats-row">
      <el-col :span="6" v-for="(stat, index) in quickStats" :key="index">
        <div class="glass-card stat-card" :style="{ animationDelay: index * 0.1 + 's' }">
          <div class="stat-icon" :class="stat.type">
            <el-icon><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
          <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
            <el-icon><component :is="stat.trend > 0 ? 'Top' : 'Bottom'" /></el-icon>
            {{ Math.abs(stat.trend) }}%
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- Row 1: Sales & Revenue -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="16">
        <div class="glass-card chart-card">
          <div class="card-header">
            <div class="title-group">
              <span class="icon">📈</span>
              <span>销量趋势分析（近7天）</span>
            </div>
            <el-tooltip content="展示每小时的订单总量" placement="top">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          <div ref="trendChartRef" class="chart-lg"></div>
        </div>
      </el-col>
      
      <el-col :span="8">
        <div class="glass-card chart-card">
          <div class="card-header">
            <div class="title-group">
              <span class="icon">💰</span>
              <span>营收趋势（近30天）</span>
            </div>
            <el-tooltip content="每日总营收趋势" placement="top">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          <div ref="revenueChartRef" class="chart-lg"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Row 2: Heatmap & Radar -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="12">
        <div class="glass-card chart-card">
          <div class="card-header">
            <div class="title-group">
              <span class="icon">🔥</span>
              <span>订单热力图（星期 × 小时）</span>
            </div>
            <el-tooltip content="展示各时段的订单密度" placement="top">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          <div ref="heatmapChartRef" class="chart-md"></div>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="glass-card chart-card">
          <div class="card-header">
            <div class="title-group">
              <span class="icon">🧭</span>
              <span>全校口味雷达</span>
            </div>
            <el-tooltip content="展示全校师生的口味偏好分布" placement="top">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          <div ref="radarChartRef" class="chart-md"></div>
        </div>
      </el-col>
    </el-row>
    
    <!-- Row 3: Pie & Top Users -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="8">
        <div class="glass-card chart-card">
          <div class="card-header">
            <div class="title-group">
              <span class="icon">🍰</span>
              <span>菜品分类占比</span>
            </div>
            <el-tooltip content="展示各菜品分类的销售占比" placement="top">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          <div ref="pieChartRef" class="chart-md"></div>
        </div>
      </el-col>
      
      <el-col :span="16">
        <div class="glass-card chart-card">
          <div class="card-header">
            <div class="title-group">
              <span class="icon">⚡</span>
              <span>人均热量摄入趋势（7天）</span>
            </div>
            <el-tooltip content="展示近7天的人均热量摄入变化" placement="top">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          <div ref="funnelChartRef" class="chart-md"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Row 4: Traffic Prediction -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="24">
        <div class="glass-card chart-card">
          <div class="card-header">
            <div class="title-group">
              <span class="icon">🔮</span>
              <span>全天人流量预测（基于历史同期）</span>
            </div>
            <el-tooltip content="基于过去30天数据预测的今日分时人流量" placement="top">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          <div ref="trafficChartRef" class="chart-md"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Row 5: Procurement Guidance -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="24">
        <div class="glass-card chart-card">
          <div class="card-header">
            <div class="title-group">
              <span class="icon">🥬</span>
              <span>原材料采购指导（基于销量预测）</span>
            </div>
            <el-tooltip content="基于近7天销量预测的明日原材料需求量" placement="top">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          <div ref="procurementChartRef" class="chart-md"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { InfoFilled, Download, Top, Bottom, Money, User, Goods, Timer } from '@element-plus/icons-vue'
import api from '../api'

const trendChartRef = ref(null)
const revenueChartRef = ref(null)
const radarChartRef = ref(null)
const heatmapChartRef = ref(null)
const pieChartRef = ref(null)
const funnelChartRef = ref(null)
const trafficChartRef = ref(null)
const procurementChartRef = ref(null)
const loading = ref(true)

// Mock Quick Stats
const quickStats = ref([
  { label: '今日订单', value: '1,284', icon: 'Goods', type: 'primary', trend: 12.5 },
  { label: '今日营收', value: '¥15,230', icon: 'Money', type: 'success', trend: 8.2 },
  { label: '活跃用户', value: '856', icon: 'User', type: 'warning', trend: -2.4 },
  { label: '平均耗时', value: '12min', icon: 'Timer', type: 'info', trend: -5.1 },
])

const initTrendChart = async () => {
  const chart = echarts.init(trendChartRef.value)
  const res = await api.get('/admin/analytics/sales_trend')
  chart.setOption({
    tooltip: { 
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#1e293b' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: res.data.dates, 
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: { 
      type: 'value', 
      name: '订单量',
      splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } }
    },
    series: [{
      data: res.data.counts,
      type: 'line',
      smooth: true,
      symbolSize: 8,
      lineStyle: { width: 4, color: '#6366f1' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(99, 102, 241, 0.5)' },
          { offset: 1, color: 'rgba(99, 102, 241, 0.05)' }
        ])
      },
      itemStyle: { color: '#6366f1', borderWidth: 2, borderColor: '#fff' }
    }]
  })
}

const initRevenueChart = async () => {
  const chart = echarts.init(revenueChartRef.value)
  const res = await api.get('/admin/analytics/revenue')
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: res.data.dates,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: { 
      type: 'value', 
      name: '营收(元)',
      splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } }
    },
    series: [{
      data: res.data.values,
      type: 'bar',
      barWidth: '40%',
      itemStyle: { 
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#10b981' },
          { offset: 1, color: '#34d399' }
        ]),
        borderRadius: [6, 6, 0, 0] 
      }
    }]
  })
}

const initPieChart = async () => {
  const chart = echarts.init(pieChartRef.value)
  const res = await api.get('/admin/analytics/category_share')
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: '0%', left: 'center', icon: 'circle' },
    series: [{
      name: '销售占比',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '38%'],
      avoidLabelOverlap: false,
      itemStyle: { 
        borderRadius: 10, 
        borderColor: '#fff', 
        borderWidth: 2 
      },
      label: { show: false, position: 'center' },
      emphasis: { 
        label: { show: true, fontSize: 20, fontWeight: 'bold', color: '#1e293b' },
        scale: true,
        scaleSize: 10
      },
      data: res.data
    }],
    color: ['#6366f1', '#ec4899', '#8b5cf6', '#10b981', '#f59e0b']
  })
}

const initHeatmapChart = async () => {
  const chart = echarts.init(heatmapChartRef.value)
  const res = await api.get('/admin/analytics/heatmap')
  const hours = Array.from({length: 24}, (_, i) => i + '点')
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  
  chart.setOption({
    tooltip: { position: 'top' },
    grid: { height: '60%', top: '5%', bottom: '25%' },
    xAxis: { type: 'category', data: hours, splitArea: { show: true } },
    yAxis: { type: 'category', data: days, splitArea: { show: true } },
    visualMap: {
      min: 0,
      max: 500, 
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: { 
        color: ['#f1f5f9', '#67e8f9', '#4ade80', '#facc15', '#fb923c', '#f43f5e'] // Cool to Hot: Slate -> Cyan -> Green -> Yellow -> Orange -> Red
      }
    },
    series: [{
      type: 'heatmap',
      data: res.data,
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } },
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 1 }
    }]
  })
}

const initRadarChart = async () => {
  const chart = echarts.init(radarChartRef.value)
  const res = await api.get('/admin/analytics/user_radar')
  chart.setOption({
    tooltip: {},
    radar: {
      indicator: res.data.indicators,
      shape: 'circle',
      splitNumber: 4,
      axisName: { color: '#64748b', fontWeight: 'bold' },
      splitLine: { lineStyle: { color: '#e2e8f0' } },
      splitArea: {
        areaStyle: {
          color: ['#f8fafc', '#f1f5f9', '#e2e8f0', '#cbd5e1'],
          shadowColor: 'rgba(0, 0, 0, 0.1)',
          shadowBlur: 10
        }
      }
    },
    series: [{
      name: '口味偏好',
      type: 'radar',
      data: [{
        value: res.data.values,
        name: '全校统计',
        areaStyle: { color: 'rgba(245, 158, 11, 0.4)' },
        itemStyle: { color: '#f59e0b' },
        lineStyle: { width: 3 }
      }]
    }]
  })
}

const initCalorieTrendChart = async () => {
  const chart = echarts.init(funnelChartRef.value)
  const res = await api.get('/admin/analytics/calories_trend')
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: res.data.dates, boundaryGap: false },
    yAxis: { type: 'value', name: '千卡(kcal)', splitLine: { lineStyle: { type: 'dashed' } } },
    series: [{
      data: res.data.values,
      type: 'line',
      smooth: true,
      lineStyle: { width: 4, color: '#f59e0b' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(245, 158, 11, 0.5)' },
          { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }
        ])
      },
      itemStyle: { color: '#f59e0b', borderWidth: 2, borderColor: '#fff' }
    }]
  })
}

const initTrafficChart = async () => {
  const chart = echarts.init(trafficChartRef.value)
  const res = await api.get('/admin/analytics/traffic_prediction')
  
  const currentHour = new Date().getHours()
  const currentHourStr = `${currentHour}点`
  const fullData = res.data.predicted_traffic
  
  // Split data into two series
  // Series 1: 0 to currentHour (Past/Current)
  const pastData = fullData.map((val, idx) => idx <= currentHour ? val : null)
  // Series 2: currentHour to 23 (Future) - Start from currentHour to connect lines
  const futureData = fullData.map((val, idx) => idx >= currentHour ? val : null)
  
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: res.data.hours,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: { 
      type: 'value', 
      name: '预测人次',
      splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } }
    },
    series: [
      {
        name: '已发生',
        data: pastData,
        type: 'line',
        smooth: true,
        lineStyle: { width: 4, color: '#94a3b8' }, // Grey
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(148, 163, 184, 0.5)' },
            { offset: 1, color: 'rgba(148, 163, 184, 0.05)' }
          ])
        },
        itemStyle: { color: '#94a3b8', borderWidth: 2, borderColor: '#fff' },
        symbol: 'none'
      },
      {
        name: '预测',
        data: futureData,
        type: 'line',
        smooth: true,
        lineStyle: { width: 4, color: '#8b5cf6', type: 'dashed' }, // Purple dashed
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(139, 92, 246, 0.5)' },
            { offset: 1, color: 'rgba(139, 92, 246, 0.05)' }
          ])
        },
        itemStyle: { color: '#8b5cf6', borderWidth: 2, borderColor: '#fff' },
        markLine: {
          symbol: ['none', 'none'],
          label: { show: true, position: 'end', formatter: '当前' },
          lineStyle: { color: '#ef4444', type: 'dashed', width: 2 },
          data: [
            { xAxis: currentHourStr }
          ]
        }
      }
    ]
  })
}

const initProcurementChart = async () => {
  const chart = echarts.init(procurementChartRef.value)
  const res = await api.get('/admin/analytics/procurement_guidance')
  
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '需求量(kg)',
      boundaryGap: [0, 0.01],
      splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } }
    },
    yAxis: {
      type: 'category',
      data: res.data.ingredients,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    series: [
      {
        name: '预计需求',
        type: 'bar',
        data: res.data.quantities,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: '#06b6d4' }, // Cyan
            { offset: 1, color: '#22d3ee' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c} kg'
        }
      }
    ]
  })
}

onMounted(async () => {
  // Initialize all charts in parallel to sync animations
  loading.value = true
  try {
    // Use Promise.all to fetch data and render charts concurrently
    // The v-loading mask hides the sequential rendering
    await Promise.all([
      initTrendChart(),
      initRevenueChart(),
      initPieChart(),
      initHeatmapChart(),
      initRadarChart(),
      initCalorieTrendChart(),
      initTrafficChart(),
      initProcurementChart()
    ])
  } catch (error) {
    console.error('Failed to load charts:', error)
  } finally {
    // Small delay to ensure DOM is fully painted before removing mask
    setTimeout(() => {
      loading.value = false
    }, 300)
  }
  
  // Resize charts on window resize
  window.addEventListener('resize', () => {
    [trendChartRef, revenueChartRef, pieChartRef, heatmapChartRef, radarChartRef, funnelChartRef, trafficChartRef, procurementChartRef].forEach(ref => {
      if (ref.value) echarts.getInstanceByDom(ref.value)?.resize()
    })
  })
})
</script>

<style scoped>
.admin-container {
  padding-bottom: 40px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 30px;
  padding: 0 10px;
}

.dashboard-header h1 {
  margin: 0 0 8px 0;
  font-size: 2.2rem;
  font-weight: 800;
  background: linear-gradient(to right, var(--text-primary), var(--primary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dashboard-header p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 1rem;
}

.mr-1 { margin-right: 4px; }

/* Quick Stats */
.stats-row {
  margin-bottom: 30px;
}

.stat-card {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) backwards;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.primary { background: rgba(99, 102, 241, 0.1); color: var(--primary-color); }
.stat-icon.success { background: rgba(16, 185, 129, 0.1); color: var(--success-color); }
.stat-icon.warning { background: rgba(245, 158, 11, 0.1); color: var(--warning-color); }
.stat-icon.info { background: rgba(59, 130, 246, 0.1); color: var(--info-color); }

.stat-info {
  flex-grow: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1.2;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat-trend {
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 2px;
}

.stat-trend.up { color: var(--success-color); }
.stat-trend.down { color: var(--danger-color); }

/* Charts */
.chart-row {
  margin-bottom: 24px;
}

.chart-card {
  padding: 24px;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) backwards;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.title-group .icon {
  font-size: 1.2rem;
}

.info-icon {
  color: var(--text-light);
  cursor: help;
  transition: color 0.2s;
}

.info-icon:hover {
  color: var(--primary-color);
}

.chart-lg {
  height: 360px;
  width: 100%;
}

.chart-md {
  height: 320px;
  width: 100%;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
