<template>
  <van-popup
    :show="show"
    class="sheet-popup mobile-shell-popup"
    position="bottom"
    :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }"
    @update:show="updateShow"
  >
    <div class="popup-mobile-shell all-orders-shell">
      <van-nav-bar title="我的订单" left-arrow @click-left="closePopup" />
      <van-tabs
        :active="activeOrderTab"
        sticky
        offset-top="0"
        background="#fff"
        color="#ee0a24"
        title-active-color="#ee0a24"
        @update:active="updateActiveTab"
      >
        <van-tab title="全部" name="all"></van-tab>
        <van-tab title="待发货" name="wait_ship"></van-tab>
        <van-tab title="待收货" name="shipped"></van-tab>
        <van-tab title="已完成" name="completed"></van-tab>
      </van-tabs>
      <div class="popup-mobile-content">
        <van-empty v-if="filteredAllOrders.length === 0" description="暂无相关订单" />
        <div v-for="order in filteredAllOrders" :key="order.id" class="jd-order-card" @click="viewOrderDetail(order.id)">
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
        <div style="height:40px; text-align:center; color:#ccc; font-size:12px; line-height:40px;">我是有底线的</div>
      </div>
    </div>
  </van-popup>
</template>

<script setup>
defineProps({
  show: Boolean,
  activeOrderTab: { type: String, default: 'all' },
  filteredAllOrders: { type: Array, default: () => [] },
  getStatusText: { type: Function, required: true },
  viewOrderDetail: { type: Function, required: true },
  confirmOrderReceipt: { type: Function, required: true },
  openComment: { type: Function, required: true },
  cancelOrder: { type: Function, required: true },
})

const emit = defineEmits(['update:show', 'update:activeOrderTab'])

const updateShow = value => emit('update:show', value)
const updateActiveTab = value => emit('update:activeOrderTab', value)
const closePopup = () => emit('update:show', false)
</script>
