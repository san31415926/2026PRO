<template>
  <div class="tab-page">
    <div v-if="!currentUser" class="login-wrapper">
      <div class="login-card">
        <div class="login-header"><h3>Smart Mall</h3><p>登录享受更多权益</p></div>
        <van-tabs :active="loginTab" color="#ee0a24" title-active-color="#ee0a24" @update:active="updateLoginTab">
          <van-tab title="账号登录">
            <div class="form-body">
              <van-field v-model="loginForm.username" left-icon="manager" placeholder="请输入账号" class="beauty-input" :border="false" />
              <van-field v-model="loginForm.password" left-icon="lock" type="password" placeholder="请输入密码" class="beauty-input" :border="false" />
              <van-button color="linear-gradient(to right, #ff6034, #ee0a24)" round block size="large" @click="onLogin" style="margin-top:20px; box-shadow: 0 4px 12px rgba(238,10,36,0.3);">立即登录</van-button>
            </div>
          </van-tab>
          <van-tab title="快速注册">
            <div class="form-body">
              <van-field v-model="regForm.username" left-icon="manager" placeholder="设置新账号" class="beauty-input" :border="false" />
              <van-field v-model="regForm.password" left-icon="lock" type="password" placeholder="设置新密码" class="beauty-input" :border="false" />
              <van-button color="#07c160" round block size="large" @click="onRegister" style="margin-top:20px; box-shadow: 0 4px 12px rgba(7,193,96,0.3);">注册领10000元</van-button>
            </div>
          </van-tab>
        </van-tabs>
      </div>
    </div>

    <div v-else>
      <div class="user-header-card" :class="{ 'is-vip': isVip }">
        <div class="user-info">
          <div style="position:relative; display:inline-block;">
            <img :src="currentUser.avatar" class="avatar" @click="triggerAvatarInput" style="cursor:pointer;" />
            <div
              style="position:absolute;bottom:0;right:0;background:rgba(0,0,0,0.45);border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;"
              @click="triggerAvatarInput"
            >
              <van-icon name="photograph" color="white" size="12" />
            </div>
            <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="handleAvatarChange" />
          </div>
          <div class="text-info">
            <div class="nickname">
              {{ currentUser.nickname }}
              <van-icon name="edit" style="margin-left: 8px; font-size: 16px; opacity: 0.8;" @click.stop="openEditName" />
              <span
                style="font-size:12px; font-weight:normal; margin-left:10px; opacity:0.6; border:1px solid rgba(255,255,255,0.5); padding:0px 6px; border-radius:10px; cursor:pointer;"
                @click.stop="logout"
              >
                <van-icon name="exchange" /> 切换
              </span>
            </div>
            <div class="level-badge"><van-icon name="gem" /> {{ vipLevelName }}</div>
          </div>
        </div>
        <div class="member-hero-meta">
          <div class="hero-desc-row">
            <div class="hero-desc">{{ heroText }}</div>
            <van-icon name="edit" class="hero-desc-edit-btn" @click.stop="openEditHeroText" />
          </div>
          <div class="hero-desc hero-desc-editable" contenteditable="true" spellcheck="false">鸟为什么会飞</div>
        </div>
      </div>

      <div class="data-row">
        <div class="data-item"><div class="num">{{ currentUser.balance.toFixed(2) }}</div><div class="lbl">余额</div></div>
        <div class="data-item"><div class="num">{{ currentUser.points }}</div><div class="lbl">积分</div></div>
        <div class="data-item" @click="viewMyWalletCoupons">
          <div class="num">{{ myUsableCoupons.length }}</div>
          <div class="lbl">优惠券</div>
        </div>
      </div>

      <div class="member-quick-panel">
        <div class="member-quick-item">
          <div class="quick-label">会员状态</div>
          <div class="quick-value">{{ vipLevelName }}</div>
        </div>
        <div class="member-quick-item">
          <div class="quick-label">待发货</div>
          <div class="quick-value">{{ pendingOrdersCount }}</div>
        </div>
        <div class="member-quick-item">
          <div class="quick-label">已收藏</div>
          <div class="quick-value">{{ favIds.length }}</div>
        </div>
      </div>

      <div class="menu-group">
        <div class="member-section-head">
          <span class="member-section-title">常用服务</span>
          <span class="member-section-sub">账户、资产与收藏</span>
        </div>
        <van-cell-group inset>
          <van-cell title="我的会员" :value="vipLevelName" icon="gem-o" is-link @click="openVipCenter" />
          <van-cell title="我的地址" icon="location-o" is-link @click="openAddressManager" />
          <van-cell title="修改密码" icon="shield-o" is-link @click="openChangePasswordDialog" />
          <van-cell title="余额充值" icon="gold-coin-o" is-link @click="openRecharge" />
          <van-cell title="我的收藏" icon="like-o" is-link @click="openFavorites" />
        </van-cell-group>
      </div>

      <div class="order-section">
        <div class="sec-head" @click="openOrderList"><span class="sec-title">我的订单</span><span class="sec-more">查看全部 ></span></div>

        <div v-if="!myOrderList || myOrderList.length === 0" class="empty-order-box">
          <van-icon name="orders-o" size="40" color="#ddd" /><p>这里空空如也，快去买点东西吧~</p>
        </div>

        <div v-for="order in recentOrders" :key="order.id" class="jd-order-card" @click="viewOrderDetail(order.id)">
          <div class="card-head"><span class="shop-name"><van-icon name="shop-o" /> Smart Mall 自营店</span><span class="status-txt" :class="'st-'+order.status">{{ getStatusText(order.status) }}</span></div>
          <div class="card-body"><img :src="order.img" /><div class="info"><div class="p-title">{{ order.title }}</div><div class="p-price">¥ {{ order.amount.toFixed(2) }}</div></div></div>
          <div class="card-foot">
            <van-button v-if="order.status===2" size="small" round color="#ee0a24" @click.stop="confirmOrderReceipt(order)">确认收货</van-button>
            <van-button v-if="order.status===3" size="small" round plain type="warning" @click.stop="openComment(order)">去评价</van-button>
            <van-button v-if="order.status===4" size="small" round plain disabled>已评价</van-button>
            <van-button v-if="order.status===1" size="small" round plain type="danger" @click.stop="cancelOrder(order)">取消订单</van-button>
            <span v-if="order.status===5" style="color:#ee0a24; font-size:12px;">待好友成团...</span>
          </div>
        </div>
      </div>

      <div style="height: 30px;"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  currentUser: { type: Object, default: null },
  isVip: Boolean,
  vipLevelName: { type: String, default: '' },
  heroText: { type: String, default: '' },
  loginTab: { type: Number, default: 0 },
  loginForm: { type: Object, required: true },
  regForm: { type: Object, required: true },
  myUsableCoupons: { type: Array, default: () => [] },
  myOrderList: { type: Array, default: () => [] },
  favIds: { type: Array, default: () => [] },
  onLogin: { type: Function, required: true },
  onRegister: { type: Function, required: true },
  logout: { type: Function, required: true },
  openEditName: { type: Function, required: true },
  handleAvatarChange: { type: Function, required: true },
  openEditHeroText: { type: Function, required: true },
  viewMyWalletCoupons: { type: Function, required: true },
  openVipCenter: { type: Function, required: true },
  openChangePasswordDialog: { type: Function, required: true },
  openRecharge: { type: Function, required: true },
  openFavorites: { type: Function, required: true },
  openAddressManager: { type: Function, required: true },
  openOrderList: { type: Function, required: true },
  viewOrderDetail: { type: Function, required: true },
  confirmOrderReceipt: { type: Function, required: true },
  openComment: { type: Function, required: true },
  cancelOrder: { type: Function, required: true },
  getStatusText: { type: Function, required: true },
})

const emit = defineEmits(['update:loginTab'])
const avatarInput = ref(null)

const pendingOrdersCount = computed(() => props.myOrderList.filter(order => order.status === 1 || order.status === 5).length)
const recentOrders = computed(() => props.myOrderList.slice(0, 2))

const updateLoginTab = value => emit('update:loginTab', value)
const triggerAvatarInput = () => avatarInput.value?.click()
</script>
