<template>
  <div class="mobile-app">

    <!-- 顶部导航 -->
    <van-nav-bar
      class="mall-nav-bar"
      v-if="!showPaySuccess && !showOrderDetail && activeTab !== 2 && !showProductDetail && !showAllOrders"
      :title="pageTitle"
      fixed placeholder z-index="99"
      :left-arrow="activeTab !== 0"
      @click-left="onClickLeft"
      :style="{
        '--van-nav-bar-background': isVip ? '#2f2a27' : 'rgba(255, 250, 244, 0.94)',
        '--van-nav-bar-title-text-color': isVip ? '#f7e6b6' : '#2c1b16',
        '--van-nav-bar-icon-color': isVip ? '#f7e6b6' : '#7f5d50'
      }"
    />

    <!-- ==================== Tab 0: 首页 ==================== -->
    <div v-if="activeTab === 0 && !showPaySuccess && !showOrderDetail && !showAllOrders" class="tab-page">
      <div class="header-search-box home-search-shell" :style="{ background: isVip ? '#2f2a27' : 'transparent' }">
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
          <van-search v-model="searchKeyword" placeholder="搜手机、电脑、耳机..." shape="round" background="transparent" class="home-search-input" />
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
        <van-search v-model="searchKeyword" placeholder="搜手机、电脑..." shape="round" background="transparent" style="flex:1;" />
        <van-icon name="replay" color="white" size="24" @click="loadProducts(true)" style="margin-left:10px; opacity:0.9;" />
      </div>

      <div class="banner-box">
        <van-swipe :autoplay="3000" indicator-color="white" class="my-swipe">
          <van-swipe-item v-for="b in bannerList" :key="b.id"><img :src="b.img" class="banner-img" /></van-swipe-item>
          <van-swipe-item v-if="bannerList.length === 0"><div class="empty-banner">暂无轮播图，请去后台添加</div></van-swipe-item>
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
        <draggable v-model="currentMenu" class="drag-grid" item-key="text" :animation="200">
          <template #item="{element}">
            <div class="drag-item" @click="handleGridClick(element)">
              <div class="icon-circle"><van-icon :name="element.icon" size="24" :color="isVip ? '#dda246' : '#ee0a24'" /></div>
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
             <div class="img-wrapper" style="position:relative;"><img :src="item.img" /><div v-if="item.display_stock === 0" style="position:absolute;inset:0;background:rgba(0,0,0,0.45);display:flex;align-items:center;justify-content:center;border-radius:8px 8px 0 0;"><span style="color:white;font-size:16px;font-weight:bold;">售罄</span></div></div>
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
                 <div class="price">¥ <span class="num">{{ Number(item.display_price ?? item.price).toFixed(0) }}</span>.{{ Number(item.display_price ?? item.price).toFixed(2).split('.')[1] }}<span v-if="item.is_seckill" class="activity-old-price">¥{{ Number(item.price).toFixed(0) }}</span></div>
                 <div class="goods-actions">
                    <div class="btn-icon fav" @click.stop="toggleFavorite(item)"><van-icon :name="isFav(item.id) ? 'like' : 'like-o'" :color="isFav(item.id) ? '#ee0a24' : '#666'" /></div>
                    <div v-if="!item.is_seckill" class="btn-icon cart" @click.stop="handleAddToCart(item)"><van-icon name="cart-o" /></div>
                 </div>
               </div>
               <div v-if="item.is_seckill" class="goods-seckill-meta">{{ item.seckill_limit_per_user || 1 }}人限购 · 剩余 {{ item.display_stock }} 件</div>
             </div>
          </div>
        </div>
      </div>
      <div style="height: 60px;"></div>
    </div>

    <!-- ==================== Tab 1: 购物车 ==================== -->
    <div v-else-if="activeTab === 1 && !showPaySuccess && !showOrderDetail && !showAllOrders" class="tab-page" style="padding-bottom:120px;">
      <div v-if="cartList.length === 0" class="empty-cart"><van-empty description="老板，您还没挑东西呢！" /><van-button color="linear-gradient(to right, #ff6034, #ee0a24)" round size="small" @click="activeTab=0">去逛逛</van-button></div>
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
            <van-checkbox v-model="isAllChecked" checked-color="#ee0a24" @click="toggleAllCheck">全选</van-checkbox>
          </label>
          <div class="cart-submit-price">
            <span class="cart-submit-label">合计</span>
            <span class="cart-submit-value">¥ {{ calculateCartFinalPrice }}</span>
          </div>
          <van-button round color="linear-gradient(135deg, #ff8652, #e84d2a)" class="cart-submit-btn" @click="handleCartCheckout">去结算</van-button>
        </div>
      </div>
    </div>

    <!-- ==================== Tab 2: 会员中心 ==================== -->
    <div v-else-if="activeTab === 2 && !showPaySuccess && !showOrderDetail && !showAllOrders" class="tab-page">
      <div v-if="!currentUser" class="login-wrapper">
        <div class="login-card">
          <div class="login-header"><h3>Smart Mall</h3><p>登录享受更多权益</p></div>
          <van-tabs v-model:active="loginTab" color="#ee0a24" title-active-color="#ee0a24">
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
              <img :src="currentUser.avatar" class="avatar" @click="$refs.avatarInput.click()" style="cursor:pointer;" />
              <div style="position:absolute;bottom:0;right:0;background:rgba(0,0,0,0.45);border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;" @click="$refs.avatarInput.click()"><van-icon name="photograph" color="white" size="12" /></div>
              <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="handleAvatarChange" />
            </div>
            <div class="text-info">
              <div class="nickname">
                {{ currentUser.nickname }}
                <van-icon name="edit" style="margin-left: 8px; font-size: 16px; opacity: 0.8;" @click.stop="openEditName" />
                <span style="font-size:12px; font-weight:normal; margin-left:10px; opacity:0.6; border:1px solid rgba(255,255,255,0.5); padding:0px 6px; border-radius:10px; cursor:pointer;" @click.stop="logout"><van-icon name="exchange" /> 切换</span>
              </div>
              <div class="level-badge"><van-icon name="gem" /> {{ vipLevelName }}</div>
            </div>
          </div>
          <div class="member-hero-meta">
            <div class="hero-desc-row">
              <div class="hero-desc">{{ heroText }}</div>
              <van-icon name="edit" class="hero-desc-edit-btn" @click.stop="openEditHeroText" />
            </div>
            <div
              class="hero-desc hero-desc-editable"
              contenteditable="true"
              spellcheck="false"
            >鸟为什么会飞</div>
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
            <div class="quick-value">{{ myOrderList.filter(o => o.status === 1 || o.status === 5).length }}</div>
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
            <van-cell title="我的地址" icon="location-o" is-link @click="showAddressManager=true" />
            <van-cell title="修改密码" icon="shield-o" is-link @click="openChangePasswordDialog" />
            <van-cell title="余额充值" icon="gold-coin-o" is-link @click="openRecharge" />
            <van-cell title="我的收藏" icon="like-o" is-link @click="showFavorites=true; loadFavorites()" />
          </van-cell-group>
        </div>
        <div class="order-section">
          <!-- 🔥 修改：点击“查看全部”打开独立弹窗 🔥 -->
          <div class="sec-head" @click="openOrderList"><span class="sec-title">我的订单</span><span class="sec-more">查看全部 ></span></div>

          <div v-if="!myOrderList || myOrderList.length === 0" class="empty-order-box"><van-icon name="orders-o" size="40" color="#ddd" /><p>这里空空如也，快去买点东西吧~</p></div>
          <!-- 🔥 修改：只显示最近2条，更多请点击全部 🔥 -->
          <div v-for="order in myOrderList.slice(0, 2)" :key="order.id" class="jd-order-card" @click="viewOrderDetail(order.id)">
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

    <!-- ==================== Tab 3: 拼团大厅 ==================== -->
    <div v-else-if="activeTab === 3 && !showPaySuccess && !showOrderDetail" class="tab-page activity-page" style="padding-bottom:60px;">
      <div class="activity-hero group-hero">
        <div class="activity-kicker">Group Buying Hall</div>
        <h2 class="activity-title">拼团大厅</h2>
        <p class="activity-desc">{{ systemConfig.group_buy_people }}人成团 · 享{{ systemConfig.group_buy_discount * 10 }}折优惠 · 越多人越划算</p>
        <div class="activity-stat-row">
          <div class="activity-stat-card">
            <span class="activity-stat-num">{{ filteredGoodsList.length }}</span>
            <span class="activity-stat-label">可拼商品</span>
          </div>
          <div class="activity-stat-card">
            <span class="activity-stat-num">{{ systemConfig.group_buy_people }}</span>
            <span class="activity-stat-label">成团人数</span>
          </div>
          <div class="activity-stat-card hot">
            <span class="activity-stat-num">{{ Math.round(systemConfig.group_buy_discount * 100) }}%</span>
            <span class="activity-stat-label">拼团价率</span>
          </div>
        </div>
      </div>
      <div class="goods-container activity-list">
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
      </div>
    </div>

    <!-- Tab 4: 秒杀大厅 -->
    <div v-else-if="activeTab === 4 && !showPaySuccess && !showOrderDetail" class="tab-page activity-page" style="padding-bottom:60px;">
      <div class="activity-hero seckill-hero">
        <div class="activity-kicker">Flash Sale</div>
        <h2 class="activity-title">疯狂秒杀</h2>
        <p class="activity-desc">限时限量 · 手慢无 · 趁倒计时结束前抢到心仪单品</p>
        <div class="activity-stat-row">
          <div class="activity-stat-card">
            <span class="activity-stat-num">{{ filteredGoodsList.length }}</span>
            <span class="activity-stat-label">秒杀商品</span>
          </div>
          <div class="activity-stat-card">
            <span class="activity-stat-num">{{ systemConfig.seckill_time_limit }}</span>
            <span class="activity-stat-label">限时分钟</span>
          </div>
          <div class="activity-stat-card hot">
            <span class="activity-stat-num">HOT</span>
            <span class="activity-stat-label">火热抢购</span>
          </div>
        </div>
      </div>
      <div class="goods-container activity-list">
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
      </div>
    </div>

    <!-- 底部导航 -->
    <van-tabbar v-if="!showPaySuccess && !showOrderDetail && !showProductDetail && !showAllOrders" class="mall-tabbar" v-model="activeTab" :active-color="isVip ? '#dda246' : '#ee0a24'" inactive-color="#999">
      <van-tabbar-item icon="home-o" @click="currentCategory='🔥 爆款推荐'">首页</van-tabbar-item>
      <van-tabbar-item icon="shopping-cart-o" :badge="cartCount>0?cartCount:null">购物车</van-tabbar-item>
      <van-tabbar-item icon="user-o" :dot="!currentUser">我的</van-tabbar-item>
    </van-tabbar>

    <!-- 弹窗组件群 -->
    <van-dialog v-model:show="showGroupChoiceDialog" class-name="mall-dialog" title="拼团方式" :show-confirm-button="false" :show-cancel-button="false">
      <div style="padding:20px; text-align:center; color:#666;">
        <div style="margin-bottom:16px;">请选择您是要发起新的拼团，还是加入好友的团？</div>
        <div style="display:flex; flex-direction:column; gap:12px;">
          <van-button round color="linear-gradient(135deg, #ff8652, #e84d2a)" @click="startNewGroup">我要开团</van-button>
          <van-button round plain color="#1989fa" @click="openJoinGroupDialog">我有拼团码</van-button>
          <van-button round plain color="#07c160" @click="buyGroupItemDirectly">直接购买</van-button>
          <van-button round plain color="#969799" @click="cancelGroupChoice">退出拼团</van-button>
        </div>
      </div>
    </van-dialog>
    <van-dialog v-model:show="showJoinGroupInput" title="输入拼团码" show-cancel-button @confirm="joinGroup"><div style="padding:20px;"><van-field v-model="inputGroupCode" placeholder="请输入6位拼团码" input-align="center" style="background:#f5f5f5; border-radius:8px;" /></div></van-dialog>

    <van-dialog v-model:show="showBuyDialog" class-name="mall-dialog" title="确认付款" :show-confirm-button="false" show-cancel-button>
      <div class="pay-dialog-content glass-panel">
        <div class="price-big">¥ {{ calculateFinalPrice }}</div>
        <div class="pay-row" @click="showAddressManager=true"><span class="label">📍 收货地址</span><span class="value link">{{ selectedAddress?selectedAddress.name:'去添加' }} ></span></div>
        <div v-if="!selectedItem?.is_seckill" class="pay-row" @click="openCheckoutCouponSelector"><span class="label">🎟️ 优惠券</span><span class="value link" :class="{red: selectedCoupon}">{{ selectedCoupon?'-¥'+selectedCoupon.amount:'选择' }} ></span></div>
        <div v-if="!selectedItem?.is_seckill" class="pay-row"><span class="label">🪙 积分抵扣</span><van-switch v-model="usePoints" size="20px" active-color="#ee0a24" /></div>
        <div v-if="selectedItem?.is_seckill" class="pay-row pay-row-note"><span class="label">秒杀规则</span><span class="value">不支持优惠券与积分</span></div>
        <div class="pay-qr-box">
          <div class="pay-qr-tip">请使用微信或支付宝扫码支付</div>
          <img src="https://api.qrserver.com/v1/create-qr-code/?size=170x170&data=SmartMallSingleOrder" class="pay-qr-img" />
          <van-button block round color="linear-gradient(135deg, #24c07b, #07c160)" class="pay-confirm-btn" @click="confirmSingleOrder">我已确认支付</van-button>
        </div>
      </div>
    </van-dialog>

    <van-dialog v-model:show="showCartConfirm" class-name="mall-dialog" title="购物车结算" :show-confirm-button="false" show-cancel-button>
      <div class="pay-dialog-content glass-panel">
        <div class="price-big">¥ {{ calculateCartFinalPrice }}</div>
        <div class="pay-row" @click="showAddressManager=true"><span class="label">📍 收货地址</span><span class="value link">{{ selectedAddress?selectedAddress.name:'去添加' }} ></span></div>
        <div class="pay-row" @click="openCheckoutCouponSelector"><span class="label">🎟️ 优惠券</span><span class="value link" :class="{red: selectedCoupon}">{{ selectedCoupon?'-¥'+selectedCoupon.amount:'选择' }} ></span></div>
        <div class="pay-row"><span class="label">🪙 积分抵扣</span><van-switch v-model="usePoints" size="20px" active-color="#ee0a24" /></div>
        <div class="pay-qr-box">
          <div class="pay-qr-tip">请使用微信或支付宝扫码支付</div>
          <img src="https://api.qrserver.com/v1/create-qr-code/?size=170x170&data=SmartMallCartCheckout" class="pay-qr-img" />
          <van-button block round color="linear-gradient(135deg, #24c07b, #07c160)" class="pay-confirm-btn" @click="confirmCartOrder">我已确认支付</van-button>
        </div>
      </div>
    </van-dialog>

    <!-- 🔥 新增：全部订单列表弹窗 (含Tabs) 🔥 -->
    <van-popup v-model:show="showAllOrders" class="sheet-popup mobile-shell-popup" position="bottom" :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }">
        <div class="popup-mobile-shell all-orders-shell">
        <van-nav-bar title="我的订单" fixed placeholder z-index="100" left-arrow @click-left="showAllOrders=false" />
        <van-tabs v-model:active="activeOrderTab" sticky offset-top="46" background="#fff" color="#ee0a24" title-active-color="#ee0a24">
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

    <!-- 全商品详情弹窗 -->
    <van-popup v-model:show="showProductDetail" class="sheet-popup mobile-shell-popup" position="bottom" :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }" closeable>
        <div v-if="selectedItem" class="popup-mobile-shell product-detail-shell">
            <div style="height:350px; position:relative;">
                <img :src="selectedItem.img" style="width:100%; height:100%; object-fit:cover;">
                <div v-if="isSeckillItem" class="seckill-bar-modal">
                    <div class="sk-info"><div class="sk-title">⚡ 疯狂秒杀</div><div class="sk-sub">{{ getSeckillStatusTag(selectedItem) }} · 每人限购 {{ selectedItem.seckill_limit_per_user || 1 }} 件</div></div>
                    <div class="sk-countdown"><div style="font-size:10px; margin-bottom:2px; opacity:0.8;">{{ currentSeckillStatus === 'upcoming' ? '距开始仅剩' : '距结束仅剩' }}</div><van-count-down :time="seckillTimeLeft" format="DD 天 HH : mm : ss" style="color:#fff000; font-weight:bold; font-size:20px; font-family:monospace;" @finish="handleSeckillFinish" /></div>
                </div>
            </div>

            <div class="popup-mobile-content product-detail-content" style="padding:20px; background:white; flex:1; overflow-y:auto;">
                <div style="font-size:20px; margin-bottom:10px; font-weight:bold; line-height:1.4;">{{ selectedItem.title }}</div>
                <div style="color:#ee0a24; font-size:28px; font-weight:bold; margin-bottom:15px;">
                    ¥ {{ Number(selectedItem.display_price ?? selectedItem.price).toFixed(2) }}
                    <span v-if="isSeckillItem" style="font-size:14px; color:#999; text-decoration:line-through; font-weight:normal; margin-left:10px;">¥{{ Number(selectedItem.price).toFixed(2) }}</span>
                </div>

                <div v-if="isSeckillItem" style="background:#fff7f7; border:1px solid #ffebeb; padding:15px; border-radius:10px; margin-bottom:20px;">
                    <div style="font-weight:bold; color:#ee0a24; margin-bottom:5px;"><van-icon name="warning-o" /> 秒杀规则：</div>
                    <div style="font-size:13px; color:#666; line-height:1.6;">1. 秒杀商品仅可直接购买，不支持加入购物车。<br>2. 每人限购 {{ selectedItem.seckill_limit_per_user || 1 }} 件，当前剩余 {{ selectedItem.display_stock }} 件。<br>3. 秒杀商品不支持优惠券和积分抵扣，活动结束后自动恢复常规展示。</div>
                </div>
                <div v-if="isSeckillItem" class="seckill-detail-grid">
                    <div class="seckill-detail-card">
                        <div class="seckill-detail-label">活动状态</div>
                        <div class="seckill-detail-value">{{ getSeckillStatusTag(selectedItem) }}</div>
                    </div>
                    <div class="seckill-detail-card">
                        <div class="seckill-detail-label">每人限购</div>
                        <div class="seckill-detail-value">{{ selectedItem.seckill_limit_per_user || 1 }} 件</div>
                    </div>
                    <div class="seckill-detail-card">
                        <div class="seckill-detail-label">剩余库存</div>
                        <div class="seckill-detail-value">{{ selectedItem.display_stock }} 件</div>
                    </div>
                    <div class="seckill-detail-card">
                        <div class="seckill-detail-label">活动时间</div>
                        <div class="seckill-detail-value mini">{{ selectedItem.seckill_start_at || '立即开始' }} - {{ selectedItem.seckill_end_at || '售完为止' }}</div>
                    </div>
                </div>

                <div style="margin-top:10px;">
                    <h4 style="margin-bottom:10px; border-left:4px solid #ee0a24; padding-left:10px;">商品详情</h4>
                    <p style="color:#666; font-size:14px; line-height:1.6; white-space: pre-wrap;">{{ selectedItem.description || '暂无商品介绍，请联系客服咨询详情。' }}</p>
                </div>

                <div style="margin-top:20px;">
                    <h4 style="margin-bottom:10px; border-left:4px solid #ee0a24; padding-left:10px;">用户评价 <span style="font-weight:normal;font-size:13px;color:#999;">（{{ productComments.length }}条）</span></h4>
                    <div v-if="productComments.length === 0" style="text-align:center;color:#ccc;padding:20px 0;"><van-icon name="comment-o" size="32" /><p style="margin-top:8px;font-size:13px;">暂无评价</p></div>
                    <div v-for="c in productComments" :key="c.id" style="border-bottom:1px solid #f5f5f5;padding:12px 0;">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                            <img :src="c.avatar" style="width:32px;height:32px;border-radius:50%;object-fit:cover;" />
                            <span style="font-size:13px;font-weight:500;">{{ c.user }}</span>
                            <van-rate :model-value="c.rating" readonly :size="12" color="#ffd21e" void-color="#eee" style="margin-left:auto;" />
                        </div>
                        <p style="font-size:13px;color:#555;margin:0;line-height:1.6;">{{ c.content }}</p>
                        <p style="font-size:11px;color:#bbb;margin:4px 0 0;">{{ c.date }}</p>
                    </div>
                </div>
            </div>

            <div class="product-detail-footer" style="padding:10px 20px; background:white; display:flex; gap:15px; border-top:1px solid #eee;">
                <van-button v-if="!isSeckillItem" block round color="#ff976a" :disabled="selectedItem.stock === 0" @click="handleAddToCart(selectedItem)">加入购物车</van-button>
                <div class="btn-icon fav" @click.stop="toggleFavorite(selectedItem)" style="width:44px;height:44px;border:1px solid #eee;margin-right:-5px;"><van-icon :name="isFav(selectedItem.id) ? 'like' : 'like-o'" :color="isFav(selectedItem.id) ? '#ee0a24' : '#666'" size="20" /></div>
                <template v-if="selectedItemIsGroup && !isSeckillItem">
                    <van-button block round plain color="#ee0a24" :disabled="selectedItem.stock === 0" @click="buyGroupItemDirectly">
                        {{ selectedItem.stock === 0 ? '已售罄' : '直接购买' }}
                    </van-button>
                    <van-button block round color="linear-gradient(135deg, #ff8652, #e84d2a)" :disabled="selectedItem.stock === 0" @click="triggerBuyLogic">
                        {{ selectedItem.stock === 0 ? '已售罄' : '去开团/参团' }}
                    </van-button>
                </template>
                <van-button v-else block round :color="(isSeckillItem && !canBuySeckillNow) || selectedItem.display_stock === 0 || selectedItem.stock === 0 ? '#ccc' : (isSeckillItem ? 'linear-gradient(to right, #ff6034, #ee0a24)' : '#ee0a24')" :disabled="(isSeckillItem && !canBuySeckillNow) || (isSeckillItem ? selectedItem.display_stock === 0 : selectedItem.stock === 0)" @click="triggerBuyLogic">
                    {{ isSeckillItem ? getSeckillStatusText(selectedItem) : (selectedItem.stock === 0 ? '已售罄' : '立即购买') }}
                </van-button>
            </div>
        </div>
    </van-popup>

    <van-popup v-model:show="showCoupon" class="sheet-popup" position="bottom" round closeable :style="{ height: '60%', background: '#f7f8fa' }">
      <div style="padding: 15px 15px 30px;">
        <h3 style="text-align:center; margin-top: 10px; margin-bottom: 20px; font-weight: 600; color: #333;">🧧 领券中心</h3>
        <div v-if="coupons.length === 0" style="text-align:center;color:gray;margin-top:50px;">暂无可用优惠券</div>
        <div v-for="c in coupons" :key="c.id" class="coupon-card">
          <div class="c-left" :class="{ 'got': c.got }"><div class="c-price"><span>¥</span>{{ c.amount }}</div><div class="c-cond">{{ c.desc }}</div><div class="circle-top"></div><div class="circle-bottom"></div></div>
          <div class="c-right"><div class="c-info"><div class="c-name"><span class="c-tag" :class="{'vip-tag': c.limit_level > 1}">{{ c.limit_level > 1 ? 'VIP专享' : '通用' }}</span>{{ c.name }}</div><div class="c-date">有效期至 2025.12.31</div></div><van-button size="small" round :color="c.got ? '#ebedf0' : 'linear-gradient(to right, #ff6034, #ee0a24)'" :style="{ color: c.got ? '#969799' : 'white', fontWeight: 'bold', height: '28px', padding: '0 15px' }" :disabled="c.got" @click="handleGetCoupon(c)">{{ c.got ? '已领取' : '立即领取' }}</van-button></div>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showOwnedCouponsPopup" class="sheet-popup" position="bottom" round :style="{ height: '50%', background: '#f7f8fa' }">
      <div style="padding: 15px;">
        <h3 style="text-align:center; margin-bottom:20px;">我的卡包</h3>
        <div v-if="myUsableCoupons.length === 0" style="text-align:center;color:gray;margin-top:50px;"><van-icon name="coupon-o" size="40" /><p>暂无优惠券</p></div>
        <div v-for="c in myUsableCoupons" :key="c.id" class="coupon-card">
          <div class="c-left"><div class="c-price"><span>¥</span>{{ c.amount }}</div><div class="c-cond">满{{ c.min_spend }}可用</div><div class="circle-top"></div><div class="circle-bottom"></div></div>
          <div class="c-right"><div class="c-info"><div class="c-name">{{ c.name }}</div><div class="c-date">有效期至 2025.12.31</div></div><van-button size="small" round color="#ee0a24" @click="showOwnedCouponsPopup=false; activeTab=0">去使用</van-button></div>
        </div>
      </div>
    </van-popup>

    <div v-if="showPaySuccess" class="full-page-success">
      <div class="success-shell">
      <div class="success-icon-box"><van-icon name="checked" color="white" size="60" /></div><h2 class="success-title">支付成功</h2>
      <div v-if="lastOrderGroupCode" style="text-align:center;margin:10px 0;padding:10px;background:#f9f9f9;border-radius:8px;"><div>您的拼团码:</div><div style="font-size:24px;font-weight:bold;color:#ee0a24;letter-spacing:2px;">{{ lastOrderGroupCode }}</div><div style="font-size:12px;color:gray;">快去分享给好友参团吧!</div></div>
      <div class="success-subtitle">订单已经提交，商家正在为你准备发货。</div>
      <div class="succ-price">¥ {{ lastPaidAmount }}</div>
      <div class="success-action-row"><van-button plain block round class="success-secondary-btn" style="flex:1" @click="finishPayment('home')">返回首页</van-button><van-button color="#07c160" block round class="success-primary-btn" style="flex:1" @click="finishPayment('order')">查看订单</van-button></div>
      </div>
    </div>

    <div v-if="showOrderDetail" class="full-page-detail">
      <div class="detail-page-shell">
      <van-nav-bar title="订单详情" left-arrow @click-left="showOrderDetail=false" />
      <div class="detail-status-header"><div class="status-big"><van-icon name="logistics" size="24" />{{ getStatusText(currentOrderDetail.status) }}</div><div class="status-desc">感谢您在 Smart Mall 购物，欢迎再次光临</div><div class="detail-status-pills"><span class="detail-pill">官方自营</span><span class="detail-pill">物流可追踪</span><span class="detail-pill">售后无忧</span></div></div>
      <div v-if="currentOrderDetail" class="detail-page-content" style="margin-top: -30px; position: relative; z-index: 2;">
        <div v-if="currentOrderDetail.group_code" class="card detail-code-card" style="margin-top:-20px;text-align:center;padding:15px;"><div class="detail-code-main">拼团码：{{ currentOrderDetail.group_code }}</div><div class="detail-code-sub">状态：{{ currentOrderDetail.status===5?'待成团':'拼团成功' }}</div></div>
        <div class="card detail-address-card"><div class="icon-side"><van-icon name="location" color="#ee0a24" size="24" /></div><div class="text-side"><div class="addr-title">收货信息</div><div class="addr-text">{{ currentOrderDetail.address }}</div></div></div>
        <div class="card detail-goods-card"><div class="shop-line"><van-icon name="shop-o" /> Smart Mall 自营店</div><div class="goods-row"><img :src="currentOrderDetail.img" class="detail-goods-img" /><div class="g-right"><div class="g-title">{{ currentOrderDetail.title }}</div><div class="g-sub">官方直发 · 品质保障 · 支持售后</div><div class="g-price">¥ {{ currentOrderDetail.amount.toFixed(2) }}</div></div></div><div class="contact-line"><van-button size="small" icon="service-o" round>联系客服</van-button><van-button size="small" icon="phone-o" round>拨打电话</van-button></div></div>
        <div class="card detail-meta"><div class="meta-row"><span>订单编号</span><span>{{ currentOrderDetail.no }}</span></div><div class="meta-row"><span>下单时间</span><span>{{ currentOrderDetail.date }}</span></div><div class="meta-row"><span>支付方式</span><span>在线支付</span></div></div>

        <div v-if="logisticsTraces.length > 0" class="card detail-logistics-card" style="padding:15px;">
          <div class="detail-logistics-title">物流轨迹</div>
          <div v-for="(t, i) in logisticsTraces" :key="i" class="detail-logistics-row">
            <div class="detail-logistics-line">
              <div :class="['detail-logistics-dot', { active: i===0 }]"></div>
              <div v-if="i < logisticsTraces.length-1" class="detail-logistics-stick"></div>
            </div>
            <div class="detail-logistics-copy">
              <div :class="['detail-logistics-desc', { active: i===0 }]">{{ t.desc }}</div>
              <div class="detail-logistics-time">{{ t.time }}</div>
            </div>
          </div>
        </div>

        <div v-if="currentOrderDetail.status === 1" class="detail-action-wrap" style="padding:0 0 20px;">
          <van-button block round plain type="danger" @click="cancelOrder(currentOrderDetail)">取消订单</van-button>
        </div>
      </div>
      </div>
    </div>

    <van-dialog v-model:show="showRecharge" class-name="mall-dialog" title="余额充值" :show-confirm-button="false">
      <div style="padding:20px; text-align:center;"><van-field v-model="rechargeAmount" type="number" label="充值金额" placeholder="请输入金额" size="large" prefix="¥" class="beauty-input" /><div v-if="rechargeAmount > 0" class="pay-qr-box"><div class="pay-qr-tip">请使用微信或支付宝扫码支付</div><img src="https://api.qrserver.com/v1/create-qr-code/?size=170x170&data=SmartMallRecharge" class="pay-qr-img" /><van-button block round color="linear-gradient(135deg, #24c07b, #07c160)" class="pay-confirm-btn" @click="submitRecharge">我已确认支付</van-button></div></div>
    </van-dialog>

    <van-popup v-model:show="showMyCouponSelector" position="bottom" round :style="{ height: '40%' }"><div style="padding:20px;"><h3 style="text-align:center;">选择优惠券</h3><van-cell-group><van-cell v-for="c in myUsableCoupons" :key="c.id" :title="c.name" :value="`- ¥${c.amount}`" clickable @click="selectedCoupon=c; showMyCouponSelector=false" /><van-cell title="不使用优惠券" clickable @click="selectedCoupon=null; showMyCouponSelector=false" /></van-cell-group></div></van-popup>
    <van-popup v-model:show="showMoreMenu" position="bottom" round :style="{ height: '40%' }"><div style="padding:20px;"><h3 style="text-align:center;margin-bottom:10px;">更多服务</h3><van-grid :column-num="4" clickable><van-grid-item v-for="(item, i) in moreMenuPool" :key="i" :icon="item.icon" :text="item.text" @click="replaceMenuItem(item)" /></van-grid></div></van-popup>
    <van-popup v-model:show="showAddressManager" position="bottom" :style="{ height: '60%' }">
      <div style="padding:15px;">
        <h3>地址管理</h3>
        <van-radio-group v-model="selectedAddrId">
          <div
            v-for="addr in addressList"
            :key="addr.id"
            class="addr-box"
            @click="selectedAddrId=addr.id;showAddressManager=false"
          >
            <van-radio :name="addr.id" style="margin-right:10px;"></van-radio>
            <div class="addr-content">
              <div class="addr-topline">
                <b>{{ addr.name }} {{ addr.phone }}</b>
                <van-tag v-if="addr.is_default" plain type="danger" round>默认地址</van-tag>
              </div>
              <span class="addr-detail">{{ addr.detail }}</span>
              <div class="addr-actions">
                <van-button
                  v-if="!addr.is_default"
                  plain
                  round
                  size="small"
                  type="primary"
                  @click.stop="setDefaultAddress(addr.id)"
                >
                  设为默认
                </van-button>
              </div>
            </div>
          </div>
        </van-radio-group>
        <van-button type="danger" block round style="margin-top:20px;" @click="showAddAddrForm=true">➕ 新增</van-button>
      </div>
    </van-popup>
    <van-dialog v-model:show="showAddAddrForm" title="新增地址" show-cancel-button @confirm="saveAddress">
      <van-cell-group inset>
        <van-field v-model="newAddr.name" label="姓名" />
        <van-field v-model="newAddr.phone" label="电话" />
        <van-field v-model="newAddr.detail" label="地址" />
        <van-cell title="设为默认地址" center>
          <template #right-icon>
            <van-switch v-model="newAddr.is_default" size="20" />
          </template>
        </van-cell>
      </van-cell-group>
    </van-dialog>
    <van-popup v-model:show="showFavorites" position="bottom" round :style="{ height: '60%' }">
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
    <van-dialog v-model:show="showCommentDialog" title="商品评价" show-cancel-button @confirm="submitComment"><div style="padding:20px;text-align:center;"><van-rate v-model="commentForm.rating" :size="30" color="#ffd21e" void-icon="star" void-color="#eee" /><van-field v-model="commentForm.content" rows="3" autosize label="" type="textarea" placeholder="请输入您的使用心得..." class="beauty-input" style="margin-top:15px;" /></div></van-dialog>
    <van-dialog v-model:show="showEditNameDialog" title="修改昵称" show-cancel-button @confirm="submitEditName"><div style="padding: 20px;"><van-field v-model="editingName" placeholder="请输入新昵称" class="beauty-input" /></div></van-dialog>
    <van-dialog v-model:show="showChangePasswordDialog" title="修改密码" show-cancel-button @confirm="submitChangePassword">
      <div style="padding: 20px;">
        <van-field v-model="changePasswordForm.old_password" type="password" label="原密码" placeholder="请输入原密码" class="beauty-input" />
        <van-field v-model="changePasswordForm.new_password" type="password" label="新密码" placeholder="至少 6 位" class="beauty-input" />
        <van-field v-model="changePasswordForm.confirm_password" type="password" label="确认密码" placeholder="请再次输入新密码" class="beauty-input" />
      </div>
    </van-dialog>
    <van-dialog v-model:show="showEditHeroDialog" title="修改文案" show-cancel-button @confirm="submitEditHeroText"><div style="padding: 20px;"><van-field v-model="editingHeroText" maxlength="20" show-word-limit placeholder="请输入文案" class="beauty-input" /><div style="margin-top:8px;font-size:12px;color:#999;">最多 20 个字，超出不允许保存。</div></div></van-dialog>
    <van-dialog v-model:show="showPhonePopup" class-name="mall-dialog" title="拨打电话" show-cancel-button confirm-button-text="立刻拨打" @confirm="callServicePhone">
      <div style="padding: 20px; text-align: center;">
        <div style="font-size: 14px; color: #8a6b5a;">售后服务电话</div>
        <div style="margin-top: 10px; font-size: 26px; font-weight: 800; color: #2f221b; letter-spacing: 1px;">86-45224655</div>
      </div>
    </van-dialog>
    <van-dialog v-model:show="showQQPopup" class-name="mall-dialog" title="联系客服" show-cancel-button confirm-button-text="复制群号" @confirm="copyServiceQQ">
      <div style="padding: 20px; text-align: center;">
        <div style="font-size: 14px; color: #8a6b5a;">添加QQ群联系客服</div>
        <div style="margin-top: 10px; font-size: 26px; font-weight: 800; color: #2f221b; letter-spacing: 1px;">274625416</div>
      </div>
    </van-dialog>
    <van-popup v-model:show="showSigninPopup" round :style="{ padding: '30px', textAlign: 'center', width: '70%' }"><div style="color: #ee0a24; font-size: 50px; margin-bottom: 10px;"><van-icon name="gift" /></div><h2 style="margin: 0; color: #333;">签到成功!</h2><p style="color: #666; margin: 10px 0 20px;">恭喜获得 <span style="color: #ee0a24; font-weight: bold; font-size: 18px;">+100</span> 积分</p><van-button round block type="danger" @click="showSigninPopup = false">开心收下</van-button></van-popup>

    <!-- 会员升级弹窗 -->
    <van-popup v-model:show="showVipModal" position="bottom" round :style="{ height: '60%', background: '#f5f5f5' }">
      <div style="padding:20px;">
        <h3 style="text-align:center;margin-bottom:20px;">👑 会员升级中心</h3>
        <p style="text-align:center;color:gray;font-size:12px;margin-bottom:20px;">当前等级: {{ vipLevelName }}</p>
        <div class="vip-card gold" @click="selectVip(2)" :class="{disabled: currentUser.level >= 2}"><div class="v-left"><van-icon name="award" size="30" /><div><b>黄金VIP</b><div class="v-desc">全场9折 + 专属券</div></div></div><div class="v-price">¥ 99</div></div>
        <div class="vip-card diamond" @click="selectVip(3)" :class="{disabled: currentUser.level >= 3}"><div class="v-left"><van-icon name="gem" size="30" /><div><b>钻石VIP</b><div class="v-desc">全场8折 + 顶级券</div></div></div><div class="v-price">¥ 199</div></div>
      </div>
    </van-popup>

    <van-dialog v-model:show="showVipPayDialog" title="升级支付" :show-confirm-button="false">
      <div style="padding:20px; text-align:center;">
        <p style="font-size:16px; margin-bottom:10px;">升级为 <b style="color:#ee0a24">{{ pendingVipLevel === 2 ? '黄金VIP' : '钻石VIP' }}</b></p>
        <p style="font-size:24px; font-weight:bold; margin-bottom:20px;">¥ {{ pendingVipLevel === 2 ? '99.00' : '199.00' }}</p>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=VipUpgrade" style="width:150px; height:150px; margin:10px 0;" />
        <van-button type="success" block round @click="confirmVipPay" style="margin-top:20px;">✅ 我已扫码支付</van-button>
      </div>
    </van-dialog>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch, nextTick } from 'vue'
