<template>
  <div class="mobile-app">

    <!-- 顶部导航 -->
    <van-nav-bar
      class="mall-nav-bar"
      v-if="!showPaySuccess && !showOrderDetail && activeTab !== 2 && !showProductDetail && !showAllOrders && !showBuyDialog && !showCartConfirm"
      :title="pageTitle"
      fixed placeholder z-index="99"
      :left-arrow="activeTab !== 0"
      @click-left="onClickLeft"
      :style="{
        '--van-nav-bar-background': topNavTheme.background,
        '--van-nav-bar-title-text-color': topNavTheme.titleColor,
        '--van-nav-bar-icon-color': topNavTheme.iconColor,
        width: 'calc(100% - 24px)',
        maxWidth: '576px',
        left: '50%',
        right: 'auto',
        top: '8px',
        transform: 'translateX(-50%)',
        borderBottomLeftRadius: '18px',
        borderBottomRightRadius: '18px',
        overflow: 'hidden'
      }"
    />

    <!-- ==================== Tab 0: 首页 ==================== -->
    <HomeTab
      v-if="activeTab === 0 && !showPaySuccess && !showOrderDetail && !showAllOrders"
      v-model:search-keyword="searchKeyword"
      v-model:current-menu="currentMenu"
      :is-vip="isVip"
      :goods-list="goodsList"
      :banner-list="bannerList"
      :current-category="currentCategory"
      :filtered-goods-list="filteredGoodsList"
      :load-products="loadProducts"
      :handle-grid-click="handleGridClick"
      :get-seckill-status-tag="getSeckillStatusTag"
      :is-fav="isFav"
      :toggle-favorite="toggleFavorite"
      :handle-add-to-cart="handleAddToCart"
      :open-product-detail="openProductDetail"
    />

    <!-- ==================== Tab 1: 购物车 ==================== -->
    <CartTab
      v-else-if="activeTab === 1 && !showPaySuccess && !showOrderDetail && !showAllOrders"
      v-model:is-all-checked="isAllChecked"
      :cart-list="cartList"
      :calculate-cart-final-price="calculateCartFinalPrice"
      :update-cart-num="updateCartNum"
      :handle-cart-checkout="handleCartCheckout"
      :go-home="onClickLeft"
    />

    <!-- ==================== Tab 2: 会员中心 ==================== -->
    <ProfileTab
      v-else-if="activeTab === 2 && !showPaySuccess && !showOrderDetail && !showAllOrders"
      v-model:login-tab="loginTab"
      :current-user="currentUser"
      :is-vip="isVip"
      :vip-level-name="vipLevelName"
      :hero-text="heroText"
      :login-form="loginForm"
      :reg-form="regForm"
      :my-usable-coupons="myUsableCoupons"
      :my-order-list="myOrderList"
      :fav-ids="favIds"
      :on-login="onLogin"
      :on-register="onRegister"
      :logout="logout"
      :open-edit-name="openEditName"
      :handle-avatar-change="handleAvatarChange"
      :open-edit-hero-text="openEditHeroText"
      :view-my-wallet-coupons="viewMyWalletCoupons"
      :open-vip-center="openVipCenter"
      :open-change-password-dialog="openChangePasswordDialog"
      :open-recharge="openRecharge"
      :open-favorites="openFavoritesPanel"
      :open-address-manager="openAddressManagerPanel"
      :open-order-list="openOrderList"
      :view-order-detail="viewOrderDetail"
      :confirm-order-receipt="confirmOrderReceipt"
      :open-comment="openComment"
      :cancel-order="cancelOrder"
      :get-status-text="getStatusText"
    />

    <!-- ==================== Tab 3: 拼团大厅 ==================== -->
    <ActivityHallTab
      v-else-if="activeTab === 3 && !showPaySuccess && !showOrderDetail"
      mode="group"
      :system-config="systemConfig"
      :filtered-goods-list="filteredGoodsList"
      :open-product-detail="openProductDetail"
      :get-seckill-status-tag="getSeckillStatusTag"
      :get-seckill-status-text="getSeckillStatusText"
      :get-seckill-progress="getSeckillProgress"
    />

    <!-- Tab 4: 秒杀大厅 -->
    <ActivityHallTab
      v-else-if="activeTab === 4 && !showPaySuccess && !showOrderDetail"
      mode="seckill"
      :system-config="systemConfig"
      :filtered-goods-list="filteredGoodsList"
      :open-product-detail="openProductDetail"
      :get-seckill-status-tag="getSeckillStatusTag"
      :get-seckill-status-text="getSeckillStatusText"
      :get-seckill-progress="getSeckillProgress"
    />

    <!-- 底部导航 -->
    <van-tabbar v-if="!showPaySuccess && !showOrderDetail && !showProductDetail && !showAllOrders && !showBuyDialog && !showCartConfirm" class="mall-tabbar" v-model="activeTab" :active-color="isVip ? '#dda246' : '#ee0a24'" inactive-color="#999">
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
          <img :src="singlePayQrSrc" class="pay-qr-img" alt="单品支付二维码" />
          <van-button block round color="linear-gradient(135deg, #24c07b, #07c160)" class="pay-confirm-btn" :loading="isPaySubmitting" :disabled="isPaySubmitting" @click="confirmSingleOrder">我已确认支付</van-button>
        </div>
      </div>
    </van-dialog>

    <van-dialog v-model:show="showCartConfirm" class-name="mall-dialog" title="购物车结算" :show-confirm-button="false" show-cancel-button>
      <div class="pay-dialog-content glass-panel">
        <div class="price-big">¥ {{ calculateCartFinalPrice }}</div>
        <div class="pay-row" @click="showAddressManager=true"><span class="label">📍 收货地址</span><span class="value link">{{ selectedAddress?selectedAddress.name:'去添加' }} ></span></div>
        <div v-if="!checkedCartHasSeckill" class="pay-row" @click="openCheckoutCouponSelector"><span class="label">🎟️ 优惠券</span><span class="value link" :class="{red: selectedCoupon}">{{ selectedCoupon?'-¥'+selectedCoupon.amount:'选择' }} ></span></div>
        <div v-if="!checkedCartHasSeckill" class="pay-row"><span class="label">🪙 积分抵扣</span><van-switch v-model="usePoints" size="20px" active-color="#ee0a24" /></div>
        <div v-else class="pay-row pay-row-note"><span class="label">秒杀规则</span><span class="value">购物车含秒杀商品时不支持优惠券与积分</span></div>
        <div class="pay-qr-box">
          <div class="pay-qr-tip">请使用微信或支付宝扫码支付</div>
          <img :src="cartPayQrSrc" class="pay-qr-img" alt="购物车支付二维码" />
          <van-button block round color="linear-gradient(135deg, #24c07b, #07c160)" class="pay-confirm-btn" :loading="isPaySubmitting" :disabled="isPaySubmitting" @click="confirmCartOrder">我已确认支付</van-button>
        </div>
      </div>
    </van-dialog>

    <AllOrdersPopup
      v-model:show="showAllOrders"
      v-model:active-order-tab="activeOrderTab"
      :filtered-all-orders="filteredAllOrders"
      :get-status-text="getStatusText"
      :view-order-detail="viewOrderDetail"
      :confirm-order-receipt="confirmOrderReceipt"
      :open-comment="openComment"
      :cancel-order="cancelOrder"
    />

    <ProductDetailPopup
      v-model:show="showProductDetail"
      :selected-item="selectedItem"
      :is-seckill-item="isSeckillItem"
      :selected-item-is-group="selectedItemIsGroup"
      :current-seckill-status="currentSeckillStatus"
      :can-buy-seckill-now="canBuySeckillNow"
      :seckill-time-left="seckillTimeLeft"
      :product-comments="productComments"
      :get-seckill-status-tag="getSeckillStatusTag"
      :get-seckill-status-text="getSeckillStatusText"
      :handle-seckill-finish="handleSeckillFinish"
      :handle-add-to-cart="handleAddToCart"
      :toggle-favorite="toggleFavorite"
      :is-fav="isFav"
      :buy-group-item-directly="buyGroupItemDirectly"
      :trigger-buy-logic="triggerBuyLogic"
    />

    <van-popup
      v-model:show="showCoupon"
      class="sheet-popup mobile-shell-popup"
      position="bottom"
      :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }"
    >
      <div class="popup-mobile-shell coupon-shell">
        <van-nav-bar title="领券中心" left-arrow @click-left="showCoupon = false" />
        <div class="popup-mobile-content coupon-content">
          <div v-if="coupons.length === 0" class="coupon-empty-state">
            <van-icon name="coupon-o" size="40" />
            <p>暂无可用优惠券</p>
          </div>
          <div v-for="c in coupons" :key="c.id" class="coupon-card">
            <div class="c-left" :class="{ 'got': c.got }"><div class="c-price"><span>¥</span>{{ c.amount }}</div><div class="c-cond">{{ c.desc }}</div><div class="circle-top"></div><div class="circle-bottom"></div></div>
            <div class="c-right"><div class="c-info"><div class="c-name"><span class="c-tag" :class="{'vip-tag': c.limit_level > 1}">{{ c.limit_level > 1 ? 'VIP专享' : '通用' }}</span>{{ c.name }}</div><div class="c-date">有效期至 2025.12.31</div></div><van-button size="small" round :color="c.got ? '#ebedf0' : 'linear-gradient(to right, #ff6034, #ee0a24)'" :style="{ color: c.got ? '#969799' : 'white', fontWeight: 'bold', height: '30px', padding: '0 16px' }" :disabled="c.got" @click="handleGetCoupon(c)">{{ c.got ? '已领取' : '立即领取' }}</van-button></div>
          </div>
        </div>
      </div>
    </van-popup>

    <van-popup
      v-model:show="showOwnedCouponsPopup"
      class="sheet-popup mobile-shell-popup"
      position="bottom"
      :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }"
    >
      <div class="popup-mobile-shell coupon-shell">
        <van-nav-bar title="我的卡包" left-arrow @click-left="showOwnedCouponsPopup = false" />
        <div class="popup-mobile-content coupon-content">
          <div v-if="myUsableCoupons.length === 0" class="coupon-empty-state">
            <van-icon name="coupon-o" size="40" />
            <p>暂无优惠券</p>
          </div>
          <div v-for="c in myUsableCoupons" :key="c.id" class="coupon-card">
            <div class="c-left"><div class="c-price"><span>¥</span>{{ c.amount }}</div><div class="c-cond">满{{ c.min_spend }}可用</div><div class="circle-top"></div><div class="circle-bottom"></div></div>
            <div class="c-right"><div class="c-info"><div class="c-name">{{ c.name }}</div><div class="c-date">有效期至 2025.12.31</div></div><van-button size="small" round color="#ee0a24" style="height:30px; padding:0 16px;" @click="showOwnedCouponsPopup=false; activeTab=0">去使用</van-button></div>
          </div>
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

    <OrderDetailView
      v-model:show="showOrderDetail"
      :current-order-detail="currentOrderDetail"
      :logistics-traces="logisticsTraces"
      :get-status-text="getStatusText"
      :cancel-order="cancelOrder"
      @contact-qq="openQQServicePopup"
      @contact-phone="openPhoneServicePopup"
    />

    <van-dialog v-model:show="showRecharge" class-name="mall-dialog" title="余额充值" :show-confirm-button="false">
      <div style="padding:20px; text-align:center;">
        <van-field
          v-model="rechargeAmount"
          type="number"
          label="充值金额"
          placeholder="请输入金额"
          size="large"
          prefix="¥"
          class="beauty-input"
        />
        <van-button
          v-if="!rechargeAmount || Number(rechargeAmount) <= 0"
          block
          round
          plain
          color="#969799"
          style="margin-top: 18px;"
          @click="showRecharge = false"
        >
          退出
        </van-button>
        <div v-if="rechargeAmount > 0" class="pay-qr-box">
          <div class="pay-qr-tip">请使用微信或支付宝扫码支付</div>
          <img :src="rechargePayQrSrc" class="pay-qr-img" alt="充值支付二维码" />
          <van-button
            block
            round
            color="linear-gradient(135deg, #24c07b, #07c160)"
            class="pay-confirm-btn"
            @click="submitRecharge"
          >
            我已确认支付
          </van-button>
          <van-button
            block
            round
            plain
            color="#969799"
            style="margin-top: 12px;"
            @click="showRecharge = false"
          >
            退出
          </van-button>
        </div>
      </div>
    </van-dialog>

    <van-popup
      v-model:show="showMyCouponSelector"
      class="sheet-popup mobile-shell-popup"
      position="bottom"
      :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }"
    >
      <div class="popup-mobile-shell coupon-selector-shell">
        <van-nav-bar title="选择优惠券" left-arrow @click-left="showMyCouponSelector = false" />
        <div class="popup-mobile-content coupon-selector-content">
          <van-cell-group inset class="coupon-selector-group">
            <van-cell
              v-for="c in myUsableCoupons"
              :key="c.id"
              class="coupon-selector-cell"
              :class="{ 'coupon-selector-cell-disabled': !canUseCouponForCurrentCheckout(c) }"
              :title="c.name"
              :value="`- ¥${c.amount}`"
              clickable
              @click="selectCheckoutCoupon(c)"
            />
            <van-cell
              class="coupon-selector-cell coupon-selector-cell-muted"
              title="不使用优惠券"
              clickable
              @click="selectCheckoutCoupon(null)"
            />
          </van-cell-group>
        </div>
      </div>
    </van-popup>
    <van-popup v-model:show="showMoreMenu" position="bottom" round :style="{ height: '40%' }"><div style="padding:20px;"><h3 style="text-align:center;margin-bottom:10px;">更多服务</h3><van-grid :column-num="4" clickable><van-grid-item v-for="(item, i) in moreMenuPool" :key="i" :icon="item.icon" :text="item.text" @click="replaceMenuItem(item)" /></van-grid></div></van-popup>
    <AddressManagerPopup
      v-model:show="showAddressManager"
      v-model:selected-addr-id="selectedAddrId"
      :address-list="addressList"
      :set-default-address="setDefaultAddress"
      @open-add-form="showAddAddrForm=true"
    />
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
    <FavoritesPopup
      v-model:show="showFavorites"
      :favorite-list="favoriteList"
      :open-product-detail="openProductDetail"
    />
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
    <van-popup
      v-model:show="showVipModal"
      class="sheet-popup mobile-shell-popup"
      position="bottom"
      :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }"
    >
      <div class="popup-mobile-shell vip-shell">
        <van-nav-bar title="会员升级中心" left-arrow @click-left="showVipModal = false" />
        <div class="popup-mobile-content vip-content">
          <div class="vip-summary-card glass-panel">
            <div class="vip-summary-icon">👑</div>
            <div class="vip-summary-title">会员升级中心</div>
            <div class="vip-summary-copy">当前等级：{{ vipLevelName }}</div>
          </div>
          <div class="vip-card gold" @click="selectVip(2)" :class="{disabled: currentUser.level >= 2}">
            <div class="v-left">
              <van-icon name="award" size="30" />
              <div>
                <b>黄金VIP</b>
                <div class="v-desc">全场9折 + 专属券</div>
              </div>
            </div>
            <div class="v-price">¥ 99</div>
          </div>
          <div class="vip-card diamond" @click="selectVip(3)" :class="{disabled: currentUser.level >= 3}">
            <div class="v-left">
              <van-icon name="gem" size="30" />
              <div>
                <b>钻石VIP</b>
                <div class="v-desc">全场8折 + 顶级券</div>
              </div>
            </div>
            <div class="v-price">¥ 199</div>
          </div>
        </div>
      </div>
    </van-popup>

    <van-dialog v-model:show="showVipPayDialog" title="升级支付" :show-confirm-button="false">
      <div style="padding:20px; text-align:center;">
        <p style="font-size:16px; margin-bottom:10px;">升级为 <b style="color:#ee0a24">{{ pendingVipLevel === 2 ? '黄金VIP' : '钻石VIP' }}</b></p>
        <p style="font-size:24px; font-weight:bold; margin-bottom:20px;">¥ {{ pendingVipLevel === 2 ? '99.00' : '199.00' }}</p>
        <img :src="vipPayQrSrc" alt="VIP 升级支付二维码" style="width:150px; height:150px; margin:10px 0; image-rendering: pixelated;" />
        <van-button type="success" block round @click="confirmVipPay" style="margin-top:20px;">✅ 我已扫码支付</van-button>
      </div>
    </van-dialog>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch, nextTick } from 'vue'
