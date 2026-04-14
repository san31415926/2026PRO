export const HERO_TEXT_MAX = 20
export const DEFAULT_HERO_TEXT = '鸟为什么会飞'
export const DEFAULT_SYSTEM_CONFIG = {
  group_buy_people: 2,
  seckill_time_limit: 5,
  group_buy_discount: 0.8,
}

export const DEFAULT_CURRENT_MENU = [
  { text: '热卖', icon: 'fire-o', type: 'filter', key: '热卖' },
  { text: '手机', icon: 'shopping-cart-o', type: 'filter', key: '手机' },
  { text: '电脑', icon: 'desktop-o', type: 'filter', key: '电脑' },
  { text: '数码', icon: 'tv-o', type: 'filter', key: '数码' },
  { text: '拼团', icon: 'friends-o', type: 'filter', key: '拼团' },
  { text: '秒杀', icon: 'clock-o', type: 'filter', key: '秒杀' },
  { text: '领券', icon: 'coupon-o', type: 'action', act: 'coupon' },
  { text: '更多', icon: 'apps-o', type: 'action', act: 'more' },
]

export const DEFAULT_MORE_MENU_POOL = [
  { text: '充值', icon: 'gold-coin-o', type: 'action', act: 'recharge' },
  { text: '签到', icon: 'gift-o', type: 'action', act: 'signin' },
  { text: '平板', icon: 'points', type: 'filter', key: '平板' },
  { text: '相机', icon: 'photograph', type: 'filter', key: '相机' },
  { text: '耳机', icon: 'service-o', type: 'filter', key: '耳机' },
  { text: '手表', icon: 'clock', type: 'filter', key: '手表' },
]
