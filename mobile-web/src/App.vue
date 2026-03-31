<template>
  <div class="mobile-app">

    <!-- 顶部导航 -->
    <van-nav-bar
      v-if="!showPaySuccess && !showOrderDetail && activeTab !== 2 && !showProductDetail && !showAllOrders"
      :title="pageTitle"
      fixed placeholder z-index="99"
      :left-arrow="activeTab !== 0"
      @click-left="onClickLeft"
      :style="{ '--van-nav-bar-background': isVip ? '#333' : '#ee0a24', '--van-nav-bar-title-text-color': 'white', '--van-nav-bar-icon-color': 'white' }"
    />

    <!-- ==================== Tab 0: 首页 ==================== -->
    <div v-if="activeTab === 0 && !showPaySuccess && !showOrderDetail && !showAllOrders" class="tab-page">
      <div class="header-search-box" :style="{ background: isVip ? '#333' : '#ee0a24' }">
        <van-search v-model="searchKeyword" placeholder="搜手机、电脑..." shape="round" background="transparent" style="flex:1;" />
        <van-icon name="replay" color="white" size="24" @click="loadProducts(true)" style="margin-left:10px; opacity:0.9;" />
      </div>

      <div class="banner-box">
        <van-swipe :autoplay="3000" indicator-color="white" class="my-swipe">
          <van-swipe-item v-for="b in bannerList" :key="b.id"><img :src="b.img" class="banner-img" /></van-swipe-item>
          <van-swipe-item v-if="bannerList.length === 0"><div class="empty-banner">暂无轮播图，请去后台添加</div></van-swipe-item>
        </van-swipe>
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
        <van-divider :style="{ color: isVip ? '#dda246' : '#ee0a24', borderColor: isVip ? '#dda246' : '#ee0a24' }">{{ currentCategory }}</van-divider>
        <van-empty v-if="filteredGoodsList.length === 0" description="暂无相关商品" />
        <div class="goods-waterfall">
          <div v-for="item in filteredGoodsList" :key="item.id" class="goods-card" @click="openProductDetail(item)">
             <div class="img-wrapper"><img :src="item.img" /></div>
             <div class="info-wrapper">
               <div class="title">{{ item.title }}</div>
               <div class="tags">
                   <span v-if="!isVip" class="tag red">原价</span>
                   <span v-else class="tag gold">VIP价</span>
                   <span v-if="item.category.includes('拼团')" class="tag blue">拼团</span>
                   <span v-if="item.category.includes('秒杀')" class="tag red">秒杀</span>
               </div>
               <div class="bottom-row">
                 <div class="price">¥ <span class="num">{{ item.price.toFixed(0) }}</span>.{{ item.price.toFixed(2).split('.')[1] }}</div>
                 <div class="goods-actions">
                    <div class="btn-icon fav" @click.stop="toggleFavorite(item)"><van-icon :name="isFav(item.id) ? 'like' : 'like-o'" :color="isFav(item.id) ? '#ee0a24' : '#666'" /></div>
                    <div class="btn-icon cart" @click.stop="handleAddToCart(item)"><van-icon name="cart-o" /></div>
                 </div>
               </div>
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
        <van-submit-bar :price="calculateCartFinalPrice * 100" button-text="去结算" @submit="handleCartCheckout" class="custom-submit-bar"><van-checkbox v-model="isAllChecked" checked-color="#ee0a24" @click="toggleAllCheck">全选</van-checkbox></van-submit-bar>
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
          <div class="user-info" @click="logout">
            <img :src="currentUser.avatar" class="avatar" />
            <div class="text-info">
              <div class="nickname">
                {{ currentUser.nickname }}
                <van-icon name="edit" style="margin-left: 8px; font-size: 16px; opacity: 0.8;" @click.stop="openEditName" />
                <span style="font-size:12px; font-weight:normal; margin-left:10px; opacity:0.6; border:1px solid rgba(255,255,255,0.5); padding:0px 6px; border-radius:10px;"><van-icon name="exchange" /> 切换</span>
              </div>
              <div class="level-badge"><van-icon name="gem" /> {{ vipLevelName }}</div>
            </div>
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
        <div class="menu-group">
          <van-cell-group inset>
            <van-cell title="我的会员" :value="vipLevelName" icon="gem-o" is-link @click="openVipCenter" />
            <van-cell title="我的地址" icon="location-o" is-link @click="showAddressManager=true" />
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
              <span v-if="order.status===1" style="color:gray; font-size:12px;">等待商家发货...</span>
              <span v-if="order.status===5" style="color:#ee0a24; font-size:12px;">待好友成团...</span>
            </div>
          </div>
        </div>
        <div style="height: 30px;"></div>
      </div>
    </div>

    <!-- ==================== Tab 3: 拼团大厅 ==================== -->
    <div v-else-if="activeTab === 3 && !showPaySuccess && !showOrderDetail" class="tab-page" style="padding-bottom:60px;">
      <div style="background:#ee0a24; padding:20px; color:white; text-align:center;">
        <h2 style="margin:0;">🔥 拼团大厅</h2>
        <p style="font-size:12px; margin-top:5px; opacity:0.8;">{{ systemConfig.group_buy_people }}人成团 · 享{{ systemConfig.group_buy_discount * 10 }}折优惠</p>
      </div>
      <div class="goods-container" style="margin-top:-20px;">
        <div v-for="item in filteredGoodsList" :key="item.id" class="goods-card" style="margin-bottom:10px; display:flex; flex-direction:row; height:120px;" @click="openProductDetail(item)">
           <img :src="item.img" style="width:120px; height:120px; object-fit:cover;" />
           <div class="info-wrapper" style="padding:10px;">
             <div class="title">{{ item.title }}</div>
             <div class="tags"><span class="tag blue">{{ systemConfig.group_buy_people }}人团</span></div>
             <div style="margin-top:auto; display:flex; justify-content:space-between; align-items:center;">
               <div class="price" style="font-size:18px;">¥ {{ (item.price * systemConfig.group_buy_discount).toFixed(0) }} <span style="font-size:12px; color:#999; text-decoration:line-through; font-weight:normal;">¥{{ item.price }}</span></div>
               <van-button type="danger" size="small" round>去开团</van-button>
             </div>
           </div>
        </div>
      </div>
    </div>

    <!-- Tab 4: 秒杀大厅 -->
    <div v-else-if="activeTab === 4 && !showPaySuccess && !showOrderDetail" class="tab-page" style="padding-bottom:60px;">
      <div style="background:#ee0a24; padding:25px 20px; color:white; text-align:center;">
        <h2 style="margin:0; font-size:26px;">⚡ 疯狂秒杀</h2>
        <p style="font-size:13px; margin-top:5px; opacity:0.9;">限时限量 · 手慢无</p>
      </div>
      <div class="goods-container" style="margin-top:-25px;">
        <div v-for="item in filteredGoodsList" :key="item.id" class="goods-card" style="margin-bottom:12px; display:flex; flex-direction:row; height:130px;" @click="openProductDetail(item)">
           <div style="width:130px; height:130px; position:relative;">
               <img :src="item.img" style="width:100%; height:100%; object-fit:cover; border-radius:8px 0 0 8px;" />
               <div style="position:absolute;top:0;left:0;background:#ee0a24;color:white;font-size:10px;padding:2px 5px;border-radius:8px 0 8px 0;">秒杀中</div>
           </div>
           <div class="info-wrapper" style="padding:12px;">
             <div class="title" style="font-weight:bold;">{{ item.title }}</div>
             <div style="margin-top:auto;">
                <div style="color:#ee0a24; font-size:18px; font-weight:bold;">¥ {{ item.price }} <span style="color:#999; font-size:12px; text-decoration:line-through; font-weight:normal; margin-left:5px;">¥{{ (item.price * 1.5).toFixed(0) }}</span></div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <div style="height:4px; flex:1; background:#eee; border-radius:2px; margin-right:10px; overflow:hidden;"><div style="width:70%; height:100%; background:#ee0a24;"></div></div>
                    <van-button type="danger" size="small" round style="height:26px; padding:0 12px;">马上抢</van-button>
                </div>
             </div>
           </div>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <van-tabbar v-if="!showPaySuccess && !showOrderDetail && !showProductDetail && !showAllOrders" v-model="activeTab" :active-color="isVip ? '#dda246' : '#ee0a24'" inactive-color="#999">
      <van-tabbar-item icon="home-o" @click="currentCategory='🔥 爆款推荐'">首页</van-tabbar-item>
      <van-tabbar-item icon="shopping-cart-o" :badge="cartCount>0?cartCount:null">购物车</van-tabbar-item>
      <van-tabbar-item icon="user-o" :dot="!currentUser">我的</van-tabbar-item>
    </van-tabbar>

    <!-- 弹窗组件群 -->
    <van-dialog v-model:show="showGroupChoiceDialog" title="拼团方式" show-cancel-button cancel-button-text="我要开团" confirm-button-text="我有拼团码" confirm-button-color="#1989fa" @cancel="startNewGroup" @confirm="showJoinGroupInput=true"><div style="padding:20px; text-align:center; color:#666;">请选择您是要发起新的拼团，还是加入好友的团？</div></van-dialog>
    <van-dialog v-model:show="showJoinGroupInput" title="输入拼团码" show-cancel-button @confirm="joinGroup"><div style="padding:20px;"><van-field v-model="inputGroupCode" placeholder="请输入6位拼团码" input-align="center" style="background:#f5f5f5; border-radius:8px;" /></div></van-dialog>

    <van-dialog v-model:show="showBuyDialog" title="确认付款" show-cancel-button @confirm="confirmSingleOrder">
      <div class="pay-dialog-content">
        <div class="price-big">¥ {{ calculateFinalPrice }}</div>
        <div class="pay-row" @click="showAddressManager=true"><span class="label">📍 收货地址</span><span class="value link">{{ selectedAddress?selectedAddress.name:'去添加' }} ></span></div>
        <div class="pay-row" @click="openMyCoupons"><span class="label">🎟️ 优惠券</span><span class="value link" :class="{red: selectedCoupon}">{{ selectedCoupon?'-¥'+selectedCoupon.amount:'选择' }} ></span></div>
        <div class="pay-row"><span class="label">🪙 积分抵扣</span><van-switch v-model="usePoints" size="20px" active-color="#ee0a24" /></div>
      </div>
    </van-dialog>

    <van-dialog v-model:show="showCartConfirm" title="购物车结算" show-cancel-button @confirm="confirmCartOrder">
      <div class="pay-dialog-content">
        <div class="price-big">¥ {{ calculateCartFinalPrice }}</div>
        <div class="pay-row" @click="showAddressManager=true"><span class="label">📍 收货地址</span><span class="value link">{{ selectedAddress?selectedAddress.name:'去添加' }} ></span></div>
        <div class="pay-row" @click="openMyCoupons"><span class="label">🎟️ 优惠券</span><span class="value link" :class="{red: selectedCoupon}">{{ selectedCoupon?'-¥'+selectedCoupon.amount:'选择' }} ></span></div>
        <div class="pay-row"><span class="label">🪙 积分抵扣</span><van-switch v-model="usePoints" size="20px" active-color="#ee0a24" /></div>
      </div>
    </van-dialog>

    <!-- 🔥 新增：全部订单列表弹窗 (含Tabs) 🔥 -->
    <van-popup v-model:show="showAllOrders" position="bottom" :style="{ height: '100%', background: '#f7f8fa' }" closeable>
        <van-nav-bar title="我的订单" fixed placeholder z-index="100" />
        <van-tabs v-model:active="activeOrderTab" sticky offset-top="46" background="#fff" color="#ee0a24" title-active-color="#ee0a24">
            <van-tab title="全部" name="all"></van-tab>
            <van-tab title="待发货" name="wait_ship"></van-tab>
            <van-tab title="待收货" name="shipped"></van-tab>
            <van-tab title="已完成" name="completed"></van-tab>
        </van-tabs>
        <div style="padding:10px;">
            <van-empty v-if="filteredAllOrders.length === 0" description="暂无相关订单" />
            <div v-for="order in filteredAllOrders" :key="order.id" class="jd-order-card" @click="viewOrderDetail(order.id)">
                <div class="card-head"><span class="shop-name"><van-icon name="shop-o" /> Smart Mall 自营店</span><span class="status-txt" :class="'st-'+order.status">{{ getStatusText(order.status) }}</span></div>
                <div class="card-body"><img :src="order.img" /><div class="info"><div class="p-title">{{ order.title }}</div><div class="p-price">¥ {{ order.amount.toFixed(2) }}</div></div></div>
                <div class="card-foot">
                    <van-button v-if="order.status===2" size="small" round color="#ee0a24" @click.stop="confirmOrderReceipt(order)">确认收货</van-button>
                    <van-button v-if="order.status===3" size="small" round plain type="warning" @click.stop="openComment(order)">去评价</van-button>
                    <van-button v-if="order.status===4" size="small" round plain disabled>已评价</van-button>
                    <span v-if="order.status===1" style="color:gray; font-size:12px;">等待商家发货...</span>
                    <span v-if="order.status===5" style="color:#ee0a24; font-size:12px;">待好友成团...</span>
                </div>
            </div>
            <div style="height:40px; text-align:center; color:#ccc; font-size:12px; line-height:40px;">我是有底线的</div>
        </div>
    </van-popup>

    <!-- 全商品详情弹窗 -->
    <van-popup v-model:show="showProductDetail" position="bottom" :style="{ height: '100%' }" closeable>
        <div v-if="selectedItem" style="display:flex; flex-direction:column; height:100vh;">
            <div style="height:350px; position:relative;">
                <img :src="selectedItem.img" style="width:100%; height:100%; object-fit:cover;">
                <div v-if="isSeckillItem" class="seckill-bar-modal">
                    <div class="sk-info"><div class="sk-title">⚡ 疯狂秒杀</div><div class="sk-sub">手慢无 · 限时抢购</div></div>
                    <div class="sk-countdown"><div style="font-size:10px; margin-bottom:2px; opacity:0.8;">距结束仅剩</div><van-count-down :time="seckillTimeLeft" format="mm : ss" style="color:#fff000; font-weight:bold; font-size:20px; font-family:monospace;" @finish="handleSeckillFinish" /></div>
                </div>
            </div>

            <div style="padding:20px; background:white; flex:1; overflow-y:auto;">
                <div style="font-size:20px; margin-bottom:10px; font-weight:bold; line-height:1.4;">{{ selectedItem.title }}</div>
                <div style="color:#ee0a24; font-size:28px; font-weight:bold; margin-bottom:15px;">
                    ¥ {{ selectedItem.price }}
                    <span v-if="isSeckillItem" style="font-size:14px; color:#999; text-decoration:line-through; font-weight:normal; margin-left:10px;">¥{{ (selectedItem.price * 1.5).toFixed(2) }}</span>
                </div>

                <div v-if="isSeckillItem" style="background:#fff7f7; border:1px solid #ffebeb; padding:15px; border-radius:10px; margin-bottom:20px;">
                    <div style="font-weight:bold; color:#ee0a24; margin-bottom:5px;"><van-icon name="warning-o" /> 秒杀规则：</div>
                    <div style="font-size:13px; color:#666; line-height:1.6;">1. 秒杀商品库存有限，先到先得。<br>2. 请在倒计时结束前完成支付。<br>3. 倒计时结束后，将无法下单。</div>
                </div>

                <div style="margin-top:10px;">
                    <h4 style="margin-bottom:10px; border-left:4px solid #ee0a24; padding-left:10px;">商品详情</h4>
                    <p style="color:#666; font-size:14px; line-height:1.6; white-space: pre-wrap;">{{ selectedItem.description || '暂无商品介绍，请联系客服咨询详情。' }}</p>
                </div>
            </div>

            <div style="padding:10px 20px; background:white; display:flex; gap:15px; border-top:1px solid #eee;">
                <van-button block round color="#ff976a" :disabled="isSeckillItem && isSeckillExpired" @click="handleAddToCart(selectedItem)">加入购物车</van-button>
                <div class="btn-icon fav" @click.stop="toggleFavorite(selectedItem)" style="width:44px;height:44px;border:1px solid #eee;margin-right:-5px;"><van-icon :name="isFav(selectedItem.id) ? 'like' : 'like-o'" :color="isFav(selectedItem.id) ? '#ee0a24' : '#666'" size="20" /></div>
                <van-button block round :color="isSeckillItem ? 'linear-gradient(to right, #ff6034, #ee0a24)' : '#ee0a24'" :disabled="isSeckillItem && isSeckillExpired" @click="triggerBuyLogic">
                    {{ isSeckillItem ? (isSeckillExpired ? '已超时' : '立即秒杀') : (selectedItem.category.includes('拼团') ? '去开团/参团' : '立即购买') }}
                </van-button>
            </div>
        </div>
    </van-popup>

    <van-popup v-model:show="showCoupon" position="bottom" round closeable :style="{ height: '60%', background: '#f7f8fa' }">
      <div style="padding: 15px 15px 30px;">
        <h3 style="text-align:center; margin-top: 10px; margin-bottom: 20px; font-weight: 600; color: #333;">🧧 领券中心</h3>
        <div v-if="coupons.length === 0" style="text-align:center;color:gray;margin-top:50px;">暂无可用优惠券</div>
        <div v-for="c in coupons" :key="c.id" class="coupon-card">
          <div class="c-left" :class="{ 'got': c.got }"><div class="c-price"><span>¥</span>{{ c.amount }}</div><div class="c-cond">{{ c.desc }}</div><div class="circle-top"></div><div class="circle-bottom"></div></div>
          <div class="c-right"><div class="c-info"><div class="c-name"><span class="c-tag" :class="{'vip-tag': c.limit_level > 1}">{{ c.limit_level > 1 ? 'VIP专享' : '通用' }}</span>{{ c.name }}</div><div class="c-date">有效期至 2025.12.31</div></div><van-button size="small" round :color="c.got ? '#ebedf0' : 'linear-gradient(to right, #ff6034, #ee0a24)'" :style="{ color: c.got ? '#969799' : 'white', fontWeight: 'bold', height: '28px', padding: '0 15px' }" :disabled="c.got" @click="handleGetCoupon(c)">{{ c.got ? '已领取' : '立即领取' }}</van-button></div>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showOwnedCouponsPopup" position="bottom" round :style="{ height: '50%', background: '#f7f8fa' }">
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
      <div class="success-icon-box"><van-icon name="checked" color="white" size="60" /></div><h2 style="margin-top: 20px; color: #333;">支付成功</h2>
      <div v-if="lastOrderGroupCode" style="text-align:center;margin:10px 0;padding:10px;background:#f9f9f9;border-radius:8px;"><div>您的拼团码:</div><div style="font-size:24px;font-weight:bold;color:#ee0a24;letter-spacing:2px;">{{ lastOrderGroupCode }}</div><div style="font-size:12px;color:gray;">快去分享给好友参团吧!</div></div>
      <div class="succ-price">¥ {{ lastPaidAmount }}</div>
      <div style="width:85%; margin-top:50px; display: flex; gap: 15px;"><van-button plain block round style="flex:1" @click="finishPayment('home')">返回首页</van-button><van-button color="#07c160" block round style="flex:1" @click="finishPayment('order')">查看订单</van-button></div>
    </div>

    <div v-if="showOrderDetail" class="full-page-detail">
      <van-nav-bar title="订单详情" left-arrow @click-left="showOrderDetail=false" />
      <div class="detail-status-header"><div class="status-big"><van-icon name="logistics" size="24" />{{ getStatusText(currentOrderDetail.status) }}</div><div class="status-desc">感谢您在 Smart Mall 购物，欢迎再次光临</div></div>
      <div v-if="currentOrderDetail" style="padding: 0 15px; margin-top: -30px; position: relative; z-index: 2;">
        <div v-if="currentOrderDetail.group_code" class="card" style="margin-top:-20px;text-align:center;padding:15px;"><div style="color:#ee0a24;font-weight:bold;">拼团码：{{ currentOrderDetail.group_code }}</div><div style="font-size:12px;color:gray;">状态：{{ currentOrderDetail.status===5?'待成团':'拼团成功' }}</div></div>
        <div class="card detail-address-card"><div class="icon-side"><van-icon name="location" color="#ee0a24" size="24" /></div><div class="text-side"><div class="addr-title">收货信息</div><div class="addr-text">{{ currentOrderDetail.address }}</div></div></div>
        <div class="card detail-goods-card"><div class="shop-line"><van-icon name="shop-o" /> Smart Mall 自营店</div><div class="goods-row"><img :src="currentOrderDetail.img" /><div class="g-right"><div class="g-title">{{ currentOrderDetail.title }}</div><div class="g-price">¥ {{ currentOrderDetail.amount.toFixed(2) }}</div></div></div><div class="contact-line"><van-button size="small" icon="service-o" round>联系客服</van-button><van-button size="small" icon="phone-o" round>拨打电话</van-button></div></div>
        <div class="card detail-meta"><div class="meta-row"><span>订单编号</span><span>{{ currentOrderDetail.no }}</span></div><div class="meta-row"><span>下单时间</span><span>{{ currentOrderDetail.date }}</span></div><div class="meta-row"><span>支付方式</span><span>在线支付</span></div></div>
      </div>
    </div>

    <van-dialog v-model:show="showRecharge" title="余额充值" :show-confirm-button="false">
      <div style="padding:20px; text-align:center;"><van-field v-model="rechargeAmount" type="number" label="充值金额" placeholder="请输入金额" size="large" prefix="¥" class="beauty-input" /><div v-if="rechargeAmount > 0" style="margin-top:20px;"><p style="font-size:14px; color:#666;">请扫码支付 (模拟)</p><img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=SimulatePayment" style="width:150px; height:150px; margin:10px 0;" /><van-button type="success" block round @click="submitRecharge">✅ 我已确认支付</van-button></div></div>
    </van-dialog>

    <van-popup v-model:show="showMyCouponSelector" position="bottom" round :style="{ height: '40%' }"><div style="padding:20px;"><h3 style="text-align:center;">选择优惠券</h3><van-cell-group><van-cell v-for="c in myUsableCoupons" :key="c.id" :title="c.name" :value="`- ¥${c.amount}`" clickable @click="selectedCoupon=c; showMyCouponSelector=false" /><van-cell title="不使用优惠券" clickable @click="selectedCoupon=null; showMyCouponSelector=false" /></van-cell-group></div></van-popup>
    <van-popup v-model:show="showMoreMenu" position="bottom" round :style="{ height: '40%' }"><div style="padding:20px;"><h3 style="text-align:center;margin-bottom:10px;">更多服务</h3><van-grid :column-num="4" clickable><van-grid-item v-for="(item, i) in moreMenuPool" :key="i" :icon="item.icon" :text="item.text" @click="replaceMenuItem(item)" /></van-grid></div></van-popup>
    <van-popup v-model:show="showAddressManager" position="bottom" :style="{ height: '60%' }"><div style="padding:15px;"><h3>地址管理</h3><van-radio-group v-model="selectedAddrId"><div v-for="addr in addressList" :key="addr.id" class="addr-box" @click="selectedAddrId=addr.id;showAddressManager=false"><van-radio :name="addr.id" style="margin-right:10px;"></van-radio><div><b>{{ addr.name }} {{ addr.phone }}</b><br><span style="color:gray;font-size:12px;">{{ addr.detail }}</span></div></div></van-radio-group><van-button type="danger" block round style="margin-top:20px;" @click="showAddAddrForm=true">➕ 新增</van-button></div></van-popup>
    <van-dialog v-model:show="showAddAddrForm" title="新增地址" show-cancel-button @confirm="saveAddress"><van-cell-group inset><van-field v-model="newAddr.name" label="姓名" /><van-field v-model="newAddr.phone" label="电话" /><van-field v-model="newAddr.detail" label="地址" /></van-cell-group></van-dialog>
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
import { ref, computed, onMounted, reactive, watch } from 'vue'
import axios from 'axios'
import { showToast, showDialog, showSuccessToast, showLoadingToast, closeToast } from 'vant'
import draggable from 'vuedraggable'