import { showToast, showDialog, showSuccessToast, showLoadingToast, closeToast } from 'vant'
import ActivityHallTab from './components/ActivityHallTab.vue'
import AddressManagerPopup from './components/AddressManagerPopup.vue'
import AllOrdersPopup from './components/AllOrdersPopup.vue'
import CartTab from './components/CartTab.vue'
import FavoritesPopup from './components/FavoritesPopup.vue'
import HomeTab from './components/HomeTab.vue'
import OrderDetailView from './components/OrderDetailView.vue'
import ProfileTab from './components/ProfileTab.vue'
import ProductDetailPopup from './components/ProductDetailPopup.vue'
import { DEFAULT_CURRENT_MENU, DEFAULT_HERO_TEXT, DEFAULT_MORE_MENU_POOL, DEFAULT_SYSTEM_CONFIG, HERO_TEXT_MAX } from './constants/appData'
import { useAccountCenter } from './composables/useAccountCenter'
import { useAddressBook } from './composables/useAddressBook'
import { useCatalogCenter } from './composables/useCatalogCenter'
import { useEngagementCenter } from './composables/useEngagementCenter'
import { useGroupPurchase } from './composables/useGroupPurchase'
import { useOrderCenter } from './composables/useOrderCenter'
import { fetchCartList, addCartItem, updateCartItem } from './services/cart'
import { createPaymentQrDataUrl } from './utils/paymentQr'

