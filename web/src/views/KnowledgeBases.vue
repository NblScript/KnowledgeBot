<template>
  <div class="knowledge-bases-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>知识库列表</span>
              <el-button type="primary" @click="showCreateDialog">
                <el-icon><Plus /></el-icon>
                新建知识库
              </el-button>
            </div>
          </template>
          
          <el-table :data="knowledgeStore.knowledgeBases" v-loading="knowledgeStore.loading" stripe>
            <el-table-column prop="name" label="名称" min-width="150" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="document_count" label="文档数量" width="120" align="center">
              <template #default="{ row }">
                <el-tag>{{ row.document_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="viewDocuments(row.id)">
                  <el-icon><Document /></el-icon>
                  文档
                </el-button>
                <el-button size="small" type="primary" @click="showEditDialog(row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button size="small" type="danger" @click="handleDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑知识库' : '新建知识库'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useKnowledgeStore } from '@/stores/knowledge'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { KnowledgeBase } from '@/api/knowledge'

const router = useRouter()
const knowledgeStore = useKnowledgeStore()

const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  name: '',
  description: '',
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' },
  ],
}

function showCreateDialog() {
  isEditing.value = false
  editingId.value = null
  form.name = ''
  form.description = ''
  dialogVisible.value = true
}

function showEditDialog(row: KnowledgeBase) {
  isEditing.value = true
  editingId.value = row.id
  form.name = row.name
  form.description = row.description
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEditing.value && editingId.value) {
          await knowledgeStore.updateKnowledgeBase(editingId.value, {
            name: form.name,
            description: form.description,
          })
          ElMessage.success('更新成功')
        } else {
          await knowledgeStore.createKnowledgeBase(form.name, form.description)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

function handleDelete(row: KnowledgeBase) {
  ElMessageBox.confirm(
    `确定要删除知识库 "${row.name}" 吗？删除后无法恢复。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await knowledgeStore.deleteKnowledgeBase(row.id)
      ElMessage.success('删除成功')
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }).catch(() => {})
}

function viewDocuments(kbId: number) {
  router.push(`/documents/${kbId}`)
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  knowledgeStore.fetchKnowledgeBases()
})
</script>

<style scoped>
.knowledge-bases-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>