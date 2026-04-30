<template>
  <div class="chat-page">
    <el-row :gutter="20" class="chat-container">
      <!-- 左侧知识库选择 -->
      <el-col :span="6" class="sidebar">
        <el-card>
          <template #header>
            <span>选择知识库</span>
          </template>
          <el-checkbox-group v-model="selectedKbIds">
            <div v-for="kb in knowledgeStore.knowledgeBases" :key="kb.id" class="kb-item">
              <el-checkbox :label="kb.id">
                {{ kb.name }}
                <el-tag size="small" style="margin-left: 8px;">{{ kb.document_count }} 文档</el-tag>
              </el-checkbox>
            </div>
          </el-checkbox-group>
          <el-empty v-if="knowledgeStore.knowledgeBases.length === 0" description="暂无知识库" />
        </el-card>
        
        <el-card class="history-card">
          <template #header>
            <span>对话历史</span>
          </template>
          <div v-if="chatHistories.length === 0" class="empty-history">
            暂无历史记录
          </div>
          <div v-else class="history-list">
            <div
              v-for="history in chatHistories"
              :key="history.id"
              class="history-item"
              @click="loadHistory(history)"
            >
              {{ history.title }}
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧聊天区域 -->
      <el-col :span="18" class="chat-main">
        <el-card class="chat-card">
          <div ref="messagesContainer" class="messages-container">
            <div v-if="messages.length === 0" class="empty-chat">
              <el-empty description="开始一个新对话吧！" />
            </div>
            <ChatMessageComp
              v-for="(msg, index) in messages"
              :key="index"
              :message="msg"
              :timestamp="msg.timestamp"
            />
            <div v-if="loading" class="loading-message">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>AI 正在思考...</span>
            </div>
          </div>
          
          <div class="input-container">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="3"
              placeholder="输入您的问题..."
              :disabled="loading"
              @keydown.enter.ctrl="sendMessage"
            />
            <div class="input-actions">
              <el-button
                type="primary"
                :loading="loading"
                :disabled="!inputMessage.trim()"
                @click="sendMessage"
              >
                <el-icon><Promotion /></el-icon>
                发送
              </el-button>
              <el-button @click="clearChat">清空对话</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useKnowledgeStore } from '@/stores/knowledge'
import { chatApi, type ChatMessage as ChatMessageType } from '@/api/chat'
import { ElMessage } from 'element-plus'
import ChatMessageComp from '@/components/ChatMessage.vue'

interface MessageWithTimestamp extends ChatMessageType {
  timestamp?: string
}

const knowledgeStore = useKnowledgeStore()

const messages = ref<MessageWithTimestamp[]>([])
const inputMessage = ref('')
const selectedKbIds = ref<number[]>([])
const loading = ref(false)
const messagesContainer = ref<HTMLElement>()
const chatHistories = ref<{ id: string; title: string; messages: MessageWithTimestamp[] }[]>([])

async function sendMessage() {
  if (!inputMessage.value.trim() || loading.value) return
  
  const userMessage: MessageWithTimestamp = {
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date().toISOString(),
  }
  
  messages.value.push(userMessage)
  const question = inputMessage.value.trim()
  inputMessage.value = ''
  
  loading.value = true
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  try {
    const response = await chatApi.sendMessage({
      messages: messages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content })),
      knowledge_base_ids: selectedKbIds.value,
    })
    
    const assistantMessage: MessageWithTimestamp = {
      role: 'assistant',
      content: response.choices[0].message.content,
      timestamp: new Date().toISOString(),
    }
    
    messages.value.push(assistantMessage)
    
    // 更新对话历史标题
    if (messages.value.length === 2) {
      const title = question.slice(0, 20) + (question.length > 20 ? '...' : '')
      chatHistories.value.unshift({
        id: Date.now().toString(),
        title,
        messages: [...messages.value],
      })
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '发送消息失败')
    // 移除用户消息
    messages.value.pop()
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function clearChat() {
  messages.value = []
}

function loadHistory(history: { id: string; title: string; messages: MessageWithTimestamp[] }) {
  messages.value = [...history.messages]
}

onMounted(() => {
  knowledgeStore.fetchKnowledgeBases()
})
</script>

<style scoped>
.chat-page {
  height: 100%;
}

.chat-container {
  height: 100%;
}

.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.kb-item {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.kb-item:last-child {
  border-bottom: none;
}

.history-card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.history-card :deep(.el-card__body) {
  flex: 1;
  overflow: auto;
}

.empty-history {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-item:hover {
  background-color: #ecf5ff;
}

.chat-main {
  height: 100%;
}

.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.empty-chat {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  color: #909399;
}

.input-container {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.input-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>