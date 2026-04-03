<template>
  <div v-if="show" class="full-page-detail">
    <div class="detail-page-shell">
      <van-nav-bar title="订单详情" left-arrow @click-left="closeDetail" />
      <div class="detail-status-header">
        <div class="status-big"><van-icon name="logistics" size="24" />{{ getStatusText(currentOrderDetail.status) }}</div>
        <div class="status-desc">感谢您在 Smart Mall 购物，欢迎再次光临</div>
        <div class="detail-status-pills"><span class="detail-pill">官方自营</span><span class="detail-pill">物流可追踪</span><span class="detail-pill">售后无忧</span></div>
      </div>
      <div v-if="currentOrderDetail" class="detail-page-content" style="margin-top: -30px; position: relative; z-index: 2;">
        <div v-if="currentOrderDetail.group_code" class="card detail-code-card" style="margin-top:-20px;text-align:center;padding:15px;"><div class="detail-code-main">拼团码：{{ currentOrderDetail.group_code }}</div><div class="detail-code-sub">状态：{{ currentOrderDetail.status===5?'待成团':'拼团成功' }}</div></div>
        <div class="card detail-address-card"><div class="icon-side"><van-icon name="location" color="#ee0a24" size="24" /></div><div class="text-side"><div class="addr-title">收货信息</div><div class="addr-text">{{ currentOrderDetail.address }}</div></div></div>
        <div class="card detail-goods-card">
          <div class="shop-line"><van-icon name="shop-o" /> Smart Mall 自营店</div>
          <div class="goods-row"><img :src="currentOrderDetail.img" class="detail-goods-img" /><div class="g-right"><div class="g-title">{{ currentOrderDetail.title }}</div><div class="g-sub">官方直发 · 品质保障 · 支持售后</div><div class="g-price">¥ {{ currentOrderDetail.amount.toFixed(2) }}</div></div></div>
          <div class="contact-line">
            <van-button size="small" icon="service-o" round @click="openQQPopup">联系客服</van-button>
            <van-button size="small" icon="phone-o" round @click="openPhonePopup">拨打电话</van-button>
          </div>
        </div>
        <div class="card detail-meta"><div class="meta-row"><span>订单编号</span><span>{{ currentOrderDetail.no }}</span></div><div class="meta-row"><span>下单时间</span><span>{{ currentOrderDetail.date }}</span></div><div class="meta-row"><span>支付方式</span><span>在线支付</span></div></div>

        <div v-if="logisticsTraces.length > 0" class="card detail-logistics-card" style="padding:15px;">
          <div class="detail-logistics-title">物流轨迹</div>
          <div v-for="(trace, index) in logisticsTraces" :key="index" class="detail-logistics-row">
            <div class="detail-logistics-line">
              <div :class="['detail-logistics-dot', { active: index===0 }]"></div>
              <div v-if="index < logisticsTraces.length-1" class="detail-logistics-stick"></div>
            </div>
            <div class="detail-logistics-copy">
              <div :class="['detail-logistics-desc', { active: index===0 }]">{{ trace.desc }}</div>
              <div class="detail-logistics-time">{{ trace.time }}</div>
            </div>
          </div>
        </div>

        <div v-if="currentOrderDetail.status === 1" class="detail-action-wrap" style="padding:0 0 20px;">
          <van-button block round plain type="danger" @click="cancelOrder(currentOrderDetail)">取消订单</van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: Boolean,
  currentOrderDetail: { type: Object, default: null },
  logisticsTraces: { type: Array, default: () => [] },
  getStatusText: { type: Function, required: true },
  cancelOrder: { type: Function, required: true },
  openQQPopup: { type: Function, required: true },
  openPhonePopup: { type: Function, required: true },
})

const emit = defineEmits(['update:show'])
const closeDetail = () => emit('update:show', false)
</script>
