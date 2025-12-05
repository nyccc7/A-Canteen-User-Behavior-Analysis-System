<template>
  <div class="student-container">
    <!-- Header & User Selector -->
    <div class="header-section glass-card">
      <div class="user-info">
        <el-avatar :size="50" :src="'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'" />
        <div class="user-details">
          <h2>欢迎回来, {{ currentUserName }}</h2>
          <p class="user-pref">偏好: {{ userPrefString }}</p>
        </div>
      </div>
      
      <div class="user-actions">
        <span class="label">切换演示用户:</span>
        <el-select v-model="userId" placeholder="选择用户" style="width: 200px">
          <el-option
            v-for="user in demoUsers"
            :key="user.id"
            :label="user.username"
            :value="user.id"
          >
            <span style="float: left">{{ user.username }}</span>
            <span style="float: right; color: #8492a6; font-size: 13px">{{ getUserTag(user) }}</span>
          </el-option>
        </el-select>
        
        <!-- Clear History Button (only for interactive user) -->
        <el-button 
          v-if="isInteractiveUser" 
          type="danger" 
          size="small" 
          @click="confirmClearHistory"
          style="margin-left: 10px"
        >
          🗑️ 清空历史
        </el-button>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <el-tabs v-model="activeTab" class="main-tabs glass-card">
      <!-- Tab 1: Menu & Recommendations -->
      <el-tab-pane label="🍽️ 点餐 & 推荐" name="menu">
        <div class="tab-content">
          <!-- Recommendations (8 items) -->
          <div class="section-title">✨ 今日为您推荐</div>
          <el-row :gutter="20" style="flex-wrap: wrap">
            <el-col :span="6" v-for="dish in recommendations.slice(0, 8)" :key="dish._id" style="margin-bottom: 20px">
              <el-card class="dish-card" :body-style="{ padding: '0px' }" shadow="hover">
                <div class="dish-image-placeholder" :style="{ background: getDishColor(dish.category) }">
                  {{ dish.category }}
                </div>
                <div class="dish-info">
                  <div class="dish-name">{{ dish.name }}</div>
                  <div class="dish-meta" style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 12px; color: #909399;">
                    <span>{{ dish.category }}</span>
                    <span>🔥 {{ dish.calories }} kcal</span>
                  </div>
                  <div class="dish-tags">
                    <el-tag v-for="tag in dish.tags.slice(0,2)" :key="tag" size="small" effect="plain">{{ tag }}</el-tag>
                  </div>
                  <div class="dish-bottom">
                    <span class="price">¥{{ dish.price }}</span>
                    <el-button type="primary" size="small" round @click="addToCart(dish)">加入购物车</el-button>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- All Dishes -->
          <div class="section-title" style="margin-top: 20px">📋 完整菜单</div>
          <el-table :data="dishes" style="width: 100%">
            <el-table-column prop="name" label="菜名" width="180">
              <template #default="{ row }">
                <span style="font-weight: bold">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="100">
                <template #default="scope">¥{{ scope.row.price }}</template>
            </el-table-column>
            <el-table-column prop="calories" label="热量" width="100">
                <template #default="scope">🔥 {{ scope.row.calories }}</template>
            </el-table-column>
            <el-table-column label="标签">
              <template #default="scope">
                <el-tag v-for="tag in scope.row.tags" :key="tag" size="small" style="margin-right: 5px" type="info">{{ tag }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" align="right">
              <template #default="scope">
                <el-button size="small" type="primary" @click="addToCart(scope.row)">加入购物车</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- Tab 2: Order History -->
      <el-tab-pane label="📜 历史 & 偏好" name="history">
        <div class="tab-content">
          
          <!-- Personal TOP 10 Section -->
          <div class="section-title">🏆 您的年度最爱 TOP 3</div>
          <el-empty v-if="top10Dishes.length === 0" description="多点几单，生成您的专属榜单！" />
          <div v-else class="top10-container">
            <div v-for="(dish, index) in top10Dishes.slice(0, 3)" :key="dish._id" class="top10-item">
              <div class="rank-badge" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
              <div class="dish-details">
                <div class="name">{{ dish.name }}</div>
                <div class="tags">
                  <el-tag size="small" type="info">{{ dish.category }}</el-tag>
                </div>
              </div>
              <el-button type="primary" size="small" @click="addToCart(dish)">再来一份</el-button>
            </div>
          </div>

          <el-divider />

          <!-- Order History -->
          <div class="section-title">🕒 最近订单</div>
          <el-empty v-if="orderHistory.length === 0" description="暂无历史订单" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="(activity, index) in orderHistory"
              :key="index"
              :timestamp="formatTime(activity.timestamp)"
              placement="top"
              :type="index === 0 ? 'primary' : ''"
            >
              <el-card class="history-card">
                <h4>{{ activity.dish_name }}</h4>
                <p>消费: ¥{{ activity.price }} | 分类: {{ activity.category }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Floating Cart Button -->
    <div class="cart-float-btn" @click="cartVisible = true">
      <el-badge :value="cart.length" class="item" :hidden="cart.length === 0">
        <el-button type="primary" circle size="large" class="cart-btn-inner">
          <el-icon :size="24"><ShoppingCart /></el-icon>
        </el-button>
      </el-badge>
    </div>

    <!-- Cart Dialog -->
    <el-dialog v-model="cartVisible" title="🛒 购物车结算" width="500px">
      <div v-if="cart.length === 0" class="empty-cart">
        购物车是空的，快去选购吧！
      </div>
      <div v-else>
        <TransitionGroup name="list" tag="div">
          <div v-for="(item, index) in cart" :key="item._id + '_' + index" class="cart-item">
            <div class="cart-item-info">
              <span class="name">{{ item.name }}</span>
              <span class="price">¥{{ item.price }}</span>
            </div>
            <el-button type="danger" link @click="removeFromCart(index)">移除</el-button>
          </div>
        </TransitionGroup>
        <div class="cart-total">
          <span>总计:</span>
          <span class="total-price">¥{{ cartTotal }}</span>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cartVisible = false">继续点餐</el-button>
          <el-button type="primary" @click="checkout" :disabled="cart.length === 0" :loading="checkoutLoading">
            确认下单
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Floating AI Nutritionist Button -->
    <div class="ai-float-btn" @click="openAIChat">
      <el-button type="success" circle size="large" class="ai-btn-inner">
        <el-icon :size="24"><ChatDotRound /></el-icon>
      </el-button>
    </div>

    <!-- AI Chat Dialog -->
    <el-dialog v-model="aiChatVisible" title="🤖 AI 营养师" width="400px" custom-class="ai-chat-dialog">
      <div class="chat-container">
        <div class="chat-messages" ref="chatMessagesRef">
          <div v-for="(msg, index) in chatHistory" :key="index" class="message" :class="msg.role">
            <div class="message-content">{{ msg.content }}</div>
          </div>
          <div v-if="aiLoading" class="message ai">
            <div class="message-content">
              <span class="typing-dot">.</span><span class="typing-dot">.</span><span class="typing-dot">.</span>
            </div>
          </div>
        </div>
        <div class="chat-input">
          <el-input 
            v-model="chatInput" 
            placeholder="问问营养师..." 
            @keyup.enter="sendChatMessage"
            :disabled="aiLoading"
          >
            <template #append>
              <el-button @click="sendChatMessage" :loading="aiLoading">发送</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, shallowRef } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { ShoppingCart, ChatDotRound } from '@element-plus/icons-vue'
import api from '../api'

const userId = ref('')
const demoUsers = ref([])
const dishes = shallowRef([]) // Optimization: shallowRef for large list
const recommendations = shallowRef([])
const top10Dishes = shallowRef([])
const orderHistory = ref([])
const activeTab = ref('menu')

// Cart State
const cart = ref([])
const cartVisible = ref(false)
const checkoutLoading = ref(false)

const cartTotal = computed(() => {
  return cart.value.reduce((sum, item) => sum + item.price, 0)
})

const currentUserName = computed(() => {
  const u = demoUsers.value.find(u => u.id === userId.value)
  return u ? u.username : '加载中...'
})

const userPrefString = computed(() => {
  const u = demoUsers.value.find(u => u.id === userId.value)
  if (!u) return '无'
  // Use dynamic tags if available, otherwise preferences
  if (u.dynamic_tags && u.dynamic_tags.length > 0) {
    return u.dynamic_tags.join(', ')
  }
  if (u.preferences) {
    return Object.keys(u.preferences).join(', ')
  }
  return '无'
})

const isInteractiveUser = computed(() => {
  const u = demoUsers.value.find(u => u.id === userId.value)
  return u?.username === 'demo_interactive'
})

const getUserTag = (user) => {
  if (user.username.includes('spicy')) return '🌶️ 辣党'
  if (user.username.includes('sweet')) return '🍬 甜党'
  if (user.username.includes('veg')) return '🥗 素食'
  if (user.username.includes('interactive')) return '🎮 互动'
  return '👤 普通'
}

const getDishColor = (cat) => {
  const colors = {
    '川菜': '#ff7675', '本帮菜': '#fdcb6e', '素菜': '#55efc4',
    '粤菜': '#74b9ff', '面食': '#a29bfe', '饮品': '#fab1a0'
  }
  return colors[cat] || '#dfe6e9'
}

const formatTime = (isoStr) => {
  return new Date(isoStr).toLocaleString()
}

const fetchDemoUsers = async () => {
  try {
    const res = await api.get('/student/users')
    demoUsers.value = res.data
    if (demoUsers.value.length > 0 && !userId.value) {
      userId.value = demoUsers.value[0].id
    }
  } catch (e) { console.error(e) }
}

// Watch userId change to refetch data
watch(userId, (newVal) => {
  if (newVal) {
    fetchRecommendations()
    fetchTop10()
    fetchHistory()
    // Reset Chat
    chatHistory.value = [
      { role: 'ai', content: '你好！我是智慧食堂的AI营养师。我可以为您推荐健康菜品，或者解答关于热量、营养搭配的问题。' }
    ]
    ElMessage.success('已切换用户')
  }
})

const fetchDishes = async () => {
  const res = await api.get('/portal/dishes')
  dishes.value = res.data
}

const fetchRecommendations = async () => {
  if (!userId.value) return
  const res = await api.get(`/recommend/recommend/${userId.value}`)
  recommendations.value = res.data
}

const fetchTop10 = async () => {
  if (!userId.value) return
  const res = await api.get(`/recommend/top10/${userId.value}`)
  top10Dishes.value = res.data
}

const fetchHistory = async () => {
  if (!userId.value) return
  const res = await api.get(`/student/history/${userId.value}`)
  orderHistory.value = res.data
}

// Cart Logic
const addToCart = (dish) => {
  cart.value.push(dish)
  ElNotification({
    title: '已加入购物车',
    message: `${dish.name} - ¥${dish.price}`,
    type: 'success',
    duration: 2000
  })
}

const removeFromCart = (index) => {
  cart.value.splice(index, 1)
}

const checkout = async () => {
  if (!userId.value) {
    ElMessage.warning('请先选择用户')
    return
  }
  
  checkoutLoading.value = true
  try {
    // Simulate bulk order by looping (in real app, use bulk API)
    for (const item of cart.value) {
      await api.post('/portal/order', {
        user_id: userId.value,
        dish_id: item._id
      })
    }
    
    ElMessage.success(`下单成功！共消费 ¥${cartTotal.value}`)
    cart.value = []
    cartVisible.value = false
    fetchHistory() // Refresh history
    fetchRecommendations() // Refresh recommendations
    fetchTop10() // Refresh Top 10
    fetchDemoUsers() // Refresh user tags to show updated preferences
  } catch (e) {
    ElMessage.error('下单失败，请重试')
  } finally {
    checkoutLoading.value = false
  }
}

const confirmClearHistory = () => {
  ElMessageBox.confirm(
    '确定要清空所有历史订单吗？此操作不可恢复，但您可以重新开始体验个性化推荐。',
    '⚠️ 警告',
    {
      confirmButtonText: '确定清空',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    clearHistory()
  }).catch(() => {
    ElMessage.info('已取消清空操作')
  })
}

// AI Chat Logic
const aiChatVisible = ref(false)
const chatInput = ref('')
const chatHistory = ref([
  { role: 'ai', content: '你好！我是智慧食堂的AI营养师。我可以为您推荐健康菜品，或者解答关于热量、营养搭配的问题。' }
])
const aiLoading = ref(false)
const chatMessagesRef = ref(null)

const openAIChat = () => {
  aiChatVisible.value = true
  scrollToBottom()
}

const scrollToBottom = () => {
  setTimeout(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  }, 100)
}

