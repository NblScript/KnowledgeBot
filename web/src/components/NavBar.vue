<template>
  <el-menu
    :default-active="activeIndex"
    mode="horizontal"
    background-color="#409EFF"
    text-color="#fff"
    active-text-color="#ffd04b"
    @select="handleSelect"
  >
    <el-menu-item index="chat">
      <el-icon><ChatDotRound /></el-icon>
      <span>智能问答</span>
    </el-menu-item>
    <el-menu-item index="knowledge-bases">
      <el-icon><Collection /></el-icon>
      <span>知识库</span>
    </el-menu-item>
    <el-menu-item index="documents">
      <el-icon><Document /></el-icon>
      <span>文档管理</span>
    </el-menu-item>
    <div class="flex-grow" />
    <el-sub-menu index="user">
      <template #title>
        <el-icon><User /></el-icon>
        <span>{{ user?.username || '用户' }}</span>
      </template>
      <el-menu-item index="settings">
        <el-icon><Setting /></el-icon>
        <span>设置</span>
      </el-menu-item>
      <el-menu-item index="logout">
        <el-icon><SwitchButton /></el-icon>
        <span>退出登录</span>
      </el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeIndex = computed(() => {
  const path = route.path.split('/')[1]
  return path || 'chat'
})

const user = computed(() => authStore.user)

function handleSelect(index: string) {
  if (index === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(() => {
      authStore.logout()
      router.push('/login')
    }).catch(() => {})
    return
  }
  router.push('/' + index)
}
</script>

<style scoped>
.flex-grow {
  flex-grow: 1;
}
</style>