const activeTab = ref(0); const goodsList = ref([]); const currentUser = ref(null)
const loginTab = ref(0); const loginForm = reactive({username:'', password:''}); const regForm = reactive({username:'', password:''})
const myOrderList = ref([]); const cartList = ref([])
const showBuyDialog = ref(false); const showCartConfirm = ref(false); const selectedItem = ref(null); const showPaySuccess = ref(false)
const isPaySubmitting = ref(false)
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
const singleQrNonce = ref(Date.now())
const cartQrNonce = ref(Date.now() + 1)
const rechargeQrNonce = ref(Date.now() + 2)
const vipQrNonce = ref(Date.now() + 3)

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

const pageTitle = computed(() => ['', '购物车', '我的', '拼团大厅', '秒杀大厅'][activeTab.value])
const isVip = computed(() => currentUser.value && currentUser.value.level > 1)
const vipLevelName = computed(() => currentUser.value?.level==1?'普通':(currentUser.value?.level==2?'🏆 黄金VIP':'💎 钻石VIP'))
const topNavTheme = computed(() => {
  const useWarmVipTone = isVip.value && (activeTab.value === 0 || activeTab.value === 1)
  if (useWarmVipTone) {
    return {
      background: 'rgba(244, 232, 217, 0.96)',
      titleColor: '#5b3d2f',
      iconColor: '#9a6b4f',
    }
  }
  if (isVip.value) {
    return {
      background: '#2f2a27',
      titleColor: '#f7e6b6',
      iconColor: '#f7e6b6',
    }
  }
  return {
    background: 'rgba(255, 250, 244, 0.94)',
    titleColor: '#2c1b16',
    iconColor: '#7f5d50',
  }
})
const selectedAddress = computed(() => addressList.value.find(a => a.id === selectedAddrId.value))
const cartCount = computed(() => cartList.value.length)
const isAllChecked = computed({ get: () => cartList.value.length>0 && cartList.value.every(item => item.checked), set: (val) => toggleAllCheck(val) })
const checkedCartItems = computed(() => cartList.value.filter(item => item.checked))
const checkedCartHasSeckill = computed(() => checkedCartItems.value.some(item => item.is_seckill))
const cartTotalPrice = computed(() => {
  let t = 0
  let d = isVip.value ? (currentUser.value.level == 2 ? 0.9 : 0.8) : 1
  checkedCartItems.value.forEach(i => {
    const unitPrice = i.is_seckill ? Number(i.display_price ?? i.price) || 0 : (Number(i.price) || 0) * d
    t += unitPrice * (Number(i.num) || 0)
  })
  return t
})
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
const checkoutCouponBasePrice = computed(() => {
  if (showCartConfirm.value) return Number(cartBasePrice.value) || 0
  return Number(singleBasePrice.value) || 0
})
const singlePayQrSrc = computed(() => createPaymentQrDataUrl([
  'scene=single',
  `user=${currentUser.value?.id ?? 'guest'}`,
  `product=${selectedItem.value?.id ?? 'none'}`,
  `amount=${calculateFinalPrice.value}`,
  `coupon=${selectedCoupon.value?.id ?? 'none'}`,
  `points=${usePoints.value ? 1 : 0}`,
  `nonce=${singleQrNonce.value}`,
].join('&'), 175))
const cartPayQrSrc = computed(() => createPaymentQrDataUrl([
  'scene=cart',
  `user=${currentUser.value?.id ?? 'guest'}`,
  `items=${checkedCartItems.value.map(item => `${item.id}x${item.num}`).join(',') || 'none'}`,
  `amount=${calculateCartFinalPrice.value}`,
  `coupon=${selectedCoupon.value?.id ?? 'none'}`,
  `points=${usePoints.value ? 1 : 0}`,
  `nonce=${cartQrNonce.value}`,
].join('&'), 175))
const rechargePayQrSrc = computed(() => createPaymentQrDataUrl([
  'scene=recharge',
  `user=${currentUser.value?.id ?? 'guest'}`,
  `amount=${rechargeAmount.value || 0}`,
  `nonce=${rechargeQrNonce.value}`,
].join('&'), 175))
const vipPayQrSrc = computed(() => createPaymentQrDataUrl([
  'scene=vip-upgrade',
  `user=${currentUser.value?.id ?? 'guest'}`,
  `level=${pendingVipLevel.value || 0}`,
  `nonce=${vipQrNonce.value}`,
].join('&'), 150))
const { loadAddress, saveAddress, setDefaultAddress } = useAddressBook({
  addressList,
  selectedAddrId,
  newAddr,
  showAddAddrForm,
  showSuccessToast,
  showToast,
})
const {
  openCouponCenter,
  handleGetCoupon,
  openMyCoupons,
  openCheckoutCouponSelector,
  viewMyWalletCoupons,
  toggleFavorite,
  loadFavorites,
} = useEngagementCenter({
  currentUser,
  showCoupon,
  showMyCouponSelector,
  showOwnedCouponsPopup,
  showFavorites,
  coupons,
  myUsableCoupons,
  favoriteList,
  favIds,
  showToast,
  showSuccessToast,
})
const {
  cancelGroupChoice,
  openJoinGroupDialog,
  buyGroupItemDirectly,
  startNewGroup,
  joinGroup,
} = useGroupPurchase({
  pendingGroupAction,
  inputGroupCode,
  isGroupBuyMode,
  showGroupChoiceDialog,
  showJoinGroupInput,
  showBuyDialog,
  showToast,
})
const loadData = () => { loadMyOrders(); loadAddress(); loadCart(); loadFavorites(); openMyCoupons(); }
const {
  openOrderList,
  handleCartCheckout,
  confirmSingleOrder,
  confirmCartOrder,
  finishPayment,
  loadMyOrders,
  confirmOrderReceipt,
  cancelOrder,
  viewOrderDetail,
  openComment,
  submitComment,
} = useOrderCenter({
  activeTab,
  currentUser,
  selectedItem,
  selectedAddrId,
  selectedCoupon,
  usePoints,
  checkedCartItems,
  isSeckillExpired,
  calculateFinalPrice,
  calculateCartFinalPrice,
  lastPaidAmount,
  lastOrderGroupCode,
  myOrderList,
  currentOrderDetail,
  logisticsTraces,
  commentForm,
  showBuyDialog,
  showCartConfirm,
  isPaySubmitting,
  showAllOrders,
  showPaySuccess,
  showOrderDetail,
  showCommentDialog,
  pendingGroupAction,
  inputGroupCode,
  isGroupBuyMode,
  addressList,
  loadAddress,
  loadData,
  showToast,
  showDialog,
  showSuccessToast,
  showLoadingToast,
  closeToast,
})
const {
  openRecharge,
  submitRecharge,
  onLogin,
  onRegister,
  logout,
  openEditName,
  submitEditName,
  openChangePasswordDialog,
  submitChangePassword,
  openEditHeroText,
  submitEditHeroText,
  handleAvatarChange,
  upgradeVip,
  openVipCenter,
  selectVip,
  confirmVipPay,
} = useAccountCenter({
  activeTab,
  currentUser,
  heroText,
  loginTab,
  loginForm,
  regForm,
  editingName,
  showEditNameDialog,
  changePasswordForm,
  showChangePasswordDialog,
  editingHeroText,
  showEditHeroDialog,
  rechargeAmount,
  showRecharge,
  showVipModal,
  pendingVipLevel,
  showVipPayDialog,
  cartList,
  myOrderList,
  favoriteList,
  myUsableCoupons,
  coupons,
  favIds,
  DEFAULT_HERO_TEXT,
  HERO_TEXT_MAX,
  showToast,
  showDialog,
  showSuccessToast,
  showLoadingToast,
  closeToast,
  loadData,
})
const {
  getSeckillStatusText,
  getSeckillStatusTag,
  getSeckillProgress,
  getCountdownMs,
  refreshSelectedSeckillState,
  filteredGoodsList,
  loadProducts,
  handleGridClick,
  handleSignin,
  openProductDetail,
  handleBuyNow,
  triggerBuyLogic,
  handleSeckillFinish,
  stopSeckillTimer,
} = useCatalogCenter({
  activeTab,
  goodsList,
  currentUser,
  selectedItem,
  addressList,
  currentCategory,
  searchKeyword,
  bannerList,
  systemConfig,
  isGroupBuyMode,
  showBuyDialog,
  showFavorites,
  showProductDetail,
  showGroupChoiceDialog,
  productComments,
  selectedCoupon,
  usePoints,
  seckillTimer,
  seckillTimeLeft,
  isSeckillExpired,
  showSigninPopup,
  selectedItemIsGroup,
  currentSeckillStatus,
  canBuySeckillNow,
  loadAddress,
  loadFavorites,
  openMyCoupons,
  openCouponCenter,
  openRecharge,
  showMoreMenu,
  showDialog,
  showToast,
  showLoadingToast,
  closeToast,
})

