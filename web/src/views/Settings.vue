<template>
  <div class="settings-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>个人信息</span>
          </template>
          
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
          >
            <el-form-item label="用户名">
              <el-input :value="authStore.user?.username" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="profileLoading" @click="updateProfile">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>修改密码</span>
          </template>
          
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input
                v-model="passwordForm.currentPassword"
                type="password"
                placeholder="请输入当前密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请确认新密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="passwordLoading" @click="changePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>账户统计</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic title="知识库数量" :value="knowledgeStore.knowledgeBases.length" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="文档总数" :value="knowledgeStore.totalDocuments" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="账户状态">
                <template #default>
                  <el-tag type="success">正常</el-tag>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>危险操作</span>
          </template>
          
          <el-alert
            title="危险区域"
            type="warning"
            description="以下操作不可逆，请谨慎操作"
            show-icon
            :closable="false"
            style="margin-bottom: 20px;"
          />
          
          <el-button type="danger" @click="handleDeleteAccount">
            删除账户
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useKnowledgeStore } from '@/stores/knowledge'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

const authStore = useAuthStore()
const knowledgeStore = useKnowledgeStore()

const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const profileLoading = ref(false)
const passwordLoading = ref(false)

const profileForm = reactive({
  email: authStore.user?.email || '',
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const profileRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
}

const passwordRules: FormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

async function updateProfile() {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      profileLoading.value = true
      try {
        await authStore.updateProfile({ email: profileForm.email })
        ElMessage.success('更新成功')
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '更新失败')
      } finally {
        profileLoading.value = false
      }
    }
  })
}

async function changePassword() {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true
      try {
        // 调用 API 更新密码
        await authStore.updateProfile({ password: passwordForm.newPassword })
        ElMessage.success('密码修改成功')
        passwordFormRef.value?.resetFields()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '密码修改失败')
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

function handleDeleteAccount() {
  ElMessageBox.confirm(
    '您确定要删除账户吗？此操作不可恢复，所有数据将被永久删除。',
    '危险操作',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger',
    }
  ).then(() => {
    // 这里应该调用删除账户的 API
    ElMessage.info('删除账户功能暂未实现')
  }).catch(() => {})
}

onMounted(() => {
  knowledgeStore.fetchKnowledgeBases()
})
</script>

<style scoped>
.settings-page {
  height: 100%;
}
</style>