const activeTab = ref(0); const goodsList = ref([]); const currentUser = ref(null)
const loginTab = ref(0); const loginForm = reactive({username:'', password:''}); const regForm = reactive({username:'', password:''})
const myOrderList = ref([]); const cartList = ref([])
const showBuyDialog = ref(false); const showCartConfirm = ref(false); const selectedItem = ref(null); const showPaySuccess = ref(false)
const showOrderDetail = ref(false); const currentOrderDetail = ref(null)
const showAddressManager = ref(false); const showAddAddrForm = ref(false); const addressList = ref([]); const selectedAddrId = ref(null); const newAddr = reactive({name:'', phone:'', detail:''})
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
const logisticsTraces = ref([]); const showSigninPopup = ref(false)
const systemConfig = ref({ group_buy_people: 2, seckill_time_limit: 5, group_buy_discount: 0.8 })
const showGroupChoiceDialog = ref(false); const showJoinGroupInput = ref(false); const inputGroupCode = ref(''); const pendingGroupAction = ref(null); const lastOrderGroupCode = ref(null)
const isGroupBuyMode = ref(false)
const coupons = ref([])

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
const isSeckillItem = computed(() => selectedItem.value && selectedItem.value.category.includes('秒杀'))

// 新增：我的优惠券弹窗状态
const showOwnedCouponsPopup = ref(false)

