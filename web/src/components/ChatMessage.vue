<template>
  <div class="chat-message" :class="message.role">
    <div class="message-avatar">
      <el-avatar v-if="message.role === 'user'">
        <el-icon><User /></el-icon>
      </el-avatar>
      <el-avatar v-else class="assistant-avatar">
        <el-icon><Monitor /></el-icon>
      </el-avatar>
    </div>
    <div class="message-content">
      <div class="message-header">
        <span class="role-name">{{ roleLabel }}</span>
        <span v-if="timestamp" class="timestamp">{{ formatTime(timestamp) }}</span>
      </div>
      <div class="message-text" v-html="formattedContent"></div>
      <div v-if="message.role === 'assistant' && showActions" class="message-actions">
        <el-button size="small" text @click="copyContent">
          <el-icon><CopyDocument /></el-icon>
          复制
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { ChatMessage } from '@/api/chat'

interface Props {
  message: ChatMessage
  timestamp?: string
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true,
})

const roleLabel = computed(() => {
  return props.message.role === 'user' ? '你' : 'AI 助手'
})

const formattedContent = computed(() => {
  // 简单的 markdown 渲染
  let content = props.message.content
  // 代码块
  content = content.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
  // 行内代码
  content = content.replace(/`([^`]+)`/g, '<code>$1</code>')
  // 粗体
  content = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  // 斜体
  content = content.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  // 换行
  content = content.replace(/\n/g, '<br>')
  return content
})

function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function copyContent() {
  navigator.clipboard.writeText(props.message.content)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.chat-message.user {
  background-color: #ecf5ff;
}

.chat-message.assistant {
  background-color: #f4f4f5;
}

.message-avatar {
  flex-shrink: 0;
}

.assistant-avatar {
  background-color: #409EFF;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.role-name {
  font-weight: 600;
  color: #303133;
}

.timestamp {
  font-size: 12px;
  color: #909399;
}

.message-text {
  color: #303133;
  line-height: 1.6;
  word-break: break-word;
}

.message-text :deep(pre) {
  background-color: #282c34;
  color: #abb2bf;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-text :deep(code) {
  font-family: 'Fira Code', monospace;
}

.message-text :deep(code:not(pre code)) {
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  color: #e96900;
}

.message-actions {
  margin-top: 8px;
}
</style>