import { showToast, showDialog, showSuccessToast, showLoadingToast, closeToast } from 'vant'
import draggable from 'vuedraggable'
import { DEFAULT_CURRENT_MENU, DEFAULT_HERO_TEXT, DEFAULT_MORE_MENU_POOL, DEFAULT_SYSTEM_CONFIG, HERO_TEXT_MAX } from './constants/appData'
import { loginMobile, registerMobile, signinMobile } from './services/auth'
import { fetchBanners, fetchProductComments, fetchProducts, fetchSystemConfig } from './services/catalog'
import { fetchCouponMarket, fetchMyCoupons, claimCoupon } from './services/coupon'
import { rechargeBalance, updateProfile, updatePassword, uploadImage, upgradeVipLevel } from './services/profile'
import { fetchCartList, addCartItem, updateCartItem, checkoutCart } from './services/cart'
import { fetchAddressList, createAddress, switchDefaultAddress } from './services/address'
import { createOrder, fetchMyOrders, confirmReceipt, cancelOrderById, fetchOrderDetail, fetchOrderLogistics } from './services/order'
import { toggleFavoriteItem, fetchFavorites } from './services/favorite'
import { submitCommentByOrder } from './services/comment'

const activeTab = ref(0); const goodsList = ref([]); const currentUser = ref(null)
const loginTab = ref(0); const loginForm = reactive({username:'', password:''}); const regForm = reactive({username:'', password:''})
const myOrderList = ref([]); const cartList = ref([])
const showBuyDialog = ref(false); const showCartConfirm = ref(false); const selectedItem = ref(null); const showPaySuccess = ref(false)
const showOrderDetail = ref(false); const currentOrderDetail = ref(null)
const showAddressManager = ref(false); const showAddAddrForm = ref(false); const addressList = ref([]); const selectedAddrId = ref(null); const newAddr = reactive({name:'', phone:'', detail:'', is_default:false})
const currentCategory = ref('🔥 爆款推荐'); const searchKeyword = ref('')
const showRecharge = ref(false); const rechargeAmount = ref('')
const showCoupon = ref(false); const showMoreMenu = ref(false)
const time = ref(30 * 60 * 60 * 1000)
const isRefreshing = ref(false)
const usePoints = ref(false); const showMyCouponSelector = ref(false); const myUsableCoupons = ref([]); const selectedCoupon = ref(null)
const bannerList = ref([])
const showCommentDialog = ref(false); const commentForm = reactive({order_id: null, rating: 5, content: ''})
const showFavorites = ref(false); const favoriteList = ref([])
const lastPaidAmount = ref(0)
const showEditNameDialog = ref(false); const editingName = ref('')
const showChangePasswordDialog = ref(false); const changePasswordForm = reactive({old_password:'', new_password:'', confirm_password:''})
const showEditHeroDialog = ref(false); const editingHeroText = ref(DEFAULT_HERO_TEXT); const heroText = ref(DEFAULT_HERO_TEXT)
const logisticsTraces = ref([]); const showSigninPopup = ref(false)
const showPhonePopup = ref(false); const showQQPopup = ref(false)
const systemConfig = ref({ ...DEFAULT_SYSTEM_CONFIG })
const showGroupChoiceDialog = ref(false); const showJoinGroupInput = ref(false); const inputGroupCode = ref(''); const pendingGroupAction = ref(null); const lastOrderGroupCode = ref(null)
const isGroupBuyMode = ref(false)
const coupons = ref([])
const seckillTimer = ref(null)

