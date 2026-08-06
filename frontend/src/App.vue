<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { login, register } from './api/auth'
import HeatFlowCalculator from './components/HeatFlowCalculator.vue'
import UserManagement from './components/UserManagement.vue'

const activeTab = ref('calculation')
const authMode = ref('login')
const authLoading = ref(false)
const auth = reactive({ token: localStorage.getItem('access_token'), user: JSON.parse(localStorage.getItem('current_user') || 'null') })
const credentials = reactive({ username: '', email: '', identifier: '', password: '' })

async function authenticate() {
  authLoading.value = true
  try {
    if (authMode.value === 'register') {
      await register({ username: credentials.username, email: credentials.email, password: credentials.password })
      ElMessage.success('注册成功，请登录')
      authMode.value = 'login'
      return
    }
    const { data } = await login({ identifier: credentials.identifier, password: credentials.password })
    auth.token = data.access_token
    auth.user = data.user
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('current_user', JSON.stringify(data.user))
    ElMessage.success('登录成功')
  } catch (error) { ElMessage.error(error.response?.data?.detail || '操作失败') }
  finally { authLoading.value = false }
}

function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('current_user')
  auth.token = null
  auth.user = null
  activeTab.value = 'calculation'
}
</script>

<template>
  <el-container v-if="!auth.token" class="auth-page"><el-card class="auth-card"><template #header><h1>地热产能计算平台</h1></template><p>请登录后使用计算与管理功能</p><el-tabs v-model="authMode" stretch><el-tab-pane label="登录" name="login" /><el-tab-pane label="注册" name="register" /></el-tabs><el-form label-position="top" @submit.prevent="authenticate"><el-form-item :label="authMode === 'login' ? '用户名或邮箱' : '用户名'"><el-input v-if="authMode === 'login'" v-model="credentials.identifier" autocomplete="username" /><el-input v-else v-model="credentials.username" autocomplete="username" /></el-form-item><el-form-item v-if="authMode === 'register'" label="邮箱"><el-input v-model="credentials.email" type="email" autocomplete="email" /></el-form-item><el-form-item label="密码"><el-input v-model="credentials.password" type="password" show-password autocomplete="current-password" /></el-form-item><el-button type="primary" native-type="submit" :loading="authLoading" class="full-button">{{ authMode === 'login' ? '登录' : '注册' }}</el-button></el-form><small>用户名唯一，限 3–50 位字母、数字、下划线或连字符；密码至少 6 位。</small></el-card></el-container>
  <el-container v-else class="page"><el-header><h1>地热产能计算平台</h1><div class="header-user"><span>{{ auth.user?.username }}（{{ auth.user?.role === 'admin' ? '管理员' : '用户' }}）</span><el-button text @click="logout">退出登录</el-button></div></el-header><el-main><el-tabs v-model="activeTab" class="main-tabs"><el-tab-pane label="产能计算" name="calculation"><HeatFlowCalculator /></el-tab-pane><el-tab-pane v-if="auth.user?.role === 'admin'" label="用户管理" name="users"><UserManagement /></el-tab-pane></el-tabs></el-main></el-container>
</template>
