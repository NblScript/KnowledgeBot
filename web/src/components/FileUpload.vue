<template>
  <el-upload
    ref="uploadRef"
    class="file-upload"
    :auto-upload="false"
    :limit="limit"
    :accept="acceptTypes"
    :on-change="handleFileChange"
    :on-exceed="handleExceed"
    :file-list="fileList"
    drag
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      将文件拖到此处，或 <em>点击上传</em>
    </div>
    <template #tip>
      <div class="el-upload__tip">
        支持 PDF、TXT、Markdown 等格式文件，单个文件不超过 {{ maxSizeMB }}MB
      </div>
    </template>
  </el-upload>
  <div v-if="selectedFile" class="file-info">
    <el-tag type="success">
      已选择: {{ selectedFile.name }} ({{ formatSize(selectedFile.size) }})
    </el-tag>
    <el-button type="primary" :loading="uploading" @click="handleUpload">
      开始上传
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile, UploadFiles, UploadInstance } from 'element-plus'

interface Props {
  limit?: number
  maxSizeMB?: number
  knowledgeBaseId?: number
}

const props = withDefaults(defineProps<Props>(), {
  limit: 5,
  maxSizeMB: 50,
})

const emit = defineEmits<{
  (e: 'upload', file: File): void
  (e: 'success', file: File): void
  (e: 'error', error: Error): void
}>()

const uploadRef = ref<UploadInstance>()
const fileList = ref<UploadFile[]>([])
const selectedFile = ref<File | null>(null)
const uploading = ref(false)

const acceptTypes = '.pdf,.txt,.md,.markdown,.docx,.doc'

function handleFileChange(file: UploadFile, _files: UploadFiles) {
  const maxSize = props.maxSizeMB * 1024 * 1024
  if (file.raw && file.raw.size > maxSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSizeMB}MB`)
    fileList.value = []
    return
  }
  selectedFile.value = file.raw || null
  emit('upload', file.raw!)
}

function handleExceed(_files: File[]) {
  ElMessage.warning(`最多只能上传 ${props.limit} 个文件`)
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  uploading.value = true
  try {
    emit('success', selectedFile.value)
    fileList.value = []
    selectedFile.value = null
  } catch (error: any) {
    emit('error', error)
  } finally {
    uploading.value = false
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

defineExpose({
  clearFiles: () => {
    fileList.value = []
    selectedFile.value = null
  }
})
</script>

<style scoped>
.file-upload {
  width: 100%;
}

.file-info {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