// 收藏相关：新增 favIds
const favIds = ref([])
const isFav = (id) => favIds.value.includes(id)

// VIP相关
const showVipModal = ref(false)
const showVipPayDialog = ref(false)
const pendingVipLevel = ref(0)

// 🔥 新增：订单管理弹窗 🔥
const showAllOrders = ref(false)
const activeOrderTab = ref('all')

// 🔥 新增：商品详情 & 秒杀相关状态 🔥
const showProductDetail = ref(false)
const seckillTimeLeft = ref(0)
const isSeckillExpired = ref(false)
// 判断当前选中的商品是不是秒杀商品
const isSeckillItem = computed(() => selectedItem.value && !!selectedItem.value.is_seckill)
const selectedItemIsGroup = computed(() => selectedItem.value && selectedItem.value.category && selectedItem.value.category.includes('拼团'))
const currentSeckillStatus = computed(() => selectedItem.value?.seckill_status || 'none')
const canBuySeckillNow = computed(() => currentSeckillStatus.value === 'active')

// 新增：我的优惠券弹窗状态
const showOwnedCouponsPopup = ref(false)
const productComments = ref([])

const currentMenu = ref(DEFAULT_CURRENT_MENU.map(item => ({ ...item })))
const moreMenuPool = ref(DEFAULT_MORE_MENU_POOL.map(item => ({ ...item })))

