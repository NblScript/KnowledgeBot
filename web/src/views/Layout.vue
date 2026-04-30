<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <NavBar />
    </el-header>
    <el-main class="layout-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NavBar from '@/components/NavBar.vue'

const authStore = useAuthStore()

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error('Failed to fetch user:', error)
    }
  }
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-header {
  padding: 0;
  height: auto;
}

.layout-main {
  padding: 20px;
  background-color: #f5f7fa;
}
</style>