const sendChatMessage = async () => {
  if (!chatInput.value.trim() || aiLoading.value) return
  
  const userMsg = chatInput.value
  chatHistory.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  scrollToBottom()
  
  aiLoading.value = true
  try {
    const res = await api.post('/student/chat', {
      message: userMsg,
      history: [], // Simplify for now
      user_id: userId.value // Pass user ID for personalized recommendations
    })
    
    chatHistory.value.push({ role: 'ai', content: res.data.reply })
  } catch (e) {
    chatHistory.value.push({ role: 'ai', content: '抱歉，我现在有点忙，请稍后再试。' })
  } finally {
    aiLoading.value = false
    scrollToBottom()
  }
}

const clearHistory = async () => {
  try {
    const res = await api.delete(`/student/history/${userId.value}`)
    ElMessage.success(res.data.message || '历史已清空！现在可以点餐体验个性化推荐了')
    // Refresh all relevant data
    fetchHistory()
    fetchRecommendations()
    fetchTop10()
    fetchDemoUsers() // Update user tags
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '清空失败，请重试')
  }
}

onMounted(() => {
  fetchDemoUsers()
  fetchDishes()
})
</script>

<style scoped>
.student-container {
  padding: 0 20px;
  padding-bottom: 80px; /* Space for floating button */
}