const pageTitle = computed(() => ['Smart Mall', '购物车', '我的', '拼团大厅', '秒杀大厅'][activeTab.value])
const isVip = computed(() => currentUser.value && currentUser.value.level > 1)
const vipLevelName = computed(() => currentUser.value?.level==1?'普通':(currentUser.value?.level==2?'🏆 黄金VIP':'💎 钻石VIP'))
const selectedAddress = computed(() => addressList.value.find(a => a.id === selectedAddrId.value))
const cartCount = computed(() => cartList.value.length)
const isAllChecked = computed({ get: () => cartList.value.length>0 && cartList.value.every(item => item.checked), set: (val) => toggleAllCheck(val) })
const checkedCartItems = computed(() => cartList.value.filter(item => item.checked))
const cartTotalPrice = computed(() => { let t=0; let d=isVip.value?(currentUser.value.level==2?0.9:0.8):1; checkedCartItems.value.forEach(i=>{t+=(Number(i.price)||0)*(Number(i.num)||0)*d}); return t })
const singleBasePrice = computed(() => {
  if(!selectedItem.value) return 0;
  if(selectedItem.value.is_seckill) return Number(selectedItem.value.display_price ?? selectedItem.value.price)
  let d=1;
  if(isGroupBuyMode.value) d=systemConfig.value.group_buy_discount;
  else d=isVip.value?(currentUser.value.level==2?0.9:0.8):1;
  return Number(selectedItem.value.price) * d
})
const cartBasePrice = computed(() => cartTotalPrice.value)
const calculateCartFinalPrice = computed(() => calcFinal(cartBasePrice.value))
const calculateFinalPrice = computed(() => calcFinal(singleBasePrice.value))

const calcFinal = (basePrice) => {
  let price = Number(basePrice) || 0
  if (selectedCoupon.value) { if (price >= selectedCoupon.value.min_spend) price -= selectedCoupon.value.amount; else { showToast(`未满 ${selectedCoupon.value.min_spend} 元`); selectedCoupon.value = null } }
  if (price < 0) price = 0
  if (usePoints.value && currentUser.value && currentUser.value.points > 0) {
    let maxDeduct = price; let available = currentUser.value.points; let needed = Math.floor(maxDeduct * 100); let actual = Math.min(available, needed)
    price -= actual / 100
  }
  if (price < 0) price = 0
  return price.toFixed(2)
}

const getSeckillStatusText = (item) => {
  const status = item?.seckill_status || 'none'
  if (status === 'upcoming') return '即将开抢'
  if (status === 'active') return '立即秒杀'
  if (status === 'sold_out') return '已售罄'
  if (status === 'ended') return '活动结束'
  return '立即购买'
}

const getSeckillStatusTag = (item) => {
  const status = item?.seckill_status || 'none'
  if (status === 'upcoming') return '即将开始'
  if (status === 'active') return '秒杀中'
  if (status === 'sold_out') return '已售罄'
  if (status === 'ended') return '已结束'
  return '秒杀'
}

const getSeckillProgress = (item) => {
  if (!item?.is_seckill) return 0
  const total = Number(item.stock || 0)
  const remain = Number(item.display_stock ?? item.seckill_stock ?? 0)
  if (total <= 0) return 0
  return Math.min(100, Math.max(0, Math.round(((total - remain) / total) * 100)))
}

const getCountdownMs = (dateText) => {
  if (!dateText) return 0
  const target = new Date(String(dateText).replace(' ', 'T')).getTime()
  const diff = target - Date.now()
  return diff > 0 ? diff : 0
}

const refreshSelectedSeckillState = () => {
  if (!selectedItem.value?.is_seckill) return
  const now = Date.now()
  const startAt = selectedItem.value.seckill_start_at ? new Date(String(selectedItem.value.seckill_start_at).replace(' ', 'T')).getTime() : null
  const endAt = selectedItem.value.seckill_end_at ? new Date(String(selectedItem.value.seckill_end_at).replace(' ', 'T')).getTime() : null
  if (startAt && now < startAt) {
    selectedItem.value.seckill_status = 'upcoming'
    seckillTimeLeft.value = startAt - now
    isSeckillExpired.value = false
    return
  }
  if (endAt && now < endAt) {
    selectedItem.value.seckill_status = selectedItem.value.display_stock > 0 ? 'active' : 'sold_out'
    seckillTimeLeft.value = endAt - now
    isSeckillExpired.value = false
    return
  }
  if (selectedItem.value.display_stock <= 0) {
    selectedItem.value.seckill_status = 'sold_out'
  } else {
    selectedItem.value.seckill_status = 'ended'
  }
  seckillTimeLeft.value = 0
  isSeckillExpired.value = true
}

const filteredGoodsList = computed(() => {
  let list = goodsList.value
  if (searchKeyword.value) list = list.filter(item => item.title.includes(searchKeyword.value))
  if (activeTab.value === 3) return list.filter(i => i.category.includes('拼团'))
  if (activeTab.value === 4) return list.filter(i => i.category.includes('秒杀')) // Tab 4 是秒杀大厅
  if (currentCategory.value === '🔥 爆款推荐') return list
  return list.filter(i => i.category.includes(currentCategory.value))
})

// 🔥 核心：订单筛选逻辑 🔥
const filteredAllOrders = computed(() => {
    if(!myOrderList.value) return []
    const tab = activeOrderTab.value
    if(tab === 'all') return myOrderList.value
    if(tab === 'wait_ship') return myOrderList.value.filter(o => o.status === 1 || o.status === 5) // 待发货或拼团中
    if(tab === 'shipped') return myOrderList.value.filter(o => o.status === 2)
    if(tab === 'completed') return myOrderList.value.filter(o => o.status === 3 || o.status === 4)
    return myOrderList.value
})
const getStatusText = (s) => {
    if(s===1) return '等待发货'
    if(s===2) return '运输中'
    if(s===3) return '待评价'
    if(s===4) return '已完成'
    if(s===5) return '拼团中'
    if(s===6) return '拼团失败'
    return '未知状态'
}
const openOrderList = () => { showAllOrders.value = true }

const loadProducts = async (isManualRefresh = false) => {
  if (isManualRefresh) showLoadingToast({ message: '刷新中', forbidClick: true, duration: 0 })
  try {
    const res = await fetchProducts()
    if(res.data.code === 200) goodsList.value = res.data.data.filter(item => item.is_on_sale)
    const bannerRes = await fetchBanners()
    if(bannerRes.data.code === 200) bannerList.value = bannerRes.data.data
    const cfgRes = await fetchSystemConfig()
    if(cfgRes.data.code === 200) {
        systemConfig.value.group_buy_people = parseInt(cfgRes.data.data.group_buy_people)
        systemConfig.value.seckill_time_limit = parseInt(cfgRes.data.data.seckill_time_limit)
        systemConfig.value.group_buy_discount = parseFloat(cfgRes.data.data.group_buy_discount)
    }
    // 🔥 加载收藏列表 🔥
    if(currentUser.value) {
        loadFavorites();
        openMyCoupons(); // 预加载优惠券以显示数量
    }
  } catch(e) { console.error(e) }
  finally { if (isManualRefresh) closeToast() }
}
onMounted(loadProducts)
watch(showOrderDetail, async (visible) => {
  if (!visible) return
  await nextTick()
  bindOrderDetailContactActions()
})
watch(showProductDetail, (visible) => {
  if (!visible && seckillTimer.value) {
    clearInterval(seckillTimer.value)
    seckillTimer.value = null
  }
})

const onClickLeft = () => { activeTab.value = 0 }

// 🔥 修改：秒杀点击逻辑，进入大厅 🔥
const handleGridClick = (item) => {
  if (item.type === 'filter') {
      if(item.text === '拼团') { activeTab.value = 3; return }
      if(item.text === '秒杀') { activeTab.value = 4; return } // 跳转到秒杀大厅 Tab 4
      currentCategory.value = item.text;
      searchKeyword.value = '';
      showToast(`进入 ${item.text}`)
  }
  else if (item.type === 'action') { if (item.act === 'coupon') openCouponCenter(); if (item.act === 'recharge') openRecharge(); if (item.act === 'signin') handleSignin(); if (item.act === 'more') showMoreMenu.value = true }
}
const handleSignin = async () => {
  if(!currentUser.value) return showToast('请登录');
  const res = await signinMobile();
  if(res.data.code===200){ currentUser.value.points=res.data.points; showSigninPopup.value = true }
}

const openCouponCenter = async () => {
  showCoupon.value = true
  const res = await fetchCouponMarket()
  if(res.data.code === 200) {
      coupons.value = res.data.data.map(c => ({...c, got: false}))
      if(currentUser.value) {
          const myRes = await fetchMyCoupons()
          if(myRes.data.code===200) {
              const myCouponNames = myRes.data.data.map(mc => mc.name)
              coupons.value.forEach(c => {
                  if(myCouponNames.includes(c.name)) c.got = true
              })
          }
      }
  }
}

const handleGetCoupon = async (c) => {
  if(!currentUser.value) return showToast('请登录');
  try {
    const res = await claimCoupon(c.id);
    if(res.data.code===200) {
        showSuccessToast('领取成功');
        c.got = true;
        // 刷新我的优惠券列表以便数字更新
        openMyCoupons();
    }
    else { if(res.data.msg.includes('已领取')) c.got = true; showToast(res.data.msg) }
  } catch(e) { showToast('网络错误') }
}

const openMyCoupons = async () => {
    if(!currentUser.value) return;
    const res = await fetchMyCoupons();
    if(res.data.code===200){
        myUsableCoupons.value=res.data.data;
        // 这里的 showMyCouponSelector 原本是下单用的，如果是仅查看不需要设置true，除非是在下单界面
        // 这里只是为了刷新数据
    }
}
const openCheckoutCouponSelector = async () => {
    if(!currentUser.value) return showToast('请登录');
    await openMyCoupons();
    showMyCouponSelector.value = true;
}
const viewMyWalletCoupons = async () => {
    if(!currentUser.value) return showToast('请登录');
    await openMyCoupons();
    showOwnedCouponsPopup.value = true;
}