const canUseCouponForCurrentCheckout = (coupon) => {
  if (!coupon) return true
  return checkoutCouponBasePrice.value >= (Number(coupon.min_spend) || 0)
}

const selectCheckoutCoupon = (coupon) => {
  if (!coupon) {
    selectedCoupon.value = null
    showMyCouponSelector.value = false
    return
  }
  if (!canUseCouponForCurrentCheckout(coupon)) {
    showToast(`未满 ${coupon.min_spend} 元`)
    return
  }
  selectedCoupon.value = coupon
  showMyCouponSelector.value = false
}

const calcFinal = (basePrice) => {
  let price = Number(basePrice) || 0
  if (selectedCoupon.value && price >= (Number(selectedCoupon.value.min_spend) || 0)) {
    price -= Number(selectedCoupon.value.amount) || 0
  }
  if (price < 0) price = 0
  if (usePoints.value && currentUser.value && currentUser.value.points > 0) {
    let maxDeduct = price; let available = currentUser.value.points; let needed = Math.floor(maxDeduct * 100); let actual = Math.min(available, needed)
    price -= actual / 100
  }
  if (price < 0) price = 0
  return price.toFixed(2)
}

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

onMounted(loadProducts)
watch(showProductDetail, (visible) => {
  if (!visible && seckillTimer.value) {
    clearInterval(seckillTimer.value)
    seckillTimer.value = null
  }
})
watch(showBuyDialog, (visible) => {
  if (visible) singleQrNonce.value = Date.now()
})
watch(showCartConfirm, (visible) => {
  if (visible) cartQrNonce.value = Date.now()
})
watch(showRecharge, (visible) => {
  if (visible) rechargeQrNonce.value = Date.now()
})
watch(showVipPayDialog, (visible) => {
  if (visible) vipQrNonce.value = Date.now()
})
watch(rechargeAmount, () => {
  if (showRecharge.value) rechargeQrNonce.value = Date.now()
})
watch(pendingVipLevel, () => {
  if (showVipPayDialog.value) vipQrNonce.value = Date.now()
})