const currentMenu = ref([{text:'热卖',icon:'fire-o',type:'filter',key:'热卖'},{text:'手机',icon:'shopping-cart-o',type:'filter',key:'手机'},{text:'电脑',icon:'desktop-o',type:'filter',key:'电脑'},{text:'数码',icon:'tv-o',type:'filter',key:'数码'},{text:'拼团',icon:'friends-o',type:'filter',key:'拼团'},{text:'秒杀',icon:'clock-o',type:'filter',key:'秒杀'},{text:'领券',icon:'coupon-o',type:'action',act:'coupon'},{text:'更多',icon:'apps-o',type:'action',act:'more'}])
const moreMenuPool = ref([{text:'充值',icon:'gold-coin-o',type:'action',act:'recharge'},{text:'签到',icon:'gift-o',type:'action',act:'signin'},{text:'平板',icon:'points',type:'filter',key:'平板'},{text:'相机',icon:'photograph',type:'filter',key:'相机'},{text:'耳机',icon:'service-o',type:'filter',key:'耳机'},{text:'手表',icon:'clock',type:'filter',key:'手表'}])

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
    const res = await axios.get('http://localhost:5000/api/products')
    if(res.data.code === 200) goodsList.value = res.data.data.filter(item => item.is_on_sale)
    const bannerRes = await axios.get('http://localhost:5000/api/banners')
    if(bannerRes.data.code === 200) bannerList.value = bannerRes.data.data
    const cfgRes = await axios.get('http://localhost:5000/api/common/config')
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
  const res = await axios.post('http://localhost:5000/api/mobile/signin');
  if(res.data.code===200){ currentUser.value.points=res.data.points; showSigninPopup.value = true }
}