.glass-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-details h2 {
  margin: 0 0 5px 0;
  font-size: 1.5rem;
}

.user-pref {
  margin: 0;
  color: #606266;
  font-size: 0.9rem;
}

.user-actions .label {
  margin-right: 10px;
  color: #606266;
}

.section-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 20px;
  border-left: 4px solid #409eff;
  padding-left: 10px;
}

.dish-card {
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s;
  border: none;
}

.dish-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.dish-image-placeholder {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.dish-info {
  padding: 15px;
}

.dish-name {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 8px;
}

.dish-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
}

.price {
  color: #f56c6c;
  font-weight: bold;
  font-size: 1.2rem;
}

.history-card {
  border-radius: 8px;
}

.history-card h4 {
  margin: 0 0 5px 0;
}

.history-card p {
  margin: 0;
  color: #909399;
  font-size: 0.9rem;
}

/* Top 10 Styles */
.top10-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.top10-item {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 12px;
  transition: transform 0.2s;
}

.top10-item:hover {
  transform: scale(1.02);
  background: #ecf5ff;
}

.rank-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e4e7ed;
  color: #606266;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 15px;
  flex-shrink: 0;
}

.rank-1 { background: #f56c6c; color: white; box-shadow: 0 2px 8px rgba(245, 108, 108, 0.4); }
.rank-2 { background: #e6a23c; color: white; box-shadow: 0 2px 8px rgba(230, 162, 60, 0.4); }
.rank-3 { background: #409eff; color: white; box-shadow: 0 2px 8px rgba(64, 158, 255, 0.4); }

.dish-details {
  flex-grow: 1;
}

.dish-details .name {
  font-weight: bold;
  margin-bottom: 4px;
}

/* Cart Styles */
.cart-float-btn {
  position: fixed;
  bottom: 40px;
  right: 40px;
  z-index: 1000;
  cursor: pointer;
}

.cart-btn-inner {
  width: 60px;
  height: 60px;
  font-size: 24px;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.4);
}

.ai-float-btn {
  position: fixed;
  bottom: 110px;
  right: 40px;
  z-index: 1000;
  cursor: pointer;
}

.ai-btn-inner {
  width: 60px;
  height: 60px;
  font-size: 24px;
  box-shadow: 0 4px 20px rgba(103, 194, 58, 0.4);
}

.chat-container {
  height: 400px;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 10px;
}

.message {
  margin-bottom: 10px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.ai {
  justify-content: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 0.9rem;
  line-height: 1.4;
}

.message.user .message-content {
  background: #409eff;
  color: white;
  border-bottom-right-radius: 2px;
}

.message.ai .message-content {
  background: white;
  color: #303133;
  border: 1px solid #e4e7ed;
  border-bottom-left-radius: 2px;
}

.typing-dot {
  animation: typing 1.4s infinite ease-in-out both;
  margin: 0 1px;
  display: inline-block;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.cart-item-info {
  display: flex;
  flex-direction: column;
}

.cart-item-info .name {
  font-weight: bold;
}

.cart-item-info .price {
  color: #f56c6c;
  font-size: 0.9rem;
}

.cart-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  font-size: 1.2rem;
  font-weight: bold;
}

.total-price {
  color: #f56c6c;
  font-size: 1.5rem;
}

.empty-cart {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}

/* Animations */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.list-leave-active {
  position: absolute;
  width: 100%;
}

.el-button:active {
  transform: scale(0.95);
}

.dish-card {
  animation: fadeIn 0.5s ease-out backwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