const onClickLeft = () => { activeTab.value = 0 }

// 🔥 修改：秒杀点击逻辑，进入大厅 🔥
const replaceMenuItem = (newItem) => { const moreIndex = currentMenu.value.findIndex(i => i.act === 'more'); const targetIndex = moreIndex > 0 ? moreIndex - 1 : 0; const oldItem = currentMenu.value[targetIndex]; currentMenu.value[targetIndex] = newItem; moreMenuPool.value.push(oldItem); const poolIndex = moreMenuPool.value.indexOf(newItem); if (poolIndex > -1) moreMenuPool.value.splice(poolIndex, 1); showMoreMenu.value = false; showToast(`已切换为 ${newItem.text}`) }
const openAddressManagerPanel = () => { showAddressManager.value = true }
const openFavoritesPanel = () => { showFavorites.value = true; loadFavorites() }
const openPhoneServicePopup = () => { showPhonePopup.value = true }
const openQQServicePopup = () => { showQQPopup.value = true }
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
const loadCart = async () => { if(!currentUser.value) return; const res = await fetchCartList(); if(res.data.code===200) cartList.value = res.data.data.map(i => ({...i, checked: true})) }
const handleAddToCart = async (item) => {
    if(!currentUser.value) return showToast('请登录');
    const res = await addCartItem(item.id);
    if(res.data.code===200) { showSuccessToast('已加购'); loadCart() } else { showToast(res.data.msg || '加入购物车失败') }
}
const updateCartNum = async (item, num) => { if (num === undefined) num = item.num; await updateCartItem(item.id, num); loadCart() }
const toggleAllCheck = (val) => { cartList.value.forEach(item => item.checked = val) }

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
.user-header-card.is-vip {
  background:
    radial-gradient(circle at top right, rgba(255, 196, 143, 0.36), transparent 24%),
    linear-gradient(135deg, #f3deca, #ead3bb 55%, #e4c8ae);
  color: var(--mall-text);
}
.user-header-card.is-vip .avatar {
  border-color: rgba(127, 93, 80, 0.22);
}
.user-header-card.is-vip .level-badge {
  background: rgba(127, 93, 80, 0.1);
  color: #8c633f;
}
.user-header-card.is-vip .member-hero-meta {
  border-top-color: rgba(127, 93, 80, 0.16);
}
.user-header-card.is-vip .hero-desc-edit-btn {
  color: rgba(127, 93, 80, 0.75);
}
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
.section-kicker {
  font-size: 13px;
  letter-spacing: 0.02em;
  color: #8b6c5d;
  font-weight: 600;
  text-transform: none;
}
.section-title {
  margin-top: 6px;
  font-size: 20px;
  line-height: 1.25;
  font-weight: 700;
  color: var(--mall-text);
}
.section-sub {
  margin-top: 6px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--mall-text-soft);
}
.section-side {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,0.7);
  color: var(--mall-text-soft);
  font-size: 13px;
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
  width: 175px;
  height: 175px;
  margin: 12px auto 14px;
  display: block;
  image-rendering: pixelated;
  border-radius: 18px;
  background: #fff;
  padding: 8px;
  box-shadow: var(--mall-shadow-card);
}
.pay-confirm-btn {
  margin-top: 2px;
}
.address-shell :deep(.van-nav-bar) {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(14px);
}
.vip-shell :deep(.van-nav-bar) {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(14px);
}
.address-content {
  padding: 14px;
}
.vip-content {
  padding: 14px;
}
.vip-summary-card {
  padding: 18px 16px;
  text-align: center;
  margin-bottom: 14px;
}
.vip-summary-icon {
  font-size: 24px;
  line-height: 1;
}
.vip-summary-title {
  margin-top: 8px;
  font-size: 22px;
  font-weight: 800;
  color: var(--mall-text);
}
.vip-summary-copy {
  margin-top: 8px;
  font-size: 14px;
  color: var(--mall-text-soft);
}
.addr-box {
  background: #f9f4ef;
  padding: 16px 14px;
  border-radius: 18px;
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
  border: 1px solid rgba(232,77,42,0.08);
  box-shadow: var(--mall-shadow-card);
}
.addr-content { flex: 1; min-width: 0; }
.addr-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 15px;
  color: var(--mall-text);
}
.addr-detail {
  color: var(--mall-text-soft);
  font-size: 13px;
  line-height: 1.6;
  display: block;
}
.addr-actions { margin-top: 12px; display: flex; justify-content: flex-end; }
.fav-item { display: flex; background: #ffffff; padding: 14px 16px; border-radius: 18px; margin-bottom: 12px; box-shadow: var(--mall-shadow-card); align-items: center; gap: 14px; }
.fav-item img { width: 72px; height: 72px; border-radius: 16px; object-fit: cover; flex-shrink: 0; }
.favorites-shell :deep(.van-nav-bar) {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(14px);
}
.favorites-content {
  padding: 14px;
}
.coupon-shell :deep(.van-nav-bar) {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(14px);
}
.coupon-content {
  padding: 14px;
}
.coupon-selector-shell :deep(.van-nav-bar) {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(14px);
}
.coupon-selector-content {
  padding: 14px;
}
.coupon-selector-group {
  overflow: hidden;
  border-radius: 22px;
  box-shadow: var(--mall-shadow-card);
}
.coupon-selector-cell {
  min-height: 64px;
}
.coupon-selector-cell :deep(.van-cell__title) {
  font-size: 16px;
  font-weight: 600;
  color: var(--mall-text);
}
.coupon-selector-cell :deep(.van-cell__value) {
  font-size: 16px;
  font-weight: 700;
  color: var(--mall-primary);
}
.coupon-selector-cell-disabled {
  opacity: 0.55;
}
.coupon-selector-cell-disabled :deep(.van-cell__title),
.coupon-selector-cell-disabled :deep(.van-cell__value) {
  color: #b4a39a;
}
.coupon-selector-cell-muted :deep(.van-cell__title) {
  color: var(--mall-text-soft);
  font-weight: 500;
}
.coupon-empty-state {
  text-align: center;
  color: var(--mall-text-soft);
  padding: 60px 0 40px;
}
.coupon-empty-state p {
  margin-top: 10px;
  font-size: 14px;
}
.f-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--mall-text);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.f-price {
  margin-top: 6px;
  font-size: 18px;
  font-weight: 800;
  color: var(--mall-primary);
}
.fav-item :deep(.van-icon-arrow) {
  font-size: 20px;
}
.f-title { font-weight: bold; font-size: 14px; margin-bottom: 5px; }
.f-price { color: var(--mall-primary); font-weight: 800; }
.coupon-card { display: flex; min-height: 98px; background: #ffffff; border-radius: 20px; margin-bottom: 12px; box-shadow: var(--mall-shadow-card); overflow: hidden; position: relative; }
.c-left { width: 110px; background: linear-gradient(135deg, #ff6034, var(--mall-primary)); color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; border-right: 2px dashed #f7f8fa; padding: 10px 8px; box-sizing: border-box; }
.c-left.got { background: #c8c9cc; }
.c-price { font-size: 32px; font-weight: bold; line-height: 1; font-family: sans-serif; }
.c-price span { font-size: 14px; margin-right: 2px; font-weight: normal; }
.c-cond { font-size: 11px; margin-top: 6px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px; }
.circle-top, .circle-bottom { position: absolute; width: 12px; height: 12px; background: #f7f8fa; border-radius: 50%; right: -6px; z-index: 2; }
.circle-top { top: -6px; }
.circle-bottom { bottom: -6px; }
.c-right { flex: 1; padding: 0 16px 0 18px; display: flex; justify-content: space-between; align-items: center; gap: 12px; }
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
.product-detail-shell {
  position: relative;
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
.vip-card { display:flex; justify-content:space-between; align-items:center; color:white; padding:22px 18px; border-radius:22px; margin-bottom:14px; box-shadow:0 12px 28px rgba(0,0,0,0.14); cursor:pointer; transition:transform 0.1s; min-height: 104px; }
.vip-card:active { transform:scale(0.98); }
.vip-card.disabled { opacity:0.6; filter:grayscale(1); cursor:not-allowed; }
.vip-card.gold { background:linear-gradient(135deg, #ffd979, #d59b23); }
.vip-card.diamond { background:linear-gradient(135deg, #46a5ff, #05d2ff); }
.v-left { display:flex; align-items:center; gap:15px; font-size:18px; flex: 1; min-width: 0; }
.v-left b { display: block; font-size: 22px; line-height: 1.2; }
.v-desc { font-size:14px; opacity:0.92; font-weight:normal; margin-top:6px; line-height: 1.4; }
.v-price { font-size:34px; font-weight:800; line-height: 1; margin-left: 12px; flex-shrink: 0; }
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
.mall-nav-bar :deep(.van-nav-bar--fixed) {
  width: min(100%, 600px);
  left: 50%;
  right: auto;
  transform: translateX(-50%);
}
.mall-nav-bar :deep(.van-nav-bar::after) {
  display: none;
}
.mall-nav-bar :deep(.van-nav-bar__placeholder) {
  height: 54px !important;
}
.mall-nav-bar :deep(.van-nav-bar__content) {
  position: relative;
  z-index: 5001;
  background: var(--van-nav-bar-background);
  backdrop-filter: blur(14px);
  height: 46px;
}
.mall-nav-bar :deep(.van-nav-bar__title),
.mall-nav-bar :deep(.van-icon),
.mall-nav-bar :deep(.van-nav-bar__text) {
  position: relative;
  z-index: 5002;
}
.mall-tabbar {
  position: fixed !important;
  left: 50% !important;
  right: auto !important;
  bottom: 10px !important;
  width: min(calc(100vw - 24px), 576px) !important;
  max-width: 576px !important;
  transform: translateX(-50%) !important;
  border-radius: 22px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(255,255,255,0.78);
  box-shadow: 0 18px 36px rgba(85, 45, 27, 0.14);
  backdrop-filter: blur(18px);
  box-sizing: border-box;
}
.mall-tabbar :deep(.van-tabbar-item) {
  background: transparent;
}
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