const openCouponCenter = async () => {
  showCoupon.value = true
  const res = await axios.get('http://localhost:5000/api/mobile/coupon/market')
  if(res.data.code === 200) {
      coupons.value = res.data.data.map(c => ({...c, got: false}))
      if(currentUser.value) {
          const myRes = await axios.get('http://localhost:5000/api/mobile/coupon/my')
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
    const res = await axios.post('http://localhost:5000/api/mobile/coupon/get', { id: c.id });
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
    const res = await axios.get('http://localhost:5000/api/mobile/coupon/my');
    if(res.data.code===200){
        myUsableCoupons.value=res.data.data;
        // 这里的 showMyCouponSelector 原本是下单用的，如果是仅查看不需要设置true，除非是在下单界面
        // 这里只是为了刷新数据
    }
}
const viewMyWalletCoupons = () => {
    if(!currentUser.value) return showToast('请登录');
    openMyCoupons().then(() => {
        showOwnedCouponsPopup.value = true
    })
}

const replaceMenuItem = (newItem) => { const moreIndex = currentMenu.value.findIndex(i => i.act === 'more'); const targetIndex = moreIndex > 0 ? moreIndex - 1 : 0; const oldItem = currentMenu.value[targetIndex]; currentMenu.value[targetIndex] = newItem; moreMenuPool.value.push(oldItem); const poolIndex = moreMenuPool.value.indexOf(newItem); if (poolIndex > -1) moreMenuPool.value.splice(poolIndex, 1); showMoreMenu.value = false; showToast(`已切换为 ${newItem.text}`) }
const openRecharge = () => { if(!currentUser.value) return showToast('请登录'); rechargeAmount.value=''; showRecharge.value=true }
const submitRecharge = async () => {
  if (!rechargeAmount.value) return showToast('请输入金额');
  showLoadingToast({ message: '充值中...', forbidClick: true });
  try {
    const res = await axios.post('http://localhost:5000/api/mobile/recharge', { amount: rechargeAmount.value });
    closeToast();
    if (res.data.code === 200) { showSuccessToast('充值成功'); if (currentUser.value) { currentUser.value.balance = res.data.balance; } showRecharge.value = false; rechargeAmount.value = ''; } else { showToast(res.data.msg || '充值失败'); }
  } catch (e) { closeToast(); showToast('网络错误'); }
}
const onLogin = async () => { try { const res = await axios.post('http://localhost:5000/api/mobile/login', loginForm); if(res.data.code===200){ currentUser.value=res.data.data; showSuccessToast('欢迎'); loadData(); } else showToast(res.data.msg) } catch(e){showToast('失败')} }
const onRegister = async () => { const res = await axios.post('http://localhost:5000/api/mobile/register', regForm); if(res.data.code===200){ showSuccessToast('注册成功'); loginTab.value=0; loginForm.username=regForm.username } else showToast(res.data.msg) }
const logout = () => { showDialog({ title: '提示', message: '确定要切换账号吗？', showCancelButton: true }).then(() => { currentUser.value=null; loginForm.username=''; loginForm.password=''; cartList.value=[]; myOrderList=[]; favoriteList=[]; myUsableCoupons.value=[]; coupons.value.forEach(c=>c.got=false); favIds.value=[]; showSuccessToast('已退出'); activeTab.value = 2; }) }
const openEditName = () => { editingName.value = currentUser.value.nickname; showEditNameDialog.value = true }
const submitEditName = async () => { if(!editingName.value) return showToast('昵称不能为空'); const res = await axios.post('http://localhost:5000/api/mobile/profile/update', { nickname: editingName.value }); if(res.data.code===200) { currentUser.value.nickname = editingName.value; showSuccessToast('修改成功') } else showToast(res.data.msg) }
const loadData = () => { loadMyOrders(); loadAddress(); loadCart(); loadFavorites(); openMyCoupons(); }
const loadCart = async () => { if(!currentUser.value) return; const res = await axios.get('http://localhost:5000/api/mobile/cart/list'); if(res.data.code===200) cartList.value = res.data.data.map(i => ({...i, checked: true})) }
const handleAddToCart = async (item) => { if(!currentUser.value) return showToast('请登录'); const res = await axios.post('http://localhost:5000/api/mobile/cart/add', { product_id: item.id }); if(res.data.code===200) { showSuccessToast('已加购'); loadCart() } }
const updateCartNum = async (item, num) => { if (num === undefined) num = item.num; await axios.post('http://localhost:5000/api/mobile/cart/update', { id: item.id, num: num }); loadCart() }
const toggleAllCheck = (val) => { cartList.value.forEach(item => item.checked = val) }

// 🔥 核心修改：点击商品 -> 打开统一详情页 (openProductDetail) 🔥
// 代替原来的 handleBuyNow，所有商品点击都走这里
const handleBuyNow = (item) => openProductDetail(item)

const openProductDetail = (item) => {
    selectedItem.value = item
    showFavorites.value = false

    // 如果是秒杀商品，初始化倒计时
    if (item.category.includes('秒杀')) {
        seckillTimeLeft.value = systemConfig.value.seckill_time_limit * 60 * 1000
        isSeckillExpired.value = false
    }

    // 打开通用详情弹窗
    showProductDetail.value = true
}

// 🔥 详情页底部的按钮触发逻辑 🔥
const triggerBuyLogic = () => {
    if(!currentUser.value){ showToast('请登录'); showProductDetail.value=false; activeTab.value=2; return }

    const item = selectedItem.value;
    selectedCoupon.value = null;
    usePoints.value = false;

    // 1. 秒杀商品
    if(item.category.includes('秒杀')) {
        if(isSeckillExpired.value) return showDialog({ message: '秒杀已超时，无法支付，请重新选择商品。' });
        isGroupBuyMode.value = false;
        showProductDetail.value = false;
        showBuyDialog.value = true;
        if(addressList.value.length===0) loadAddress()
        return;
    }

    // 2. 拼团商品（必须是在拼团大厅 activeTab=3 时，或者商品本身就是拼团类）
    // 逻辑优化：只要商品含"拼团"标签，默认走拼团逻辑，或者让用户选？
    // 按照之前逻辑：含拼团标签 -> 弹拼团选择
    if(item.category.includes('拼团')) {
        isGroupBuyMode.value = true;
        showProductDetail.value = false;
        showGroupChoiceDialog.value = true;
        if(addressList.value.length===0) loadAddress()
        return;
    }

    // 3. 普通商品
    isGroupBuyMode.value = false;
    showProductDetail.value = false;
    showBuyDialog.value = true;
    if(addressList.value.length===0) loadAddress()
}

// 🔥 秒杀倒计时结束 🔥
const handleSeckillFinish = () => {
    isSeckillExpired.value = true;
    // 不强制弹Toast干扰用户，只把按钮变灰
}

const startNewGroup = () => { pendingGroupAction.value = 'create'; showBuyDialog.value = true }
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

const confirmSingleOrder = async () => { await processPay('http://localhost:5000/api/mobile/order', { product_id: selectedItem.value.id, address_id: selectedAddrId.value, coupon_id: selectedCoupon.value?.id, use_points: usePoints.value, group_action: isGroupBuyMode.value ? pendingGroupAction.value : null, group_code: isGroupBuyMode.value ? inputGroupCode.value : null }) }
const confirmCartOrder = async () => { await processPay('http://localhost:5000/api/mobile/cart/checkout', { cart_ids: checkedCartItems.value.map(i=>i.id), address_id: selectedAddrId.value, coupon_id: selectedCoupon.value?.id, use_points: usePoints.value }) }
const processPay = async (url, data) => {
    if(!selectedAddrId.value) return showToast('请选地址');
    const amountToPay = calculateFinalPrice.value > 0 ? calculateFinalPrice.value : calculateCartFinalPrice.value;
    showLoadingToast({message:'支付中...', forbidClick:true, duration:0});
    try {
        await new Promise(r=>setTimeout(r,1500));
        const res = await axios.post(url, data);
        closeToast();
        if(res.data.code===200) { currentUser.value.balance=res.data.balance; currentUser.value.points=res.data.points; lastPaidAmount.value = amountToPay; lastOrderGroupCode.value = res.data.group_code || null; showPaySuccess.value=true; loadData(); pendingGroupAction.value = null; inputGroupCode.value = ''; } else { showToast(res.data.msg) }
    } catch(e) { closeToast(); showToast('网络请求失败') }
}
const finishPayment = (target) => { showPaySuccess.value=false; activeTab.value = target==='order'?2:0 }
const loadMyOrders = async () => { if(!currentUser.value)return; const res = await axios.get('http://localhost:5000/api/mobile/my_orders'); if(res.data.code===200) myOrderList.value=res.data.data }
const loadAddress = async () => { const res = await axios.get('http://localhost:5000/api/mobile/address'); if(res.data.code===200) { addressList.value=res.data.data; if(addressList.value.length>0 && !selectedAddrId.value) selectedAddrId.value=addressList.value[0].id } }
const saveAddress = async () => { await axios.post('http://localhost:5000/api/mobile/address', newAddr); showSuccessToast('成功'); loadAddress(); showAddAddrForm.value=false }
const confirmOrderReceipt = async (order) => { await axios.post(`http://localhost:5000/api/mobile/orders/${order.id}/confirm`); showSuccessToast('完成'); loadMyOrders() }
const viewOrderDetail = async (id) => { showLoadingToast('加载...'); try { const res = await axios.get(`http://localhost:5000/api/mobile/orders/${id}`); const logRes = await axios.get(`http://localhost:5000/api/mobile/orders/${id}/logistics`); if(res.data.code===200) { currentOrderDetail.value=res.data.data; logisticsTraces.value = logRes.data.data || []; showOrderDetail.value=true } } finally { closeToast() } }
const toggleFavorite = async (item) => {
    if(!currentUser.value) return showToast('请登录');
    const res = await axios.post('http://localhost:5000/api/mobile/favorite/toggle', { product_id: item.id });
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
    const res = await axios.get('http://localhost:5000/api/mobile/favorites');
    if(res.data.code===200) {
        favoriteList.value = res.data.data;
        // 提取ID
        favIds.value = res.data.data.map(i => i.id);
    }
}
const openComment = (order) => { commentForm.order_id = order.id; commentForm.content = ''; commentForm.rating = 5; showCommentDialog.value = true }
const submitComment = async () => { const res = await axios.post('http://localhost:5000/api/mobile/comments/add', commentForm); if(res.data.code === 200) { showSuccessToast('评价成功'); loadMyOrders(); showCommentDialog.value=false } }
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
        const res = await axios.post('http://localhost:5000/api/mobile/vip/upgrade', { level: pendingVipLevel.value })
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
body { margin: 0; background-color: #f7f8fa; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif; }
.mobile-app { padding-bottom: 60px; max-width: 600px; margin: 0 auto; min-height: 100vh; position: relative; }
.user-header-card { margin: 0; padding: 40px 20px 100px; background: linear-gradient(135deg, #ff6034, #ee0a24); color: white; border-bottom-left-radius: 30px; border-bottom-right-radius: 30px; }
.user-header-card.is-vip { background: linear-gradient(135deg, #333, #555); }
.data-row { display: flex; justify-content: space-around; text-align: center; background: white; margin: 0 20px; padding: 20px 0; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-top: -80px; color: #333; position: relative; z-index: 2; }
.login-wrapper { min-height: 80vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
.login-card { width: 100%; background: white; border-radius: 16px; padding: 30px 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); }
.login-header h3 { text-align: center; color: #333; margin: 0; font-size: 24px; }
.login-header p { text-align: center; color: #999; font-size: 14px; margin-top: 5px; margin-bottom: 30px; }
.beauty-input { background-color: #f5f6f8; border-radius: 24px; margin-bottom: 15px; padding: 10px 15px; }
.tab-page { background: #f7f8fa; min-height: 100vh; }
.header-search-box { padding: 10px; display: flex; align-items: center; position: sticky; top: 0; z-index: 99; }
.banner-box { padding: 10px; }
.my-swipe .van-swipe-item { border-radius: 12px; overflow: hidden; height: 160px; }
.banner-img { width: 100%; height: 100%; object-fit: cover; }
.empty-banner { background: #ddd; height: 100%; display: flex; align-items: center; justify-content: center; color: gray; }
.drag-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px 0; padding: 15px 0; background: white; margin: 0 10px; border-radius: 12px; }
.drag-item { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.icon-circle { width: 44px; height: 44px; background: #f7f8fa; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 6px; }
.menu-text { font-size: 12px; color: #333; }
.seckill-bar { display: flex; justify-content: space-between; align-items: center; background: #fff0f0; margin: 10px; padding: 10px 15px; border-radius: 8px; border: 1px solid #ffcccc; }
.sk-left { display: flex; align-items: center; color: #ee0a24; font-weight: bold; gap: 5px; }
.sk-timer { color: #ee0a24; font-weight: bold; }
.goods-container { padding: 0 10px; }
.goods-waterfall { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.goods-card { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.03); display: flex; flex-direction: column; }
.img-wrapper { position: relative; padding-top: 100%; width: 100%; }
.img-wrapper img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }
.info-wrapper { padding: 10px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.title { font-size: 14px; color: #333; line-height: 1.4; height: 40px; overflow: hidden; margin-bottom: 5px; }
.tags { display: flex; gap: 4px; margin-bottom: 5px; }
.tag { font-size: 10px; padding: 1px 4px; border-radius: 4px; }
.tag.red { border: 1px solid #ee0a24; color: #ee0a24; }
.tag.gold { background: #333; color: #ffd700; }
.tag.blue { background: #e8f3ff; color: #1989fa; border: 1px solid #a3d3ff; }
.vip-tag { background: #333; color: gold; border-color: #333; }
.bottom-row { display: flex; justify-content: space-between; align-items: center; }
.price { color: #ee0a24; font-weight: bold; font-size: 16px; }
.price .num { font-size: 20px; }
.goods-actions { display: flex; gap: 8px; }
.btn-icon { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.btn-icon.fav { background: #f5f5f5; color: #666; transition: all 0.2s; }
.btn-icon.fav:active { color: #ee0a24; background: #ffebeb; }
.btn-icon.cart { background: #ee0a24; color: white; box-shadow: 0 2px 6px rgba(238,10,36,0.4); }
.empty-cart { padding: 60px 0; text-align: center; }
.cart-list-container { padding-bottom: 50px; }
.cart-item { background: white; margin: 10px; padding: 10px; border-radius: 12px; display: flex; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
.cart-img { width: 90px; height: 90px; border-radius: 6px; object-fit: cover; margin: 0 10px; }
.cart-info { flex: 1; height: 90px; display: flex; flex-direction: column; justify-content: space-between; }
.cart-title { font-size: 14px; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cart-footer { display: flex; justify-content: space-between; align-items: center; }
.cart-price { color: #ee0a24; font-weight: bold; font-size: 16px; }
.custom-submit-bar { bottom: 50px; border-top: 1px solid #f5f5f5; }
.user-info { display: flex; align-items: center; margin-bottom: 20px; cursor: pointer; }
.avatar { width: 64px; height: 64px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.6); }
.text-info { margin-left: 15px; }
.nickname { font-size: 20px; font-weight: bold; display: flex; align-items: center; }
.level-badge { background: rgba(0,0,0,0.2); padding: 2px 10px; border-radius: 12px; font-size: 12px; margin-top: 5px; }
.data-item .num { font-size: 20px; font-weight: bold; margin-bottom: 5px; }
.data-item .lbl { font-size: 12px; color: #999; }
.menu-group { margin-top: 20px; }
.jd-order-section { margin: 15px; }
.sec-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding: 0 5px; }
.sec-title { font-weight: bold; font-size: 16px; color: #333; }
.sec-more { font-size: 12px; color: #999; }
.empty-order-box { text-align: center; color: #ccc; padding: 40px 0; }
.jd-order-card { background: white; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.card-head { display: flex; justify-content: space-between; font-size: 12px; border-bottom: 1px solid #f9f9f9; padding-bottom: 10px; margin-bottom: 10px; }
.shop-name { font-weight: bold; display: flex; align-items: center; gap: 4px; }
.status-txt.st-1 { color: #ee0a24; }
.status-txt.st-2 { color: #ff976a; }
.status-txt.st-3 { color: #07c160; }
.card-body { display: flex; align-items: center; }
.card-body img { width: 70px; height: 70px; border-radius: 6px; margin-right: 12px; object-fit: cover; }
.card-body .info { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.p-title { font-size: 14px; color: #333; font-weight: 500; line-height: 1.4; margin-bottom: 5px; }
.p-price { color: #ee0a24; font-weight: bold; font-size: 15px; }
.card-foot { text-align: right; margin-top: 12px; border-top: 1px solid #f9f9f9; padding-top: 10px; }
.full-page-success { position: fixed; top: 0; left: 0; width: 100%; height: 100vh; background: white; z-index: 9999; display: flex; flex-direction: column; align-items: center; padding-top: 100px; }
.success-icon-box { width: 80px; height: 80px; background: #07c160; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(7,193,96,0.3); }
.succ-price { font-size: 48px; font-weight: bold; margin-top: 20px; font-family: sans-serif; }
.full-page-detail { position: fixed; top: 0; left: 0; width: 100%; height: 100vh; background: #f7f8fa; z-index: 200; overflow-y: auto; }
.detail-status-header { background: linear-gradient(to right, #ff6034, #ee0a24); color: white; padding: 25px 20px 50px; }
.status-big { font-size: 20px; font-weight: bold; display: flex; align-items: center; gap: 10px; margin-bottom: 5px; }
.status-desc { font-size: 12px; opacity: 0.8; margin-left: 34px; }
.card { background: white; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.detail-address-card { display: flex; align-items: center; }
.icon-side { margin-right: 15px; }
.addr-title { font-weight: bold; font-size: 14px; margin-bottom: 4px; }
.addr-text { font-size: 13px; color: #666; line-height: 1.4; }
.g-right { margin-left: 15px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.g-title { font-size: 14px; font-weight: 500; line-height: 1.4; }
.g-price { font-size: 18px; color: #ee0a24; font-weight: bold; }
.detail-meta .meta-row { display: flex; justify-content: space-between; font-size: 12px; color: #999; margin-bottom: 8px; }
.contact-line { margin-top: 15px; border-top: 1px solid #f9f9f9; padding-top: 10px; display: flex; justify-content: center; gap: 20px; }
.pay-dialog-content { padding: 10px; }
.price-big { text-align: center; font-size: 36px; font-weight: bold; color: #ee0a24; margin: 20px 0; }
.pay-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #f5f5f5; font-size: 15px; }
.pay-row .link { color: #999; display: flex; align-items: center; }
.pay-row .link.red { color: #ee0a24; }
.addr-box { background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; align-items: center; }
.fav-item { display: flex; background: white; padding: 10px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); align-items: center; }
.fav-item img { width: 60px; height: 60px; border-radius: 4px; margin-right: 10px; object-fit: cover; }
.f-title { font-weight: bold; font-size: 14px; margin-bottom: 5px; }
.f-price { color: #ee0a24; font-weight: bold; }
.coupon-card { display: flex; height: 90px; background: white; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden; position: relative; }
.c-left { width: 105px; background: linear-gradient(135deg, #ff6034, #ee0a24); color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; border-right: 2px dashed #f7f8fa; }
.c-left.got { background: #c8c9cc; }
.c-price { font-size: 32px; font-weight: bold; line-height: 1; font-family: sans-serif; }
.c-price span { font-size: 14px; margin-right: 2px; font-weight: normal; }
.c-cond { font-size: 11px; margin-top: 6px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px; }
.circle-top, .circle-bottom { position: absolute; width: 12px; height: 12px; background: #f7f8fa; border-radius: 50%; right: -6px; z-index: 2; }
.circle-top { top: -6px; }
.circle-bottom { bottom: -6px; }
.c-right { flex: 1; padding: 0 15px 0 20px; display: flex; justify-content: space-between; align-items: center; }
.c-info { display: flex; flex-direction: column; justify-content: center; gap: 6px; }
.c-name { font-size: 15px; font-weight: bold; color: #323233; display: flex; align-items: center; }
.c-tag { font-size: 10px; background: #fff0f0; color: #ee0a24; padding: 1px 4px; border-radius: 4px; margin-right: 6px; font-weight: normal; border: 1px solid rgba(238, 10, 36, 0.2); }
.c-left.got + .c-right .c-tag { background: #f2f3f5; color: #969799; border-color: #ebedf0; }
.c-date { font-size: 11px; color: #969799; }
.vip-card { display:flex; justify-content:space-between; align-items:center; color:white; padding:20px; border-radius:12px; margin-bottom:15px; box-shadow:0 4px 12px rgba(0,0,0,0.1); cursor:pointer; transition:transform 0.1s; }
.vip-card:active { transform:scale(0.98); }
.vip-card.disabled { opacity:0.6; filter:grayscale(1); cursor:not-allowed; }
.vip-card.gold { background:linear-gradient(135deg, #FFD700, #DAA520); }
.vip-card.diamond { background:linear-gradient(135deg, #4facfe, #00f2fe); }
.v-left { display:flex; align-items:center; gap:15px; font-size:18px; }
.v-desc { font-size:12px; opacity:0.9; font-weight:normal; margin-top:2px; }
.v-price { font-size:24px; font-weight:bold; }
/* 🔥 新增秒杀条样式 (UI优化版) 🔥 */
.seckill-bar-modal { position:absolute; bottom:0; left:0; width:100%; background:linear-gradient(to right, #f02d2d, #ee0a24); color:white; padding:10px 15px; display:flex; justify-content:space-between; align-items:center; box-sizing: border-box; }
.sk-info { display:flex; flex-direction:column; justify-content:center; }
.sk-title { font-size:18px; font-weight:bold; margin-bottom:2px; }
.sk-sub { font-size:11px; opacity:0.9; }
.sk-countdown { text-align:right; display:flex; flex-direction:column; align-items:flex-end; }
</style>