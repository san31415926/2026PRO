<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-left">
        <h2 class="sys-title">Smart Mall</h2>
        <p class="sys-desc">全渠道智慧新零售系统</p>
      </div>
      <div class="login-right">
        <h3>{{ isRegisterMode ? '注册管理员' : '管理员登录' }}</h3>
        <el-form size="large" class="login-form">
          <el-form-item>
            <el-input v-model="loginForm.username" placeholder="请输入账号" prefix-icon="User" />
          </el-form-item>
          <el-form-item>
            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item v-if="isRegisterMode">
            <el-input v-model="registerConfirmPassword" type="password" placeholder="请再次输入密码" prefix-icon="Lock" show-password />
          </el-form-item>
          <el-button type="primary" class="login-btn" @click="isRegisterMode ? handleRegister() : handleLogin()">
            {{ isRegisterMode ? '立即注册' : '立即登录' }}
          </el-button>
          <el-button link class="switch-mode-btn" @click="toggleAuthMode">
            {{ isRegisterMode ? '已有账号？去登录' : '没有账号？注册管理员' }}
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const emit = defineEmits(['login-success'])

const loginForm = reactive({ username: 'admin', password: '123456' })
const isRegisterMode = ref(false)
const registerConfirmPassword = ref('')

const handleLogin = async () => {
  try {
    const res = await axios.post('http://localhost:5000/api/admin/login', loginForm);
    if (res.data.code === 200) {
      emit('login-success', res.data.data)
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch(e) {
    ElMessage.error('连接失败')
  }
}

const handleRegister = async () => {
  const username = (loginForm.username || '').trim()
  const password = (loginForm.password || '').trim()
  const confirm = (registerConfirmPassword.value || '').trim()
  if (!username) return ElMessage.warning('请输入账号')
  if (username.length < 3) return ElMessage.warning('账号至少3位')
  if (!password) return ElMessage.warning('请输入密码')
  if (password.length < 6) return ElMessage.warning('密码至少6位')
  if (password !== confirm) return ElMessage.warning('两次密码不一致')
  try {
    const res = await axios.post('http://localhost:5000/api/admin/register', { username, password })
    if (res.data.code === 200) {
      ElMessage.success('注册成功，请登录')
      isRegisterMode.value = false
      registerConfirmPassword.value = ''
    } else {
      ElMessage.error(res.data.msg || '注册失败')
    }
  } catch (e) {
    ElMessage.error('连接失败')
  }
}

const toggleAuthMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  registerConfirmPassword.value = ''
}
</script>

<style scoped>
.login-container { display: flex; height: 100vh; justify-content: center; align-items: center; background: #2d3a4b; }
.login-box { width: 700px; height: 400px; background: white; display: flex; border-radius: 8px; overflow: hidden; }
.login-left { width: 40%; background: #409EFF; padding: 40px; color: white; display:flex; flex-direction:column; justify-content:center; }
.login-right { width: 60%; padding: 40px; display: flex; flex-direction: column; justify-content: center; }
.login-btn { width: 100%; margin-top: 10px; }
.switch-mode-btn { margin-top: 10px; width: 100%; }
.sys-title { margin: 0 0 20px 0; font-size: 24px; }
.sys-desc { margin: 0; font-size: 14px; opacity: 0.8; }
</style>
