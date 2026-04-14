<template>
  <van-popup
    :show="show"
    class="sheet-popup mobile-shell-popup"
    position="bottom"
    :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }"
    @update:show="updateShow"
  >
    <div class="popup-mobile-shell favorites-shell">
      <van-nav-bar title="我的收藏" left-arrow @click-left="updateShow(false)" />
      <div class="popup-mobile-content favorites-content">
        <div v-if="favoriteList.length===0" style="text-align:center;color:gray;margin-top:50px;">暂无收藏</div>
        <div v-for="item in favoriteList" :key="item.id" class="fav-item" @click="openProductDetail(item)">
          <img :src="item.img">
          <div style="flex:1; min-width: 0;">
            <div class="f-title">{{ item.title }}</div>
            <div class="f-price">¥ {{ item.price }}</div>
          </div>
          <van-icon name="arrow" color="#999" />
        </div>
      </div>
    </div>
  </van-popup>
</template>

<script setup>
defineProps({
  show: Boolean,
  favoriteList: { type: Array, default: () => [] },
  openProductDetail: { type: Function, required: true },
})

const emit = defineEmits(['update:show'])
const updateShow = value => emit('update:show', value)
</script>
