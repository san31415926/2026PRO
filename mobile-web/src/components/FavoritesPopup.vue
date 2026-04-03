<template>
  <van-popup :show="show" position="bottom" round :style="{ height: '60%' }" @update:show="updateShow">
    <div style="padding:20px;">
      <h3 style="text-align:center;">我的收藏</h3>
      <div v-if="favoriteList.length===0" style="text-align:center;color:gray;margin-top:50px;">暂无收藏</div>
      <div v-for="item in favoriteList" :key="item.id" class="fav-item" @click="openProductDetail(item)">
        <img :src="item.img">
        <div style="flex:1;">
          <div class="f-title">{{ item.title }}</div>
          <div class="f-price">¥ {{ item.price }}</div>
        </div>
        <van-icon name="arrow" color="#999" />
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