const replaceMenuItem = (newItem) => { const moreIndex = currentMenu.value.findIndex(i => i.act === 'more'); const targetIndex = moreIndex > 0 ? moreIndex - 1 : 0; const oldItem = currentMenu.value[targetIndex]; currentMenu.value[targetIndex] = newItem; moreMenuPool.value.push(oldItem); const poolIndex = moreMenuPool.value.indexOf(newItem); if (poolIndex > -1) moreMenuPool.value.splice(poolIndex, 1); showMoreMenu.value = false; showToast(`已切换为 ${newItem.text}`) }
const openRecharge = () => { if(!currentUser.value) return showToast('请登录'); rechargeAmount.value=''; showRecharge.value=true }
const submitRecharge = async () => {
  if (!rechargeAmount.value) return showToast('请输入金额');
  showLoadingToast({ message: '正在验证支付...', forbidClick: true, duration: 0 });
  try {
    await new Promise(r=>setTimeout(r,1500));
    const res = await rechargeBalance(rechargeAmount.value);
    closeToast();
    if (res.data.code === 200) { showSuccessToast('充值成功'); if (currentUser.value) { currentUser.value.balance = res.data.balance; } showRecharge.value = false; rechargeAmount.value = ''; } else { showToast(res.data.msg || '充值失败'); }
  } catch (e) { closeToast(); showToast('网络错误'); }
}
const onLogin = async () => { try { const res = await loginMobile(loginForm); if(res.data.code===200){ currentUser.value=res.data.data; heroText.value = res.data.data.hero_text || DEFAULT_HERO_TEXT; showSuccessToast('欢迎'); loadData(); } else showToast(res.data.msg) } catch(e){showToast('失败')} }
const onRegister = async () => {
  const res = await registerMobile(regForm)
  if(res.data.code===200){
    showSuccessToast(res.data.newcomer_coupon_received ? '注册成功，新人券已到账' : '注册成功')
    loginTab.value=0
    loginForm.username=regForm.username
  } else showToast(res.data.msg)
}
const logout = () => { showDialog({ title: '提示', message: '确定要切换账号吗？', showCancelButton: true }).then(() => { currentUser.value=null; heroText.value = DEFAULT_HERO_TEXT; loginForm.username=''; loginForm.password=''; cartList.value=[]; myOrderList=[]; favoriteList=[]; myUsableCoupons.value=[]; coupons.value.forEach(c=>c.got=false); favIds.value=[]; showSuccessToast('已退出'); activeTab.value = 2; }) }
const openEditName = () => { editingName.value = currentUser.value.nickname; showEditNameDialog.value = true }
const submitEditName = async () => { if(!editingName.value) return showToast('昵称不能为空'); const res = await updateProfile({ nickname: editingName.value }); if(res.data.code===200) { currentUser.value.nickname = editingName.value; showSuccessToast('修改成功') } else showToast(res.data.msg) }
const resetChangePasswordForm = () => { changePasswordForm.old_password=''; changePasswordForm.new_password=''; changePasswordForm.confirm_password='' }
const openChangePasswordDialog = () => { resetChangePasswordForm(); showChangePasswordDialog.value = true }
const submitChangePassword = async () => {
    if(!changePasswordForm.old_password || !changePasswordForm.new_password || !changePasswordForm.confirm_password) return showToast('请填写完整信息')
    if(changePasswordForm.new_password.length < 6) return showToast('新密码至少 6 位')
    if(changePasswordForm.new_password !== changePasswordForm.confirm_password) return showToast('两次输入的新密码不一致')
    const res = await updatePassword({
      old_password: changePasswordForm.old_password,
      new_password: changePasswordForm.new_password
    })
    if(res.data.code===200) {
      showChangePasswordDialog.value = false
      resetChangePasswordForm()
      showSuccessToast('密码已更新')
    } else {
      showToast(res.data.msg)
    }
}
const openEditHeroText = () => { editingHeroText.value = heroText.value; showEditHeroDialog.value = true }
const submitEditHeroText = () => {
    const text = (editingHeroText.value || '').trim()
    if(!text) return showToast('文案不能为空')
    if(text.length > HERO_TEXT_MAX) return showToast(`最多 ${HERO_TEXT_MAX} 个字`)
    updateProfile({ hero_text: text }).then((res) => {
        if(res.data.code===200) {
            heroText.value = res.data.hero_text || text
            if(currentUser.value) currentUser.value.hero_text = heroText.value
            showEditHeroDialog.value = false
            showSuccessToast('修改成功')
        } else {
            showToast(res.data.msg || '修改失败')
        }
    }).catch(() => showToast('网络错误'))
}
const bindOrderDetailContactActions = () => {
    const buttons = document.querySelectorAll('.contact-line .van-button')
    if (buttons[0]) buttons[0].onclick = () => { showQQPopup.value = true }
    if (buttons[1]) buttons[1].onclick = () => { showPhonePopup.value = true }
}
const callServicePhone = () => {
    showPhonePopup.value = false
    window.location.href = 'tel:86-45224655'
}
const copyServiceQQ = async () => {
    try {
        await navigator.clipboard.writeText('274625416')
        showQQPopup.value = false
        showSuccessToast('QQ群号已复制')
    } catch (e) {
        showToast('复制失败，请手动添加 274625416')
    }
}
const handleAvatarChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const form = new FormData();
    form.append('file', file);
    showLoadingToast({ message: '上传中...', forbidClick: true });
    try {
        const upRes = await uploadImage(form);
        if (upRes.data.code !== 200) { closeToast(); return showToast('上传失败'); }
        const url = upRes.data.url;
        const res = await updateProfile({ avatar: url });
        closeToast();
        if (res.data.code === 200) { currentUser.value.avatar = url; showSuccessToast('头像已更新'); } else showToast(res.data.msg);
    } catch { closeToast(); showToast('网络错误'); }
    e.target.value = '';
}
const loadData = () => { loadMyOrders(); loadAddress(); loadCart(); loadFavorites(); openMyCoupons(); }
const loadCart = async () => { if(!currentUser.value) return; const res = await fetchCartList(); if(res.data.code===200) cartList.value = res.data.data.map(i => ({...i, checked: true})) }
const handleAddToCart = async (item) => {
    if(!currentUser.value) return showToast('请登录');
    if(item.is_seckill) return showToast('秒杀商品请直接购买');
    const res = await addCartItem(item.id);
    if(res.data.code===200) { showSuccessToast('已加购'); loadCart() } else { showToast(res.data.msg || '加入购物车失败') }
}
const updateCartNum = async (item, num) => { if (num === undefined) num = item.num; await updateCartItem(item.id, num); loadCart() }
const toggleAllCheck = (val) => { cartList.value.forEach(item => item.checked = val) }

// 🔥 核心修改：点击商品 -> 打开统一详情页 (openProductDetail) 🔥
// 代替原来的 handleBuyNow，所有商品点击都走这里
const handleBuyNow = (item) => openProductDetail(item)

const openProductDetail = async (item) => {
    selectedItem.value = { ...item }
    showFavorites.value = false
    productComments.value = []

    if (item.is_seckill) {
        if (seckillTimer.value) clearInterval(seckillTimer.value)
        refreshSelectedSeckillState()
        seckillTimer.value = setInterval(refreshSelectedSeckillState, 1000)
    }

    showProductDetail.value = true

    try {
        const res = await fetchProductComments(item.id)
        if (res.data.code === 200) productComments.value = res.data.data
    } catch {}
}

// 🔥 详情页底部的按钮触发逻辑 🔥
const triggerBuyLogic = () => {
    if(!currentUser.value){ showToast('请登录'); showProductDetail.value=false; activeTab.value=2; return }

    const item = selectedItem.value;
    selectedCoupon.value = null;
    usePoints.value = false;

    if(item.is_seckill) {
        if(item.seckill_status === 'upcoming') return showDialog({ message: '秒杀尚未开始，请等待活动开抢。' });
        if(item.seckill_status === 'sold_out') return showDialog({ message: '当前秒杀商品已售罄，请查看其他商品。' });
        if(item.seckill_status === 'ended') return showDialog({ message: '当前秒杀活动已结束。' });
        isGroupBuyMode.value = false;
        showProductDetail.value = false;
        showBuyDialog.value = true;
        if(addressList.value.length===0) loadAddress()
        return;
    }

    if(selectedItemIsGroup.value) {
        isGroupBuyMode.value = true;
        showProductDetail.value = false;
        showGroupChoiceDialog.value = true;
        if(addressList.value.length===0) loadAddress()
        return;
    }

    isGroupBuyMode.value = false;
    showProductDetail.value = false;
    showBuyDialog.value = true;
    if(addressList.value.length===0) loadAddress()
}

const handleSeckillFinish = () => {
    refreshSelectedSeckillState()
}

const cancelGroupChoice = () => {
    showGroupChoiceDialog.value = false
    showJoinGroupInput.value = false
    pendingGroupAction.value = null
    inputGroupCode.value = ''
    isGroupBuyMode.value = false
}
const openJoinGroupDialog = () => {
    showGroupChoiceDialog.value = false
    showJoinGroupInput.value = true
}
const buyGroupItemDirectly = () => {
    isGroupBuyMode.value = false
    pendingGroupAction.value = null
    inputGroupCode.value = ''
    showGroupChoiceDialog.value = false
    showJoinGroupInput.value = false
    showBuyDialog.value = true
}
const startNewGroup = () => { pendingGroupAction.value = 'create'; showGroupChoiceDialog.value = false; showBuyDialog.value = true }
const joinGroup = () => { if(!inputGroupCode.value) return showToast('请输入拼团码'); pendingGroupAction.value = 'join'; showBuyDialog.value = true }

// 🔥 修改：购物车结算拦截逻辑 🔥
const handleCartCheckout = () => {
    if(checkedCartItems.value.length===0) return showToast('请选择商品');

    // 购物车秒杀拦截逻辑
    const hasSeckillItem = checkedCartItems.value.some(i => i.category && i.category.includes('秒杀'))
    if(hasSeckillItem && isSeckillExpired.value) {
        return showDialog({ message: '包含已超时的秒杀商品，无法支付！请移除后重试。' })
    }

    usePoints.value=false; selectedCoupon.value=null; showCartConfirm.value=true;
    if(addressList.value.length===0) loadAddress()
}

const confirmSingleOrder = async () => { await processPay(createOrder, { product_id: selectedItem.value.id, address_id: selectedAddrId.value, coupon_id: selectedCoupon.value?.id, use_points: usePoints.value, group_action: isGroupBuyMode.value ? pendingGroupAction.value : null, group_code: isGroupBuyMode.value ? inputGroupCode.value : null }) }
const confirmCartOrder = async () => { await processPay(checkoutCart, { cart_ids: checkedCartItems.value.map(i=>i.id), address_id: selectedAddrId.value, coupon_id: selectedCoupon.value?.id, use_points: usePoints.value }) }
const processPay = async (submitRequest, data) => {
    if(!selectedAddrId.value) return showToast('请选地址');
    const amountToPay = calculateFinalPrice.value > 0 ? calculateFinalPrice.value : calculateCartFinalPrice.value;
    showLoadingToast({message:'正在验证支付...', forbidClick:true, duration:0});
    try {
        await new Promise(r=>setTimeout(r,1500));
        const res = await submitRequest(data);
        closeToast();
        if(res.data.code===200) { currentUser.value.balance=res.data.balance; currentUser.value.points=res.data.points; lastPaidAmount.value = amountToPay; lastOrderGroupCode.value = res.data.group_code || null; showBuyDialog.value = false; showCartConfirm.value = false; showPaySuccess.value=true; loadData(); pendingGroupAction.value = null; inputGroupCode.value = ''; } else { showToast(res.data.msg) }
    } catch(e) { closeToast(); showToast('网络请求失败') }
}
const finishPayment = (target) => { showPaySuccess.value=false; activeTab.value = target==='order'?2:0 }
const loadMyOrders = async () => { if(!currentUser.value)return; const res = await fetchMyOrders(); if(res.data.code===200) myOrderList.value=res.data.data }
const resetNewAddress = () => { newAddr.name=''; newAddr.phone=''; newAddr.detail=''; newAddr.is_default=false }
const loadAddress = async () => {
  const res = await fetchAddressList()
  if(res.data.code===200) {
    addressList.value=res.data.data
    const defaultAddr = addressList.value.find(item => item.is_default)
    if(defaultAddr) selectedAddrId.value = defaultAddr.id
    else if(addressList.value.length>0 && !selectedAddrId.value) selectedAddrId.value=addressList.value[0].id
  }
}
const saveAddress = async () => {
  await createAddress(newAddr)
  showSuccessToast('成功')
  await loadAddress()
  showAddAddrForm.value=false
  resetNewAddress()
}
const setDefaultAddress = async (id) => {
  const res = await switchDefaultAddress(id)
  if(res.data.code===200) {
    selectedAddrId.value = id
    showSuccessToast('默认地址已更新')
    await loadAddress()
  } else {
    showToast(res.data.msg || '设置失败')
  }
}
const confirmOrderReceipt = async (order) => { await confirmReceipt(order.id); showSuccessToast('完成'); loadMyOrders() }
const cancelOrder = async (order) => {
    showDialog({ title: '取消订单', message: '确定取消该订单？金额将退回账户余额', showCancelButton: true }).then(async () => {
        const res = await cancelOrderById(order.id)
        if (res.data.code === 200) {
            showSuccessToast('已取消，余额已退回')
            if (currentUser.value) currentUser.value.balance = res.data.balance
            showOrderDetail.value = false
            loadMyOrders()
        } else {
            showToast(res.data.msg)
        }
    }).catch(() => {})
}
const viewOrderDetail = async (id) => { showLoadingToast('加载...'); try { const res = await fetchOrderDetail(id); const logRes = await fetchOrderLogistics(id); if(res.data.code===200) { currentOrderDetail.value=res.data.data; logisticsTraces.value = logRes.data.data || []; showOrderDetail.value=true } } finally { closeToast() } }
const toggleFavorite = async (item) => {
    if(!currentUser.value) return showToast('请登录');
    const res = await toggleFavoriteItem(item.id);
    if(res.data.code === 200) {
        if(res.data.action === 'add') {
             showSuccessToast('收藏成功，宝贝已经躺在我的收藏里面啦');
             favIds.value.push(item.id); // 立即更新状态
        } else {
             showToast('已取消收藏');
             const idx = favIds.value.indexOf(item.id);
             if(idx > -1) favIds.value.splice(idx, 1);
        }
        if(showFavorites.value) loadFavorites();
    }
}
const loadFavorites = async () => {
    const res = await fetchFavorites();
    if(res.data.code===200) {
        favoriteList.value = res.data.data;
        // 提取ID
        favIds.value = res.data.data.map(i => i.id);
    }
}
const openComment = (order) => { commentForm.order_id = order.id; commentForm.content = ''; commentForm.rating = 5; showCommentDialog.value = true }
const submitComment = async () => { const res = await submitCommentByOrder(commentForm); if(res.data.code === 200) { showSuccessToast('评价成功'); loadMyOrders(); showCommentDialog.value=false } }
const upgradeVip = () => {
    if(!currentUser.value) return showToast('请登录');
    showVipModal.value = true
}
const openVipCenter = () => upgradeVip()
const selectVip = (level) => {
    if(currentUser.value.level >= level) return;
    pendingVipLevel.value = level
    showVipModal.value = false
    showVipPayDialog.value = true
}
const confirmVipPay = async () => {
    showLoadingToast('处理中...')
    try {
        const res = await upgradeVipLevel(pendingVipLevel.value)
        closeToast()
        if(res.data.code === 200) {
            currentUser.value.level = res.data.level
            showSuccessToast('升级成功！')
            showVipPayDialog.value = false
        } else {
            showToast(res.data.msg)
        }
    } catch(e) { showToast('网络错误') }
}

