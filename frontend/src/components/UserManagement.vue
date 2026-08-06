<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { listUsers, updateUser } from '../api/users'

const loading = ref(false)
const users = ref([])

async function loadUsers() {
  loading.value = true
  try { users.value = (await listUsers()).data }
  catch (error) { ElMessage.error(error.response?.data?.detail || '用户列表加载失败') }
  finally { loading.value = false }
}

async function toggleActive(user) {
  try {
    const { data } = await updateUser(user.id, { is_active: !user.is_active })
    Object.assign(user, data)
    ElMessage.success('用户状态已更新')
  } catch (error) { ElMessage.error(error.response?.data?.detail || '更新失败') }
}

async function changeRole(user, role) {
  try {
    const { data } = await updateUser(user.id, { role })
    Object.assign(user, data)
    ElMessage.success('用户角色已更新')
  } catch (error) { ElMessage.error(error.response?.data?.detail || '更新失败') }
}

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

onMounted(loadUsers)
</script>

<template>
  <el-card class="management-card">
    <template #header><div class="card-title"><span>用户管理</span><el-button :loading="loading" @click="loadUsers">刷新</el-button></div></template>
    <el-table :data="users" v-loading="loading" stripe>
      <el-table-column prop="username" label="用户名" />
      <el-table-column label="邮箱" min-width="220"><template #default="{ row }">{{ row.email || '-' }}</template></el-table-column>
      <el-table-column label="角色" width="160">
        <template #default="{ row }"><el-select :model-value="row.role" @change="changeRole(row, $event)"><el-option label="管理员" value="admin" /><el-option label="普通用户" value="user" /></el-select></template>
      </el-table-column>
      <el-table-column label="状态" width="130"><template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag></template></el-table-column>
      <el-table-column label="注册时间" min-width="130"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
      <el-table-column label="操作" width="110"><template #default="{ row }"><el-button link type="primary" @click="toggleActive(row)">{{ row.is_active ? '停用' : '启用' }}</el-button></template></el-table-column>
    </el-table>
  </el-card>
</template>

<style scoped>
.card-title { display: flex; justify-content: space-between; align-items: center; }
</style>
