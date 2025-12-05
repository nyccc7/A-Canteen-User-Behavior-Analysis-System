<template>
  <div class="common-layout">
    <div class="animated-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>
    
    <el-container class="main-container">
      <el-header class="glass-header" :class="{ 'scrolled': isScrolled }">
        <div class="logo-container" @click="router.push('/')">
          <div class="logo-icon-wrapper">
            <div class="logo-icon">🍱</div>
          </div>
          <div class="logo-text">
            <span class="brand">Smart</span>
            <span class="highlight">Cafeteria</span>
          </div>
        </div>
        
        <el-menu 
          :default-active="activeIndex" 
          mode="horizontal" 
          router 
          class="nav-menu"
          :ellipsis="false"
        >
          <el-menu-item index="/">
            <template #title>
              <div class="menu-icon-wrapper"><el-icon><HomeFilled /></el-icon></div>
              <span>门户首页</span>
            </template>
          </el-menu-item>
          <el-menu-item index="/student">
            <template #title>
              <div class="menu-icon-wrapper"><el-icon><Food /></el-icon></div>
              <span>学生点餐</span>
            </template>
          </el-menu-item>
          <el-menu-item index="/admin">
            <template #title>
              <div class="menu-icon-wrapper"><el-icon><DataLine /></el-icon></div>
              <span>数据大屏</span>
            </template>
          </el-menu-item>
        </el-menu>
        
        <div class="header-actions">
          <el-avatar :size="36" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="page-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled, Food, DataLine } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const activeIndex = ref(route.path)
const isScrolled = ref(false)

watch(route, (newRoute) => {
  activeIndex.value = newRoute.path
})

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
  /* Modern Palette */
  --primary-color: #6366f1; /* Indigo 500 */
  --primary-light: #818cf8;
  --primary-dark: #4f46e5;
  --secondary-color: #ec4899; /* Pink 500 */
  --accent-color: #8b5cf6; /* Violet 500 */
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --info-color: #3b82f6;
  
  /* Text */
  --text-primary: #1e293b; /* Slate 800 */
  --text-secondary: #64748b; /* Slate 500 */
  --text-light: #94a3b8;
  
  /* Glassmorphism */
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: rgba(255, 255, 255, 0.5);
  --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
  --glass-blur: blur(12px);
  
  /* Layout */
  --header-height: 70px;
  --border-radius-lg: 24px;
  --border-radius-md: 16px;
  --border-radius-sm: 12px;
}

body {
  margin: 0;
  font-family: 'Outfit', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: var(--text-primary);
  overflow-x: hidden;
  background-color: #f8fafc;
}

.common-layout {
  position: relative;
  min-height: 100vh;
}

/* Enhanced Animated Background */
.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  background: #f0f9ff;
  overflow: hidden;
}

.blob {
  position: absolute;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 20s infinite alternate;
}

.blob-1 {
  top: -10%;
  left: -10%;
  width: 50vw;
  height: 50vw;
  background: radial-gradient(circle, var(--primary-light), transparent);
  animation-delay: 0s;
}

.blob-2 {
  bottom: -10%;
  right: -10%;
  width: 60vw;
  height: 60vw;
  background: radial-gradient(circle, var(--secondary-color), transparent);
  animation-delay: -5s;
}

.blob-3 {
  top: 40%;
  left: 40%;
  width: 40vw;
  height: 40vw;
  background: radial-gradient(circle, var(--success-color), transparent);
  animation-delay: -10s;
  opacity: 0.4;
}

@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  100% { transform: translate(50px, 50px) rotate(20deg); }
}

.main-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Modern Glass Header */
.glass-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  height: var(--header-height) !important;
  padding: 0 40px !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  background: transparent;
}

.glass-header.scrolled {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-bottom: 1px solid var(--glass-border);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: transform 0.3s ease;
  flex: 1; /* Occupy left space */
}

.logo-container:hover {
  transform: scale(1.02);
}

.logo-icon-wrapper {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.logo-text .brand {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 3px;
  text-transform: uppercase;
}

.logo-text .highlight {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(to right, var(--text-primary), var(--primary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Navigation */
.nav-menu {
  background: transparent !important;
  border: none !important;
  /* flex-grow: 1; Removed to allow centering */
  justify-content: center;
  height: 100%;
  align-items: center;
  flex: 0 0 auto; /* Do not grow, auto width */
}

.nav-menu .el-menu-item {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary) !important;
  border-radius: 12px;
  margin: 0 8px;
  height: 48px !important;
  line-height: 48px !important;
  padding: 0 20px !important;
  transition: all 0.3s ease !important;
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.nav-menu .el-menu-item:hover {
  background: rgba(99, 102, 241, 0.08) !important;
  color: var(--primary-color) !important;
}

.nav-menu .el-menu-item:hover .menu-icon-wrapper {
  transform: translateY(-2px);
}

.nav-menu .el-menu-item.is-active {
  background: var(--primary-color) !important;
  color: white !important;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

.nav-menu .el-menu-item.is-active .menu-icon-wrapper {
  color: white;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1; /* Occupy right space */
  justify-content: flex-end; /* Align content to the right */
}

.main-content {
  padding: 20px 40px 40px !important;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* Page Transitions */
.page-slide-enter-active,
.page-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
  filter: blur(8px);
}

.page-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
  filter: blur(8px);
}

/* Global Utility Classes */
.glass-card {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: var(--glass-blur) !important;
  -webkit-backdrop-filter: var(--glass-blur) !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--glass-shadow) !important;
  border-radius: var(--border-radius-lg) !important;
  transition: all 0.3s ease !important;
}

.glass-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08) !important;
  background: rgba(255, 255, 255, 0.9) !important;
}

/* Element Plus Overrides */
.el-card {
  border: none !important;
  background: transparent !important;
}

.el-button--primary {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)) !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.el-button--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .glass-header {
    padding: 0 15px !important;
    height: 60px !important;
  }
  
  .logo-text .brand {
    display: none;
  }
  
  .logo-text .highlight {
    font-size: 18px;
  }
  
  .logo-icon-wrapper {
    width: 36px;
    height: 36px;
  }
  
  .logo-icon {
    font-size: 20px;
  }
  
  .nav-menu .el-menu-item {
    padding: 0 10px !important;
    margin: 0 2px;
  }
  
  .nav-menu .el-menu-item span {
    display: none; /* Hide text on mobile */
  }
  
  .main-content {
    padding: 15px !important;
  }
  
  .header-actions {
    gap: 8px;
  }
}
</style>
