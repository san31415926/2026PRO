<template>
  <div
    class="tab-page"
    :style="{
      background: isVip
        ? 'linear-gradient(180deg, rgba(248, 239, 229, 0.98) 0%, rgba(244, 232, 217, 0.96) 38%, rgba(246, 241, 235, 0.98) 100%)'
        : 'transparent'
    }"
  >
    <div
      class="header-search-box home-search-shell"
      :style="{
        background: isVip
          ? 'linear-gradient(180deg, rgba(248, 239, 229, 0.96), rgba(242, 229, 214, 0.94))'
          : 'transparent'
      }"
    >
      <div class="home-search-card">
        <div class="home-search-top">
          <div>
            <div class="home-search-kicker">{{ isVip ? 'VIP SELECTION' : 'CURATED TECH' }}</div>
            <div class="home-search-title">Smart Mall</div>
            <div class="home-search-sub">{{ isVip ? 'VIP 专属会场已开启' : '发现今天值得买的数码好物' }}</div>
          </div>
          <div class="home-search-refresh" @click="loadProducts(true)">
            <van-icon name="replay" :color="isVip ? '#f7e6b6' : '#b16d4f'" size="18" />
          </div>
        </div>
        <van-search
          :model-value="searchKeyword"
          placeholder="搜手机、电脑、耳机..."
          shape="round"
          background="transparent"
          class="home-search-input"
          @update:model-value="updateSearchKeyword"
        />
        <div class="home-search-shortcuts">
          <span class="home-shortcut">官方自营</span>
          <span class="home-shortcut">极速发货</span>
          <span class="home-shortcut active">{{ currentCategory }}</span>
        </div>
        <div class="home-metrics">
          <div class="metric-pill">
            <van-icon name="goods-collect-o" size="16" />
            <span class="metric-num">{{ goodsList.length }}</span>
            <span class="metric-label">在售好物</span>
          </div>
          <div class="metric-pill">
            <van-icon name="fire-o" size="16" />
            <span class="metric-num">{{ bannerList.length || 1 }}</span>
            <span class="metric-label">活动会场</span>
          </div>
          <div class="metric-pill accent">
            <van-icon name="star-o" size="16" />
            <span class="metric-num">{{ isVip ? 'VIP' : 'NEW' }}</span>
            <span class="metric-label">{{ isVip ? '折扣中' : '逛新品' }}</span>
          </div>
        </div>
      </div>
      <van-search
        :model-value="searchKeyword"
        placeholder="搜手机、电脑..."
        shape="round"
        background="transparent"
        style="flex:1;"
        @update:model-value="updateSearchKeyword"
      />
      <van-icon name="replay" color="white" size="24" style="margin-left:10px; opacity:0.9;" @click="loadProducts(true)" />
    </div>

    <div class="banner-box">
      <van-swipe :autoplay="3000" indicator-color="white" class="my-swipe">
        <van-swipe-item v-for="banner in bannerList" :key="banner.id">
          <img :src="banner.img" class="banner-img" />
        </van-swipe-item>
        <van-swipe-item v-if="bannerList.length === 0">
          <div class="empty-banner">暂无轮播图，请去后台添加</div>
        </van-swipe-item>
      </van-swipe>
    </div>

    <div class="home-highlight-panel">
      <div class="highlight-copy">
        <div class="highlight-eyebrow">今日主推</div>
        <div class="highlight-title">{{ isVip ? '会员价专区' : '数码潮品精选' }}</div>
        <div class="highlight-desc">{{ searchKeyword ? `搜索 “${searchKeyword}” 的相关结果` : '从热门单品到限时活动，先逛首屏精选再决定下单。' }}</div>
      </div>
      <div class="highlight-insight">
        <div class="highlight-insight-card">
          <span class="highlight-insight-label">当前频道</span>
          <span class="highlight-insight-value">{{ currentCategory }}</span>
        </div>
        <div class="highlight-insight-card warm">
          <span class="highlight-insight-label">当前展示</span>
          <span class="highlight-insight-value">{{ filteredGoodsList.length }} 件</span>
        </div>
      </div>
      <div class="highlight-badges">
        <span class="highlight-badge">包邮自营</span>
        <span class="highlight-badge">极速发货</span>
        <span class="highlight-badge hot">{{ isVip ? '会员专享' : '人气热卖' }}</span>
      </div>
    </div>

    <div class="menu-container">
      <draggable v-model="menuProxy" class="drag-grid" item-key="text" :animation="200">
        <template #item="{ element }">
          <div class="drag-item" @click="handleGridClick(element)">
            <div class="icon-circle">
              <van-icon :name="element.icon" size="24" :color="isVip ? '#dda246' : '#ee0a24'" />
            </div>
            <span class="menu-text">{{ element.text }}</span>
          </div>
        </template>
      </draggable>
    </div>

    <div v-if="currentCategory === '秒杀'" class="seckill-bar">
      <div class="sk-left"><van-icon name="clock" /> 秒杀专区</div>
      <div class="sk-timer">🔥 火热进行中</div>
    </div>

    <div class="goods-container">
      <div class="section-head">
        <div class="section-copy">
          <div class="section-kicker">{{ searchKeyword ? '搜索结果' : '商城推荐' }}</div>
          <div class="section-title">{{ currentCategory }}</div>
          <div class="section-sub">{{ searchKeyword ? '按关键词为你筛选出的商品' : '挑几件顺眼的，直接点进去看详情' }}</div>
        </div>
        <div class="section-side">{{ filteredGoodsList.length }} 件</div>
      </div>
      <van-empty v-if="filteredGoodsList.length === 0" description="暂无相关商品" />
      <div class="goods-waterfall">
        <div v-for="item in filteredGoodsList" :key="item.id" class="goods-card" @click="openProductDetail(item)">
          <div class="img-wrapper" style="position:relative;">
            <img :src="item.img" />
            <div
              v-if="item.display_stock === 0"
              style="position:absolute;inset:0;background:rgba(0,0,0,0.45);display:flex;align-items:center;justify-content:center;border-radius:8px 8px 0 0;"
            >
              <span style="color:white;font-size:16px;font-weight:bold;">售罄</span>
            </div>
          </div>
          <div class="info-wrapper">
            <div class="title">{{ item.title }}</div>
            <div class="tags">
              <span v-if="item.is_seckill" class="tag red">{{ getSeckillStatusTag(item) }}</span>
              <span v-else-if="!isVip" class="tag red">原价</span>
              <span v-else class="tag gold">VIP价</span>
              <span v-if="item.category.includes('拼团')" class="tag blue">拼团</span>
              <span v-if="item.category.includes('秒杀') && !item.is_seckill" class="tag red">秒杀</span>
            </div>
            <div class="bottom-row">
              <div class="price">
                ¥ <span class="num">{{ Number(item.display_price ?? item.price).toFixed(0) }}</span>.{{ Number(item.display_price ?? item.price).toFixed(2).split('.')[1] }}
                <span v-if="item.is_seckill" class="activity-old-price">¥{{ Number(item.price).toFixed(0) }}</span>
              </div>
              <div class="goods-actions">
                <div class="btn-icon fav" @click.stop="toggleFavorite(item)">
                  <van-icon :name="isFav(item.id) ? 'like' : 'like-o'" :color="isFav(item.id) ? '#ee0a24' : '#666'" />
                </div>
                <div class="btn-icon cart" @click.stop="handleAddToCart(item)">
                  <van-icon name="cart-o" />
                </div>
              </div>
            </div>
            <div v-if="item.is_seckill" class="goods-seckill-meta">{{ item.seckill_limit_per_user || 1 }}人限购 · 剩余 {{ item.display_stock }} 件</div>
          </div>
        </div>
      </div>
    </div>

    <div style="height: 60px;"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import draggable from 'vuedraggable'

const props = defineProps({
  isVip: Boolean,
  goodsList: { type: Array, default: () => [] },
  bannerList: { type: Array, default: () => [] },
  searchKeyword: { type: String, default: '' },
  currentCategory: { type: String, default: '' },
  filteredGoodsList: { type: Array, default: () => [] },
  currentMenu: { type: Array, default: () => [] },
  loadProducts: { type: Function, required: true },
  handleGridClick: { type: Function, required: true },
  getSeckillStatusTag: { type: Function, required: true },
  isFav: { type: Function, required: true },
  toggleFavorite: { type: Function, required: true },
  handleAddToCart: { type: Function, required: true },
  openProductDetail: { type: Function, required: true },
})

const emit = defineEmits(['update:searchKeyword', 'update:currentMenu'])

const menuProxy = computed({
  get: () => props.currentMenu,
  set: (value) => emit('update:currentMenu', value),
})

const updateSearchKeyword = (value) => emit('update:searchKeyword', value)
</script>
