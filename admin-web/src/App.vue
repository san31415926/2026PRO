<template>
  <LoginView v-if="!isLogin" @login-success="handleLoginSuccess" />

  <div v-else class="admin-layout">
    <el-container class="full-height">
      <el-aside width="220px" class="aside-menu">
        <div class="logo-area"><el-icon size="24" color="#409EFF"><Shop /></el-icon><span style="margin-left: 10px;">数码电子商城</span></div>
        <el-menu active-text-color="#409EFF" background-color="#1f2d3d" text-color="#bfcbd9" :default-active="activeMenu" class="el-menu-vertical" @select="handleMenuSelect">
          <el-menu-item index="dashboard"><el-icon><Odometer /></el-icon><span>数据分析管理</span></el-menu-item>
          <el-menu-item index="banners"><el-icon><Picture /></el-icon><span>轮播图管理</span></el-menu-item>
          <el-menu-item index="goods"><el-icon><Goods /></el-icon><span>商品管理</span></el-menu-item>
          <el-menu-item index="orders"><el-icon><List /></el-icon><span>订单处理</span></el-menu-item>
          <el-menu-item index="comments"><el-icon><ChatDotSquare /></el-icon><span>评价管理</span></el-menu-item>
          <el-menu-item index="coupon_settings"><el-icon><Ticket /></el-icon><span>领劵中心设置</span></el-menu-item>
          <el-menu-item index="group_settings"><el-icon><UserFilled /></el-icon><span>拼团设置</span></el-menu-item>
          <el-menu-item index="seckill_settings"><el-icon><Timer /></el-icon><span>秒杀设置</span></el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="admin-header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-avatar :size="30" :src="userInfo.avatar" style="margin-right: 8px;" />
            {{ userInfo.nickname }}
            <el-button link type="danger" @click="logout" style="margin-left: 15px;">退出</el-button>
          </div>
        </el-header>
        <el-main class="main-content">
          <DashboardView v-if="activeMenu === 'dashboard'" />
          <BannerManager v-if="activeMenu === 'banners'" />
          <ProductManager v-if="activeMenu === 'goods'" />
          <OrderManager v-if="activeMenu === 'orders'" />
          <CommentManager v-if="activeMenu === 'comments'" />
          <CouponManager v-if="activeMenu === 'coupon_settings'" />
          <GroupSettings v-if="activeMenu === 'group_settings'" />
          <SeckillSettings v-if="activeMenu === 'seckill_settings'" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Shop, Odometer, Picture, Goods, List, ChatDotSquare, Ticket, UserFilled, Timer } from '@element-plus/icons-vue'

// Views
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import BannerManager from './views/BannerManager.vue'
import ProductManager from './views/ProductManager.vue'
import OrderManager from './views/OrderManager.vue'
import CommentManager from './views/CommentManager.vue'
import CouponManager from './views/CouponManager.vue'
import GroupSettings from './views/GroupSettings.vue'
import SeckillSettings from './views/SeckillSettings.vue'

const isLogin = ref(false)
const userInfo = ref({ nickname: '张捷', avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png' })
const activeMenu = ref('dashboard')
const currentTitle = ref('数据分析管理')

const handleLoginSuccess = (user) => {
  userInfo.value = user
  isLogin.value = true
}

const handleMenuSelect = (index) => {
    activeMenu.value = index;
    const map = {
        'dashboard':'数据分析管理', 'banners':'轮播图管理', 'goods':'商品管理中心', 'orders':'订单处理系统', 'comments': '评价管理',
        'coupon_settings': '领劵中心设置',
        'group_settings': '拼团设置', 'seckill_settings': '秒杀设置'
    };
    currentTitle.value = map[index] || '首页';
}

const logout = () => location.reload()
</script>

<style>
body { margin: 0; background-color: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif; }
.full-height { height: 100vh; }
.aside-menu { background: #1f2d3d; }
.logo-area { height: 60px; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; background: #141e2b; }
.admin-header { background: white; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; }
.main-content { padding: 20px; }
</style>