watch(activeTab, (val) => { if(val===1) loadCart(); if(val===2) loadMyOrders() })
</script>

<style>
.mobile-app {
  --mall-primary: #e84d2a;
  --mall-primary-deep: #b92f18;
  --mall-accent: #ffb36b;
  --mall-bg: #f6f1eb;
  --mall-surface: rgba(255, 255, 255, 0.9);
  --mall-text: #241815;
  --mall-text-soft: #7b6a62;
  --mall-line: rgba(71, 43, 31, 0.08);
  --mall-shadow-soft: 0 18px 44px rgba(111, 55, 29, 0.1);
  --mall-shadow-card: 0 10px 28px rgba(88, 48, 28, 0.08);
}
body {
  margin: 0;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 158, 0.45), transparent 28%),
    radial-gradient(circle at top right, rgba(232, 77, 42, 0.12), transparent 24%),
    linear-gradient(180deg, #fbf7f2 0%, var(--mall-bg) 44%, #f1ece6 100%);
  color: var(--mall-text);
  font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}
.mobile-app { padding-bottom: 78px; max-width: 600px; margin: 0 auto; min-height: 100vh; position: relative; }
.mobile-app::before { content: ''; position: fixed; inset: 0; background: linear-gradient(140deg, rgba(255, 255, 255, 0.42), transparent 42%), radial-gradient(circle at 20% 10%, rgba(255, 183, 126, 0.12), transparent 18%); pointer-events: none; z-index: 0; }
.mobile-app > * { position: relative; z-index: 1; }
.user-header-card { margin: 0; padding: 44px 20px 108px; background: radial-gradient(circle at top right, rgba(255, 210, 164, 0.35), transparent 28%), linear-gradient(135deg, #ff7a3d, var(--mall-primary) 52%, var(--mall-primary-deep)); color: white; border-bottom-left-radius: 34px; border-bottom-right-radius: 34px; box-shadow: var(--mall-shadow-soft); }
.user-header-card.is-vip { background: radial-gradient(circle at top right, rgba(255, 226, 170, 0.28), transparent 24%), linear-gradient(135deg, #3a332f, #5d534d); }
.data-row { display: flex; justify-content: space-around; text-align: center; background: var(--mall-surface); margin: 0 20px; padding: 20px 0; border-radius: 20px; box-shadow: var(--mall-shadow-soft); margin-top: -80px; color: var(--mall-text); position: relative; z-index: 2; border: 1px solid rgba(255, 255, 255, 0.72); backdrop-filter: blur(16px); }
.login-wrapper { min-height: 80vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
.login-card { width: 100%; background: var(--mall-surface); border-radius: 24px; padding: 30px 20px; box-shadow: var(--mall-shadow-soft); border: 1px solid rgba(255,255,255,0.8); backdrop-filter: blur(16px); }
.login-header h3 { text-align: center; color: var(--mall-text); margin: 0; font-size: 24px; }
.login-header p { text-align: center; color: var(--mall-text-soft); font-size: 14px; margin-top: 5px; margin-bottom: 30px; }
.beauty-input { background-color: #f5f1ed; border-radius: 24px; margin-bottom: 15px; padding: 10px 15px; }
.tab-page { background: transparent; min-height: 100vh; }
.header-search-box { padding: 10px 12px 10px; display: flex; align-items: center; position: sticky; top: 0; z-index: 99; box-shadow: none; }
.home-search-shell {
  position: relative;
  top: auto;
  z-index: 1;
  box-shadow: none;
}
.home-search-shell {
  padding: 10px 12px 18px;
}
.home-search-shell > .van-search,
.home-search-shell > .van-icon { display: none; }
.home-search-card {
  width: 100%;
  padding: 20px 18px 16px;
  border-radius: 30px;
  background:
    radial-gradient(circle at 86% 18%, rgba(255, 161, 92, 0.24), transparent 16%),
    radial-gradient(circle at 18% 0%, rgba(255, 228, 188, 0.82), transparent 28%),
    linear-gradient(145deg, rgba(255, 252, 247, 0.98), rgba(255, 245, 237, 0.94));
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 22px 40px rgba(93, 54, 34, 0.12);
  backdrop-filter: blur(16px);
  position: relative;
  overflow: hidden;
}
.home-search-card::after {
  content: '';
  position: absolute;
  right: -26px;
  bottom: -22px;
  width: 130px;
  height: 130px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 133, 84, 0.18), rgba(255, 133, 84, 0));
  pointer-events: none;
}
.home-search-top { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 14px; }
.home-search-kicker {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.22em;
  color: #ba7d61;
  text-transform: uppercase;
}
.home-search-title {
  font-size: 28px;
  font-weight: 900;
  color: #24150f;
  letter-spacing: -0.03em;
  line-height: 1;
}
.home-search-sub {
  margin-top: 8px;
  font-size: 13px;
  color: #83675b;
  line-height: 1.45;
}
.home-search-refresh {
  width: 40px;
  height: 40px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(233, 208, 189, 0.9);
  box-shadow: 0 10px 18px rgba(122, 76, 52, 0.1);
}
.home-search-input { padding: 0; }
.home-search-input :deep(.van-search__content) {
  background: rgba(255,255,255,0.94);
  border-radius: 20px;
  padding: 10px 14px;
  border: 1px solid rgba(234, 220, 209, 0.88);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.85);
}
.home-search-input :deep(.van-field__control) { color: #3c2a24; font-size: 14px; }
.home-search-input :deep(.van-field__left-icon) { color: #b59a8d; }
.home-search-shortcuts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}
.home-shortcut {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: #8b6a5b;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(235, 220, 208, 0.9);
}
.home-shortcut.active {
  color: #fff7f1;
  background: linear-gradient(135deg, #ff8f5f, #e84d2a);
  border-color: rgba(232, 77, 42, 0.28);
}
.home-metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 12px; }
.metric-pill {
  padding: 12px 10px 10px;
  border-radius: 18px;
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(255,255,255,0.92);
  display: flex;
  flex-direction: column;
  gap: 3px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.85);
}
.metric-pill :deep(.van-icon) {
  color: #b07f68;
}
.metric-pill.accent {
  background: linear-gradient(135deg, rgba(255, 132, 84, 0.96), rgba(232, 77, 42, 0.88));
  border-color: rgba(255, 145, 105, 0.52);
  box-shadow: 0 14px 22px rgba(232, 77, 42, 0.18);
}
.metric-pill.accent :deep(.van-icon) { color: #fff6f0; }
.metric-num { font-size: 18px; font-weight: 900; color: #2a1b16; }
.metric-label { font-size: 11px; color: #83675b; }
.metric-pill.accent .metric-num,
.metric-pill.accent .metric-label { color: #fff7f1; }
.banner-box { padding: 0 12px 12px; margin-top: 4px; }
.my-swipe {
  border-radius: 28px;
  overflow: hidden;
  box-shadow: 0 20px 34px rgba(95, 57, 36, 0.12);
}
.my-swipe .van-swipe-item { border-radius: 28px; overflow: hidden; height: 194px; }
.my-swipe :deep(.van-swipe__indicators) {
  bottom: 12px;
}
.my-swipe :deep(.van-swipe__indicator) {
  width: 8px;
  height: 8px;
  background: rgba(255,255,255,0.56);
}
.my-swipe :deep(.van-swipe__indicator--active) {
  width: 20px;
  border-radius: 999px;
  background: rgba(255,255,255,0.98);
}
.banner-img { width: 100%; height: 100%; object-fit: cover; }
.empty-banner { background: #ddd; height: 100%; display: flex; align-items: center; justify-content: center; color: gray; }
.home-highlight-panel {
  margin: 0 12px 14px;
  padding: 18px 18px 16px;
  border-radius: 24px;
  background: linear-gradient(145deg, rgba(255,255,255,0.9), rgba(255,247,240,0.84));
  box-shadow: var(--mall-shadow-card);
  border: 1px solid rgba(255,255,255,0.75);
}
.highlight-copy { margin-bottom: 12px; }
.highlight-eyebrow { font-size: 11px; font-weight: 700; letter-spacing: 0.18em; color: var(--mall-primary); text-transform: uppercase; }
.highlight-title { margin-top: 6px; font-size: 22px; font-weight: 800; color: var(--mall-text); }
.highlight-desc { margin-top: 6px; font-size: 13px; line-height: 1.55; color: var(--mall-text-soft); }
.highlight-insight {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}
.highlight-insight-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(255,255,255,0.76);
  border: 1px solid rgba(255,255,255,0.78);
}
.highlight-insight-card.warm {
  background: linear-gradient(135deg, rgba(255, 244, 236, 0.98), rgba(255, 234, 221, 0.92));
  border-color: rgba(232,77,42,0.08);
}
.highlight-insight-label {
  font-size: 11px;
  color: var(--mall-text-soft);
}
.highlight-insight-value {
  font-size: 16px;
  font-weight: 800;
  color: var(--mall-text);
}
.highlight-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.highlight-badge {
  padding: 6px 10px;
  border-radius: 999px;
  background: #f6efe9;
  color: #70574c;
  font-size: 12px;
  font-weight: 600;
}
.highlight-badge.hot { background: rgba(232, 77, 42, 0.12); color: var(--mall-primary); }
.menu-container { margin-top: 2px; }
.drag-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px 0;
  padding: 18px 0 20px;
  background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,250,246,0.88));
  margin: 0 12px;
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  box-shadow: var(--mall-shadow-card);
}
.drag-item { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.icon-circle {
  width: 50px;
  height: 50px;
  background: linear-gradient(180deg, #fffdfb, #fff2e8);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 9px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.94), 0 10px 18px rgba(100, 64, 43, 0.08);
}
.menu-text { font-size: 12px; color: var(--mall-text); font-weight: 700; }
.seckill-bar { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #fff4ef, #ffe2d3); margin: 12px; padding: 12px 16px; border-radius: 16px; border: 1px solid rgba(232, 77, 42, 0.12); box-shadow: var(--mall-shadow-card); }
.sk-left { display: flex; align-items: center; color: var(--mall-primary); font-weight: bold; gap: 5px; }
.sk-timer { color: var(--mall-primary); font-weight: bold; }
.goods-container { padding: 0 12px; }
.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin: 6px 0 14px;
  padding: 0 2px;
  gap: 12px;
}
.section-copy { min-width: 0; }
.section-kicker { font-size: 11px; letter-spacing: 0.18em; color: var(--mall-text-soft); text-transform: uppercase; }
.section-title { margin-top: 4px; font-size: 24px; line-height: 1.1; font-weight: 800; color: var(--mall-text); }
.section-sub {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.5;
  color: var(--mall-text-soft);
}
.section-side {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.7);
  color: var(--mall-text-soft);
  font-size: 12px;
  font-weight: 700;
}
.activity-page {
  background:
    radial-gradient(circle at top right, rgba(255, 193, 122, 0.18), transparent 22%),
    transparent;
  padding-top: 62px;
}
.activity-hero {
  margin: 0 12px 14px;
  padding: 24px 18px 18px;
  border-radius: 28px;
  color: white;
  box-shadow: var(--mall-shadow-soft);
}
.group-hero {
  background:
    radial-gradient(circle at top right, rgba(255,255,255,0.2), transparent 24%),
    linear-gradient(135deg, #ff8150, #e84d2a 58%, #bc361b);
}
.seckill-hero {
  background:
    radial-gradient(circle at top right, rgba(255,214,170,0.18), transparent 22%),
    linear-gradient(135deg, #ff5b44, #d93434 58%, #8f1c24);
}
.activity-kicker {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: rgba(255,255,255,0.72);
}
.activity-title {
  margin: 8px 0 0;
  font-size: 30px;
  line-height: 1.05;
  font-weight: 900;
}
.activity-desc {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.55;
  color: rgba(255,255,255,0.84);
}
.activity-stat-row {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.activity-stat-card {
  padding: 12px 10px;
  border-radius: 18px;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.14);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.activity-stat-card.hot {
  background: rgba(255, 224, 181, 0.2);
}
.activity-stat-num {
  font-size: 18px;
  font-weight: 800;
  color: #fff;
}
.activity-stat-label {
  font-size: 11px;
  color: rgba(255,255,255,0.75);
}
.activity-list {
  padding-bottom: 12px;
}
.activity-card {
  display: flex;
  margin-bottom: 14px;
  overflow: hidden;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,251,247,0.92));
  border: 1px solid rgba(255,255,255,0.76);
  box-shadow: var(--mall-shadow-card);
}
.activity-card-img-shell {
  width: 128px;
  height: 138px;
  position: relative;
  flex-shrink: 0;
}
.activity-card-img {
  width: 128px;
  height: 138px;
  object-fit: cover;
  flex-shrink: 0;
}
.activity-card-body {
  flex: 1;
  padding: 14px 14px 12px;
  display: flex;
  flex-direction: column;
}
.activity-card-top {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.activity-progress-copy {
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.5;
  color: var(--mall-text-soft);
}
.activity-card-bottom {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.activity-old-price {
  margin-left: 6px;
  font-size: 12px;
  color: #9f8e87;
  text-decoration: line-through;
  font-weight: normal;
}
.activity-corner-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(217, 47, 47, 0.92);
  color: white;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.activity-progress-bar {
  margin-top: 12px;
  height: 8px;
  border-radius: 999px;
  background: #f3e4df;
  overflow: hidden;
}
.activity-progress-fill {
  width: 72%;
  height: 100%;
  background: linear-gradient(90deg, #ff8e5d, #e84d2a);
  border-radius: inherit;
}
.seckill-bottom {
  margin-top: 12px;
}
.sheet-popup :deep(.van-popup) {
  border-top-left-radius: 26px;
  border-top-right-radius: 26px;
  overflow: hidden;
  box-shadow: 0 -18px 42px rgba(63, 31, 19, 0.14);
}
.sheet-content {
  padding: 16px 15px 28px;
}
.sheet-title {
  text-align: center;
  margin-top: 10px;
  margin-bottom: 20px;
  font-weight: 700;
  color: var(--mall-text);
}
.sheet-popup :deep(.van-empty__description) {
  color: var(--mall-text-soft);
}
.sheet-popup :deep(.van-popup__close-icon) {
  color: rgba(45, 28, 22, 0.45);
}
.goods-waterfall { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.goods-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,250,246,0.9));
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 16px 28px rgba(95, 58, 36, 0.08);
  border: 1px solid rgba(255,255,255,0.78);
  display: flex;
  flex-direction: column;
}
.img-wrapper {
  position: relative;
  padding-top: 100%;
  width: calc(100% - 18px);
  margin: 9px 9px 0;
  border-radius: 18px;
  overflow: hidden;
  background: #f4ede8;
}
.img-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.info-wrapper { padding: 11px 11px 12px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.title { font-size: 14px; color: var(--mall-text); line-height: 1.45; height: 40px; overflow: hidden; margin-bottom: 6px; font-weight: 600; }
.tags { display: flex; gap: 5px; margin-bottom: 7px; flex-wrap: wrap; }
.tag { font-size: 10px; padding: 3px 7px; border-radius: 999px; font-weight: 700; }
.tag.red { border: 1px solid rgba(232, 77, 42, 0.26); color: var(--mall-primary); background: rgba(232, 77, 42, 0.08); }
.tag.gold { background: #3e342c; color: #ffd98a; }
.tag.blue { background: #edf6ff; color: #2370ca; border: 1px solid #cde1fb; }
.vip-tag { background: #333; color: gold; border-color: #333; }
.bottom-row { display: flex; justify-content: space-between; align-items: center; }
.price { color: var(--mall-primary); font-weight: 800; font-size: 16px; letter-spacing: -0.3px; }
.price .num { font-size: 20px; }
.goods-actions { display: flex; gap: 8px; }
.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.btn-icon.fav { background: #f7f2ee; color: #8c786e; transition: all 0.2s; border: 1px solid rgba(234, 222, 214, 0.9); }
.btn-icon.fav:active { color: var(--mall-primary); background: #ffebe4; }
.btn-icon.cart { background: linear-gradient(135deg, #ff7c43, var(--mall-primary)); color: white; box-shadow: 0 8px 18px rgba(232,77,42,0.28); }
.empty-cart { padding: 70px 18px; text-align: center; }
.empty-cart :deep(.van-empty) {
  padding: 28px 0 18px;
  background: rgba(255,255,255,0.7);
  border-radius: 24px;
  box-shadow: var(--mall-shadow-card);
}
.cart-list-container { padding-bottom: 132px; }
.cart-item { background: var(--mall-surface); margin: 12px; padding: 12px; border-radius: 18px; display: flex; align-items: center; box-shadow: var(--mall-shadow-card); border: 1px solid rgba(255,255,255,0.7); backdrop-filter: blur(14px); }
.cart-img { width: 90px; height: 90px; border-radius: 10px; object-fit: cover; margin: 0 10px; }
.cart-info { flex: 1; height: 90px; display: flex; flex-direction: column; justify-content: space-between; }
.cart-title { font-size: 14px; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--mall-text); }
.cart-footer { display: flex; justify-content: space-between; align-items: center; }
.cart-price { color: var(--mall-primary); font-weight: 800; font-size: 16px; }
.goods-seckill-meta { margin-top: 8px; font-size: 11px; color: var(--mall-text-soft); }
.seckill-detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 18px; }
.seckill-detail-card { padding: 12px; border-radius: 16px; background: linear-gradient(180deg, rgba(255,248,244,1), rgba(255,240,233,0.94)); border: 1px solid rgba(232,77,42,0.08); }
.seckill-detail-label { font-size: 11px; color: var(--mall-text-soft); }
.seckill-detail-value { margin-top: 6px; font-size: 15px; font-weight: 800; color: var(--mall-text); line-height: 1.45; }
.seckill-detail-value.mini { font-size: 12px; font-weight: 700; }
.cart-submit-shell {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 28px);
  max-width: 520px;
  bottom: 82px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.95);
  overflow: hidden;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.78);
  box-shadow: 0 18px 36px rgba(85, 45, 27, 0.14);
  backdrop-filter: blur(18px);
  z-index: 4200;
  box-sizing: border-box;
}
.cart-submit-check {
  flex-shrink: 0;
}
.cart-submit-price {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.cart-submit-label {
  font-size: 12px;
  color: var(--mall-text-soft);
}
.cart-submit-value {
  font-size: 20px;
  font-weight: 800;
  color: var(--mall-primary);
  letter-spacing: -0.4px;
}
.cart-submit-btn {
  flex-shrink: 0;
  min-width: 104px;
  height: 40px;
  padding: 0 16px;
}
.cart-submit-shell :deep(.van-checkbox__label) {
  color: var(--mall-text);
  font-weight: 600;
}
@media (max-width: 420px) {
  .home-search-card {
    padding: 18px 15px 14px;
    border-radius: 26px;
  }
  .home-search-title {
    font-size: 24px;
  }
  .home-search-sub {
    font-size: 12px;
  }
  .home-metrics {
    gap: 8px;
  }
  .metric-pill {
    padding: 10px 9px 9px;
    border-radius: 16px;
  }
  .metric-num {
    font-size: 16px;
  }
  .highlight-insight {
    grid-template-columns: 1fr;
  }
  .highlight-title {
    font-size: 20px;
  }
  .section-title {
    font-size: 21px;
  }
  .goods-waterfall {
    gap: 10px;
  }
  .goods-card {
    border-radius: 20px;
  }
  .img-wrapper {
    width: calc(100% - 14px);
    margin: 7px 7px 0;
    border-radius: 16px;
  }
  .info-wrapper {
    padding: 10px 9px 11px;
  }
  .cart-submit-shell {
    width: calc(100% - 20px);
    bottom: 80px;
    gap: 8px;
    padding: 11px 12px;
    border-radius: 18px;
  }
  .cart-submit-value {
    font-size: 18px;
  }
  .cart-submit-btn {
    min-width: 96px;
    height: 38px;
    padding: 0 14px;
  }
}
.user-info { display: flex; align-items: center; margin-bottom: 20px; cursor: pointer; }
.avatar { width: 68px; height: 68px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.68); box-shadow: 0 8px 20px rgba(0,0,0,0.14); }
.text-info { margin-left: 15px; }
.nickname { font-size: 20px; font-weight: bold; display: flex; align-items: center; }
.level-badge { background: rgba(0,0,0,0.2); padding: 4px 10px; border-radius: 999px; font-size: 12px; margin-top: 6px; }
.member-hero-meta {
  padding: 14px 16px 0;
  border-top: 1px solid rgba(255,255,255,0.16);
}
.hero-desc {
  margin-top: 6px;
  font-size: 20px;
  line-height: 1.45;
  font-weight: 800;
  color: rgba(255,255,255,0.95);
}
.hero-desc-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.hero-desc-edit-btn {
  flex-shrink: 0;
  font-size: 18px;
  color: rgba(255,255,255,0.82);
  cursor: pointer;
}
.hero-desc-editable {
  display: none;
}
.data-item .num { font-size: 21px; font-weight: 800; margin-bottom: 5px; }
.data-item .lbl { font-size: 12px; color: var(--mall-text-soft); }
.member-quick-panel {
  margin: 14px 20px 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.member-quick-item {
  padding: 14px 12px;
  border-radius: 18px;
  background: rgba(255,255,255,0.84);
  box-shadow: var(--mall-shadow-card);
  border: 1px solid rgba(255,255,255,0.76);
}
.quick-label {
  font-size: 11px;
  color: var(--mall-text-soft);
}
.quick-value {
  margin-top: 8px;
  font-size: 15px;
  font-weight: 800;
  color: var(--mall-text);
  line-height: 1.3;
}
.menu-group { margin-top: 20px; }
.menu-group :deep(.van-cell-group) {
  border-radius: 22px;
  overflow: hidden;
  box-shadow: var(--mall-shadow-card);
}
.menu-group :deep(.van-cell) {
  background: rgba(255,255,255,0.88);
}
.member-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 20px 10px;
}
.member-section-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--mall-text);
}
.member-section-sub {
  font-size: 12px;
  color: var(--mall-text-soft);
}
.order-section {
  margin-top: 22px;
  padding-bottom: 24px;
}
.jd-order-section { margin: 15px; }
.sec-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 0 20px; }
.sec-title { font-weight: 800; font-size: 16px; color: var(--mall-text); }
.sec-more { font-size: 12px; color: var(--mall-text-soft); }
.empty-order-box { text-align: center; color: #ccc; padding: 40px 0; }
.jd-order-card { background: var(--mall-surface); border-radius: 20px; padding: 15px; margin-bottom: 15px; box-shadow: var(--mall-shadow-card); border: 1px solid rgba(255,255,255,0.7); }
.card-head { display: flex; justify-content: space-between; font-size: 12px; border-bottom: 1px solid #f9f9f9; padding-bottom: 10px; margin-bottom: 10px; }
.shop-name { font-weight: bold; display: flex; align-items: center; gap: 4px; }
.status-txt.st-1 { color: var(--mall-primary); }
.status-txt.st-2 { color: #ff976a; }
.status-txt.st-3 { color: #07c160; }
.card-body { display: flex; align-items: center; }
.card-body img { width: 70px; height: 70px; border-radius: 10px; margin-right: 12px; object-fit: cover; }
.card-body .info { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.p-title { font-size: 14px; color: var(--mall-text); font-weight: 600; line-height: 1.4; margin-bottom: 5px; }
.p-price { color: var(--mall-primary); font-weight: 800; font-size: 15px; }
.card-foot { text-align: right; margin-top: 12px; border-top: 1px solid #f9f9f9; padding-top: 10px; }
.full-page-success { position: fixed; top: 0; left: 0; width: 100%; height: 100vh; background: linear-gradient(180deg, #fffdf9 0%, #f7f1ea 100%); z-index: 9999; display: flex; justify-content: center; padding: 90px 18px 24px; box-sizing: border-box; }
.success-shell {
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 34px 24px 26px;
  border-radius: 28px;
  background: rgba(255,255,255,0.82);
  backdrop-filter: blur(18px);
  box-shadow: var(--mall-shadow-soft);
  border: 1px solid rgba(255,255,255,0.8);
}
.success-icon-box { width: 84px; height: 84px; background: linear-gradient(135deg, #1ec870, #07c160); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 14px 28px rgba(7,193,96,0.24); }
.success-title { margin-top: 20px; color: var(--mall-text); font-size: 28px; font-weight: 900; }
.success-subtitle { margin-top: 10px; text-align: center; font-size: 13px; line-height: 1.6; color: var(--mall-text-soft); }
.success-group-box {
  width: 100%;
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(255,247,240,1), rgba(255,238,229,0.92));
  border: 1px solid rgba(232,77,42,0.1);
  text-align: center;
}
.success-group-label { font-size: 12px; color: var(--mall-text-soft); }
.success-group-code { margin-top: 6px; font-size: 28px; font-weight: 900; color: var(--mall-primary); letter-spacing: 0.12em; }
.success-group-desc { margin-top: 6px; font-size: 12px; color: var(--mall-text-soft); }
.succ-price { font-size: 48px; font-weight: bold; margin-top: 22px; font-family: sans-serif; color: var(--mall-text); }
.success-action-row { width: 100%; margin-top: 34px; display: flex; gap: 14px; }
.success-secondary-btn,
.success-primary-btn { flex: 1; }
.full-page-detail {
  position: fixed;
  inset: 0;
  background: rgba(84, 49, 36, 0.18);
  backdrop-filter: blur(8px);
  z-index: 200;
  overflow-y: auto;
  padding: 12px;
  box-sizing: border-box;
}
.detail-page-shell {
  width: 100%;
  max-width: 520px;
  min-height: calc(100vh - 24px);
  margin: 0 auto;
  background: linear-gradient(180deg, #fffdf9 0%, #f7f1ea 100%);
  border-radius: 28px;
  overflow: hidden;
  box-shadow: 0 22px 48px rgba(66, 36, 25, 0.18);
}
.detail-page-shell :deep(.van-nav-bar) {
  background: rgba(255,255,255,0.86);
  backdrop-filter: blur(14px);
}
.detail-page-content {
  padding: 0 15px 18px;
}
.detail-status-header { background: linear-gradient(to right, #ff6034, var(--mall-primary)); color: white; padding: 25px 20px 50px; box-shadow: var(--mall-shadow-soft); }
.status-big { font-size: 20px; font-weight: bold; display: flex; align-items: center; gap: 10px; margin-bottom: 5px; }
.status-desc { font-size: 12px; opacity: 0.8; margin-left: 34px; }
.detail-status-pills { display: flex; gap: 8px; flex-wrap: wrap; margin: 14px 0 0 34px; }
.detail-pill {
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 11px;
  color: rgba(255,255,255,0.88);
  background: rgba(255,255,255,0.14);
  border: 1px solid rgba(255,255,255,0.16);
}
.card { background: var(--mall-surface); border-radius: 20px; padding: 15px; margin-bottom: 15px; box-shadow: var(--mall-shadow-card); border: 1px solid rgba(255,255,255,0.75); backdrop-filter: blur(14px); }
.detail-code-card { background: linear-gradient(145deg, rgba(255,251,247,0.98), rgba(255,240,233,0.92)); }
.detail-code-main { color: var(--mall-primary); font-weight: 900; font-size: 18px; }
.detail-code-sub { font-size: 12px; color: var(--mall-text-soft); margin-top: 6px; }
.detail-address-card { display: flex; align-items: center; }
.icon-side { margin-right: 15px; }
.addr-title { font-weight: bold; font-size: 14px; margin-bottom: 4px; }
.addr-text { font-size: 13px; color: var(--mall-text-soft); line-height: 1.4; }
.goods-row { display: flex; align-items: flex-start; gap: 12px; }
.detail-goods-img { width: 86px; height: 86px; border-radius: 14px; object-fit: cover; flex-shrink: 0; }
.g-right { margin-left: 0; flex: 1; display: flex; flex-direction: column; justify-content: space-between; min-width: 0; }
.g-title { font-size: 14px; font-weight: 700; line-height: 1.45; color: var(--mall-text); }
.g-sub { margin-top: 6px; font-size: 12px; color: var(--mall-text-soft); line-height: 1.45; }
.g-price { margin-top: 10px; font-size: 18px; color: var(--mall-primary); font-weight: 800; }
.detail-meta .meta-row { display: flex; justify-content: space-between; font-size: 12px; color: var(--mall-text-soft); margin-bottom: 8px; }
.contact-line { margin-top: 14px; border-top: 1px solid #f9f9f9; padding-top: 12px; display: flex; justify-content: center; gap: 12px; }
.pay-dialog-content { padding: 12px; }
.price-big { text-align: center; font-size: 38px; font-weight: 800; color: var(--mall-primary); margin: 18px 0 22px; letter-spacing: -1px; }
.pay-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid var(--mall-line); font-size: 15px; color: var(--mall-text); }
.pay-row .link { color: var(--mall-text-soft); display: flex; align-items: center; }
.pay-row .link.red { color: var(--mall-primary); }
.pay-row-note .value { color: var(--mall-text-soft); font-size: 13px; }
.pay-qr-box {
  margin-top: 18px;
  padding: 16px 14px 12px;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,244,240,0.96));
  border: 1px solid rgba(232,77,42,0.08);
  text-align: center;
}
.pay-qr-tip {
  font-size: 14px;
  color: var(--mall-text-soft);
}
.pay-qr-img {
  width: 170px;
  height: 170px;
  margin: 12px auto 14px;
  display: block;
  border-radius: 18px;
  background: #fff;
  padding: 8px;
  box-shadow: var(--mall-shadow-card);
}
.pay-confirm-btn {
  margin-top: 2px;
}
.addr-box { background: #f9f4ef; padding: 15px; border-radius: 16px; margin-bottom: 10px; display: flex; align-items: center; border: 1px solid rgba(232,77,42,0.08); }
.addr-content { flex: 1; min-width: 0; }
.addr-topline { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 6px; }
.addr-detail { color: gray; font-size: 12px; line-height: 1.5; display: block; }
.addr-actions { margin-top: 10px; display: flex; justify-content: flex-end; }
.fav-item { display: flex; background: #ffffff; padding: 12px; border-radius: 16px; margin-bottom: 10px; box-shadow: var(--mall-shadow-card); align-items: center; }
.fav-item img { width: 60px; height: 60px; border-radius: 8px; margin-right: 10px; object-fit: cover; }
.f-title { font-weight: bold; font-size: 14px; margin-bottom: 5px; }
.f-price { color: var(--mall-primary); font-weight: 800; }
.coupon-card { display: flex; height: 90px; background: #ffffff; border-radius: 18px; margin-bottom: 12px; box-shadow: var(--mall-shadow-card); overflow: hidden; position: relative; }
.c-left { width: 105px; background: linear-gradient(135deg, #ff6034, var(--mall-primary)); color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; border-right: 2px dashed #f7f8fa; }
.c-left.got { background: #c8c9cc; }
.c-price { font-size: 32px; font-weight: bold; line-height: 1; font-family: sans-serif; }
.c-price span { font-size: 14px; margin-right: 2px; font-weight: normal; }
.c-cond { font-size: 11px; margin-top: 6px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px; }
.circle-top, .circle-bottom { position: absolute; width: 12px; height: 12px; background: #f7f8fa; border-radius: 50%; right: -6px; z-index: 2; }
.circle-top { top: -6px; }
.circle-bottom { bottom: -6px; }
.c-right { flex: 1; padding: 0 15px 0 20px; display: flex; justify-content: space-between; align-items: center; }
.c-info { display: flex; flex-direction: column; justify-content: center; gap: 6px; }
.c-name { font-size: 15px; font-weight: bold; color: var(--mall-text); display: flex; align-items: center; }
.c-tag { font-size: 10px; background: #fff0f0; color: var(--mall-primary); padding: 1px 4px; border-radius: 4px; margin-right: 6px; font-weight: normal; border: 1px solid rgba(238, 10, 36, 0.2); }
.c-left.got + .c-right .c-tag { background: #f2f3f5; color: #969799; border-color: #ebedf0; }
.c-date { font-size: 11px; color: #969799; }
.detail-logistics-card { padding-top: 16px; }
.detail-logistics-title { font-weight: 800; margin-bottom: 14px; color: var(--mall-text); }
.detail-logistics-row { display: flex; gap: 12px; margin-bottom: 12px; }
.detail-logistics-line { display: flex; flex-direction: column; align-items: center; }
.detail-logistics-dot { width: 10px; height: 10px; border-radius: 50%; background: #ddd; margin-top: 4px; flex-shrink: 0; }
.detail-logistics-dot.active { background: var(--mall-primary); box-shadow: 0 0 0 4px rgba(232,77,42,0.12); }
.detail-logistics-stick { width: 1px; flex: 1; background: #eee; min-height: 20px; margin-top: 2px; }
.detail-logistics-copy { padding-bottom: 10px; flex: 1; }
.detail-logistics-desc { font-size: 13px; color: #999; line-height: 1.55; }
.detail-logistics-desc.active { color: var(--mall-text); font-weight: 700; }
.detail-logistics-time { font-size: 11px; color: #bbb; margin-top: 3px; }
.detail-action-wrap { padding-bottom: 20px; }
.mobile-shell-popup {
  background: transparent;
}
.mobile-shell-popup :deep(.van-popup) {
  background: transparent;
  box-shadow: none;
}
.popup-mobile-shell {
  width: min(100%, 520px);
  min-height: calc(100vh - 24px);
  max-height: calc(100vh - 24px);
  margin: 12px auto;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #fffdf9 0%, #f7f1ea 100%);
  border-radius: 28px;
  overflow: hidden;
  box-shadow: 0 22px 48px rgba(66, 36, 25, 0.18);
}
.popup-mobile-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  box-sizing: border-box;
}
.all-orders-shell :deep(.van-nav-bar) {
  background: rgba(255,255,255,0.86);
  backdrop-filter: blur(14px);
}
.all-orders-shell :deep(.van-nav-bar--fixed) {
  position: sticky;
  top: 0;
  left: auto;
  right: auto;
  width: 100%;
}
.all-orders-shell :deep(.van-nav-bar__placeholder) {
  height: 46px !important;
}
.product-detail-shell {
  position: relative;
}
.product-detail-shell :deep(.van-popup__close-icon) {
  top: 18px;
  right: 18px;
  color: #fff;
  font-size: 24px;
  z-index: 4;
}
.product-detail-content {
  padding-bottom: 18px;
}
.product-detail-footer {
  flex-shrink: 0;
}
.sheet-popup :deep(.van-tabs__wrap) {
  border-bottom: 1px solid rgba(71, 43, 31, 0.06);
}
.sheet-popup :deep(.van-tab) {
  color: var(--mall-text-soft);
}
.sheet-popup :deep(.van-tab--active) {
  color: var(--mall-primary);
  font-weight: 700;
}
.vip-card { display:flex; justify-content:space-between; align-items:center; color:white; padding:20px; border-radius:18px; margin-bottom:15px; box-shadow:0 10px 24px rgba(0,0,0,0.12); cursor:pointer; transition:transform 0.1s; }
.vip-card:active { transform:scale(0.98); }
.vip-card.disabled { opacity:0.6; filter:grayscale(1); cursor:not-allowed; }
.vip-card.gold { background:linear-gradient(135deg, #ffd979, #d59b23); }
.vip-card.diamond { background:linear-gradient(135deg, #46a5ff, #05d2ff); }
.v-left { display:flex; align-items:center; gap:15px; font-size:18px; }
.v-desc { font-size:12px; opacity:0.9; font-weight:normal; margin-top:2px; }
.v-price { font-size:24px; font-weight:bold; }
/* 🔥 新增秒杀条样式 (UI优化版) 🔥 */
.seckill-bar-modal { position:absolute; bottom:0; left:0; width:100%; background:linear-gradient(to right, #f02d2d, var(--mall-primary)); color:white; padding:10px 15px; display:flex; justify-content:space-between; align-items:center; box-sizing: border-box; }
.glass-panel { background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,248,242,0.92)); border-radius: 22px; border: 1px solid rgba(255,255,255,0.8); box-shadow: var(--mall-shadow-card); }
.mall-nav-bar {
  position: relative;
  z-index: 5000;
}
.mall-nav-bar :deep(.van-nav-bar) {
  z-index: 5000 !important;
  isolation: isolate;
  background: var(--van-nav-bar-background);
  box-shadow: 0 10px 26px rgba(89, 40, 21, 0.08);
  border-bottom-left-radius: 18px;
  border-bottom-right-radius: 18px;
}
.mall-nav-bar :deep(.van-nav-bar::after) {
  display: none;
}
.mall-nav-bar :deep(.van-nav-bar__content) {
  position: relative;
  z-index: 5001;
  background: var(--van-nav-bar-background);
  backdrop-filter: blur(14px);
}
.mall-nav-bar :deep(.van-nav-bar__title),
.mall-nav-bar :deep(.van-icon),
.mall-nav-bar :deep(.van-nav-bar__text) {
  position: relative;
  z-index: 5002;
}
.mall-tabbar :deep(.van-tabbar) { left: 12px; right: 12px; bottom: 10px; width: auto; border-radius: 22px; overflow: hidden; background: rgba(255, 255, 255, 0.92); border: 1px solid rgba(255,255,255,0.78); box-shadow: 0 18px 36px rgba(85, 45, 27, 0.14); backdrop-filter: blur(18px); }
.mall-tabbar :deep(.van-tabbar-item--active) {
  background: linear-gradient(180deg, rgba(255,248,242,0.98), rgba(255,242,233,0.92));
}
.mall-tabbar :deep(.van-tabbar-item__text) { font-weight: 600; }
.mall-dialog :deep(.van-dialog) { width: calc(100% - 28px); max-width: 430px; border-radius: 26px; overflow: hidden; background: rgba(255,255,255,0.94); box-shadow: 0 24px 50px rgba(78, 41, 24, 0.18); }
.mall-dialog :deep(.van-dialog__header) { padding-top: 22px; font-size: 17px; font-weight: 800; color: var(--mall-text); }
.mall-dialog :deep(.van-dialog__footer) { border-top: 1px solid var(--mall-line); }
.sk-info { display:flex; flex-direction:column; justify-content:center; }
.sk-title { font-size:18px; font-weight:bold; margin-bottom:2px; }
.sk-sub { font-size:11px; opacity:0.9; }
.sk-countdown { text-align:right; display:flex; flex-direction:column; align-items:flex-end; }
</style>
