<template>
  <van-popup
    :show="show"
    class="sheet-popup mobile-shell-popup"
    position="bottom"
    :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }"
    closeable
    @update:show="updateShow"
  >
    <div v-if="selectedItem" class="popup-mobile-shell product-detail-shell">
      <div style="height:350px; position:relative;">
        <img :src="selectedItem.img" style="width:100%; height:100%; object-fit:cover;">
        <div v-if="isSeckillItem" class="seckill-bar-modal">
          <div class="sk-info">
            <div class="sk-title">⚡ 疯狂秒杀</div>
            <div class="sk-sub">{{ getSeckillStatusTag(selectedItem) }} · 每人限购 {{ selectedItem.seckill_limit_per_user || 1 }} 件</div>
          </div>
          <div class="sk-countdown">
            <div style="font-size:10px; margin-bottom:2px; opacity:0.8;">{{ currentSeckillStatus === 'upcoming' ? '距开始仅剩' : '距结束仅剩' }}</div>
            <van-count-down
              :time="seckillTimeLeft"
              format="DD 天 HH : mm : ss"
              style="color:#fff000; font-weight:bold; font-size:20px; font-family:monospace;"
              @finish="handleSeckillFinish"
            />
          </div>
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
          <div v-for="comment in productComments" :key="comment.id" style="border-bottom:1px solid #f5f5f5;padding:12px 0;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <img :src="comment.avatar" style="width:32px;height:32px;border-radius:50%;object-fit:cover;" />
              <span style="font-size:13px;font-weight:500;">{{ comment.user }}</span>
              <van-rate :model-value="comment.rating" readonly :size="12" color="#ffd21e" void-color="#eee" style="margin-left:auto;" />
            </div>
            <p style="font-size:13px;color:#555;margin:0;line-height:1.6;">{{ comment.content }}</p>
            <p style="font-size:11px;color:#bbb;margin:4px 0 0;">{{ comment.date }}</p>
          </div>
        </div>
      </div>

      <div class="product-detail-footer" style="padding:10px 20px; background:white; display:flex; gap:15px; border-top:1px solid #eee;">
        <van-button v-if="!isSeckillItem" block round color="#ff976a" :disabled="selectedItem.stock === 0" @click="handleAddToCart(selectedItem)">加入购物车</van-button>
        <div class="btn-icon fav" style="width:44px;height:44px;border:1px solid #eee;margin-right:-5px;" @click.stop="toggleFavorite(selectedItem)">
          <van-icon :name="isFav(selectedItem.id) ? 'like' : 'like-o'" :color="isFav(selectedItem.id) ? '#ee0a24' : '#666'" size="20" />
        </div>
        <template v-if="selectedItemIsGroup && !isSeckillItem">
          <van-button block round plain color="#ee0a24" :disabled="selectedItem.stock === 0" @click="buyGroupItemDirectly">
            {{ selectedItem.stock === 0 ? '已售罄' : '直接购买' }}
          </van-button>
          <van-button block round color="linear-gradient(135deg, #ff8652, #e84d2a)" :disabled="selectedItem.stock === 0" @click="triggerBuyLogic">
            {{ selectedItem.stock === 0 ? '已售罄' : '去开团/参团' }}
          </van-button>
        </template>
        <van-button
          v-else
          block
          round
          :color="(isSeckillItem && !canBuySeckillNow) || selectedItem.display_stock === 0 || selectedItem.stock === 0 ? '#ccc' : (isSeckillItem ? 'linear-gradient(to right, #ff6034, #ee0a24)' : '#ee0a24')"
          :disabled="(isSeckillItem && !canBuySeckillNow) || (isSeckillItem ? selectedItem.display_stock === 0 : selectedItem.stock === 0)"
          @click="triggerBuyLogic"
        >
          {{ isSeckillItem ? getSeckillStatusText(selectedItem) : (selectedItem.stock === 0 ? '已售罄' : '立即购买') }}
        </van-button>
      </div>
    </div>
  </van-popup>
</template>

<script setup>
defineProps({
  show: Boolean,
  selectedItem: { type: Object, default: null },
  isSeckillItem: Boolean,
  selectedItemIsGroup: Boolean,
  currentSeckillStatus: { type: String, default: 'none' },
  canBuySeckillNow: Boolean,
  seckillTimeLeft: { type: Number, default: 0 },
  productComments: { type: Array, default: () => [] },
  getSeckillStatusTag: { type: Function, required: true },
  getSeckillStatusText: { type: Function, required: true },
  handleSeckillFinish: { type: Function, required: true },
  handleAddToCart: { type: Function, required: true },
  toggleFavorite: { type: Function, required: true },
  isFav: { type: Function, required: true },
  buyGroupItemDirectly: { type: Function, required: true },
  triggerBuyLogic: { type: Function, required: true },
})

const emit = defineEmits(['update:show'])
const updateShow = value => emit('update:show', value)
</script>
