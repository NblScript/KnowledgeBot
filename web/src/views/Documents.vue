<template>
  <div class="documents-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <span>文档管理</span>
                <el-select
                  v-model="selectedKbId"
                  placeholder="选择知识库"
                  style="width: 200px; margin-left: 16px;"
                  @change="handleKbChange"
                >
                  <el-option
                    v-for="kb in knowledgeStore.knowledgeBases"
                    :key="kb.id"
                    :label="kb.name"
                    :value="kb.id"
                  />
                </el-select>
              </div>
              <el-button
                type="primary"
                :disabled="!selectedKbId"
                @click="showUploadDialog"
              >
                <el-icon><Upload /></el-icon>
                上传文档
              </el-button>
            </div>
          </template>
          
          <el-empty v-if="!selectedKbId" description="请选择知识库" />
          
          <el-table
            v-else
            :data="knowledgeStore.documents"
            v-loading="knowledgeStore.loading"
            stripe
          >
            <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
            <el-table-column prop="file_size" label="大小" width="120">
              <template #default="{ row }">
                {{ formatSize(row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="chunk_count" label="分块数" width="100" align="center">
              <template #default="{ row }">
                {{ row.chunk_count || 0 }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="上传时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="handleDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 上传对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传文档"
      width="600px"
    >
      <FileUpload
        ref="fileUploadRef"
        @success="handleUploadSuccess"
        @error="handleUploadError"
      />
      <template #footer>
        <el-button @click="uploadDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useKnowledgeStore } from '@/stores/knowledge'
import { ElMessage, ElMessageBox } from 'element-plus'
import FileUpload from '@/components/FileUpload.vue'
import type { Document } from '@/api/knowledge'

const route = useRoute()
const knowledgeStore = useKnowledgeStore()

const fileUploadRef = ref()
const uploadDialogVisible = ref(false)
const selectedKbId = ref<number | null>(null)

function handleKbChange() {
  if (selectedKbId.value) {
    knowledgeStore.fetchDocuments(selectedKbId.value)
  }
}

function showUploadDialog() {
  uploadDialogVisible.value = true
}

async function handleUploadSuccess(file: File) {
  if (!selectedKbId.value) return
  
  try {
    await knowledgeStore.uploadDocument(selectedKbId.value, file)
    ElMessage.success(`文档 "${file.name}" 上传成功`)
    uploadDialogVisible.value = false
    fileUploadRef.value?.clearFiles()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '上传失败')
  }
}

function handleUploadError(error: Error) {
  ElMessage.error(`上传失败: ${error.message}`)
}

function handleDelete(row: Document) {
  if (!selectedKbId.value) return
  
  ElMessageBox.confirm(
    `确定要删除文档 "${row.filename}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await knowledgeStore.deleteDocument(selectedKbId.value!, row.id)
      ElMessage.success('删除成功')
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }).catch(() => {})
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-CN')
}

function getStatusType(status: string): '' | 'success' | 'warning' | 'info' | 'danger' {
  const map: Record<string, '' | 'success' | 'warning' | 'info' | 'danger'> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return map[status] || 'info'
}

function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return map[status] || status
}

onMounted(async () => {
  await knowledgeStore.fetchKnowledgeBases()
  
  // 从路由参数获取知识库 ID
  const kbId = route.params.kbId as string
  if (kbId) {
    selectedKbId.value = parseInt(kbId)
    knowledgeStore.fetchDocuments(selectedKbId.value)
  }
})
</script>

<style scoped>
.documents-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}
</style>