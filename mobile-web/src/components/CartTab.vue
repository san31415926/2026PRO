<template>
  <div class="tab-page" style="padding-bottom:120px;">
    <div v-if="cartList.length === 0" class="empty-cart">
      <van-empty description="老板，您还没挑东西呢！" />
      <van-button color="linear-gradient(to right, #ff6034, #ee0a24)" round size="small" @click="goHome">去逛逛</van-button>
    </div>
    <div v-else class="cart-list-container">
      <div v-for="item in cartList" :key="item.id" class="cart-item">
        <van-checkbox v-model="item.checked" checked-color="#ee0a24" icon-size="18px"></van-checkbox>
        <img :src="item.img" class="cart-img" />
        <div class="cart-info">
          <div class="cart-title">{{ item.title }}</div>
          <div class="cart-footer">
            <div class="cart-price">¥ {{ Number(item.price).toFixed(2) }}</div>
            <div class="cart-stepper">
              <van-stepper v-model="item.num" theme="round" button-size="22" disable-input @change="updateCartNum(item)" />
              <van-icon name="delete" color="#999" style="margin-left:10px;" @click="updateCartNum(item, 0)" />
            </div>
          </div>
        </div>
      </div>
      <div class="cart-submit-shell">
        <label class="cart-submit-check">
          <van-checkbox v-model="allCheckedProxy" checked-color="#ee0a24">全选</van-checkbox>
        </label>
        <div class="cart-submit-price">
          <span class="cart-submit-label">合计</span>
          <span class="cart-submit-value">¥ {{ calculateCartFinalPrice }}</span>
        </div>
        <van-button round color="linear-gradient(135deg, #ff8652, #e84d2a)" class="cart-submit-btn" @click="handleCartCheckout">去结算</van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  cartList: { type: Array, default: () => [] },
  isAllChecked: Boolean,
  calculateCartFinalPrice: { type: [String, Number], default: '0.00' },
  updateCartNum: { type: Function, required: true },
  handleCartCheckout: { type: Function, required: true },
  goHome: { type: Function, required: true },
})

const emit = defineEmits(['update:isAllChecked'])

const allCheckedProxy = computed({
  get: () => props.isAllChecked,
  set: (value) => emit('update:isAllChecked', value),
})
</script>
