<template>
  <div class="tab-page activity-page" style="padding-bottom:60px;">
    <div class="activity-hero" :class="mode === 'group' ? 'group-hero' : 'seckill-hero'">
      <div class="activity-kicker">{{ mode === 'group' ? 'Group Buying Hall' : 'Flash Sale' }}</div>
      <h2 class="activity-title">{{ mode === 'group' ? '拼团大厅' : '疯狂秒杀' }}</h2>
      <p class="activity-desc">
        {{ mode === 'group'
          ? `${systemConfig.group_buy_people}人成团 · 享${systemConfig.group_buy_discount * 10}折优惠 · 越多人越划算`
          : '限时限量 · 手慢无 · 趁倒计时结束前抢到心仪单品' }}
      </p>
      <div class="activity-stat-row">
        <div class="activity-stat-card">
          <span class="activity-stat-num">{{ filteredGoodsList.length }}</span>
          <span class="activity-stat-label">{{ mode === 'group' ? '可拼商品' : '秒杀商品' }}</span>
        </div>
        <div class="activity-stat-card">
          <span class="activity-stat-num">{{ mode === 'group' ? systemConfig.group_buy_people : systemConfig.seckill_time_limit }}</span>
          <span class="activity-stat-label">{{ mode === 'group' ? '成团人数' : '限时分钟' }}</span>
        </div>
        <div class="activity-stat-card hot">
          <span class="activity-stat-num">{{ mode === 'group' ? `${Math.round(systemConfig.group_buy_discount * 100)}%` : 'HOT' }}</span>
          <span class="activity-stat-label">{{ mode === 'group' ? '拼团价率' : '火热抢购' }}</span>
        </div>
      </div>
    </div>

    <div class="goods-container activity-list">
      <template v-if="mode === 'group'">
        <div v-for="item in filteredGoodsList" :key="item.id" class="activity-card group-card" @click="openProductDetail(item)">
          <img :src="item.img" class="activity-card-img" />
          <div class="activity-card-body">
            <div class="activity-card-top">
              <div class="title">{{ item.title }}</div>
              <div class="tags"><span class="tag blue">{{ systemConfig.group_buy_people }}人团</span><span class="tag gold">多人更省</span></div>
            </div>
            <div class="activity-progress-copy">发起拼团后分享给好友，成团即可享受专属折扣。</div>
            <div class="activity-card-bottom">
              <div class="price" style="font-size:18px;">¥ {{ (item.price * systemConfig.group_buy_discount).toFixed(0) }} <span class="activity-old-price">¥{{ item.price }}</span></div>
              <van-button color="linear-gradient(135deg, #ff8652, #e84d2a)" size="small" round>去开团</van-button>
            </div>
          </div>
        </div>
      </template>

      <template v-else>
        <div v-for="item in filteredGoodsList" :key="item.id" class="activity-card seckill-card" @click="openProductDetail(item)">
          <div class="activity-card-img-shell">
            <img :src="item.img" class="activity-card-img" />
            <div class="activity-corner-badge">{{ getSeckillStatusTag(item) }}</div>
          </div>
          <div class="activity-card-body">
            <div class="title" style="font-weight:bold;">{{ item.title }}</div>
            <div class="activity-progress-copy">限时限量 · 每人限购 {{ item.seckill_limit_per_user || 1 }} 件 · 剩余 {{ item.display_stock }} 件</div>
            <div class="activity-card-bottom seckill-bottom">
              <div class="price" style="font-size:18px;">¥ {{ Number(item.display_price ?? item.price).toFixed(2) }} <span class="activity-old-price">¥{{ Number(item.price).toFixed(2) }}</span></div>
              <van-button :color="item.seckill_status === 'active' ? 'linear-gradient(135deg, #ff7347, #d92f2f)' : '#c8c9cc'" size="small" round>{{ getSeckillStatusText(item) }}</van-button>
            </div>
            <div class="activity-progress-bar">
              <div class="activity-progress-fill" :style="{ width: `${getSeckillProgress(item)}%` }"></div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
defineProps({
  mode: { type: String, required: true },
  systemConfig: { type: Object, required: true },
  filteredGoodsList: { type: Array, default: () => [] },
  openProductDetail: { type: Function, required: true },
  getSeckillStatusTag: { type: Function, required: true },
  getSeckillStatusText: { type: Function, required: true },
  getSeckillProgress: { type: Function, required: true },
})
</script>
