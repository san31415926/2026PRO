import { computed } from 'vue'
import { signinMobile } from '../services/auth'
import { fetchBanners, fetchProductComments, fetchProducts, fetchSystemConfig } from '../services/catalog'

export function useCatalogCenter(options) {
  const {
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
  } = options

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
    const startAt = selectedItem.value.seckill_start_at
      ? new Date(String(selectedItem.value.seckill_start_at).replace(' ', 'T')).getTime()
      : null
    const endAt = selectedItem.value.seckill_end_at
      ? new Date(String(selectedItem.value.seckill_end_at).replace(' ', 'T')).getTime()
      : null

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

    selectedItem.value.seckill_status = selectedItem.value.display_stock <= 0 ? 'sold_out' : 'ended'
    seckillTimeLeft.value = 0
    isSeckillExpired.value = true
  }

  const filteredGoodsList = computed(() => {
    let list = goodsList.value
    if (searchKeyword.value) list = list.filter((item) => item.title.includes(searchKeyword.value))
    if (activeTab.value === 3) return list.filter((item) => item.category.includes('拼团'))
    if (activeTab.value === 4) return list.filter((item) => item.category.includes('秒杀'))
    if (currentCategory.value === '🔥 爆款推荐') return list
    return list.filter((item) => item.category.includes(currentCategory.value))
  })

  const loadProducts = async (isManualRefresh = false) => {
    if (isManualRefresh) showLoadingToast({ message: '刷新中', forbidClick: true, duration: 0 })
    try {
      const res = await fetchProducts()
      if (res.data.code === 200) goodsList.value = res.data.data.filter((item) => item.is_on_sale)

      const bannerRes = await fetchBanners()
      if (bannerRes.data.code === 200) bannerList.value = bannerRes.data.data

      const configRes = await fetchSystemConfig()
      if (configRes.data.code === 200) {
        systemConfig.value.group_buy_people = parseInt(configRes.data.data.group_buy_people)
        systemConfig.value.seckill_time_limit = parseInt(configRes.data.data.seckill_time_limit)
        systemConfig.value.group_buy_discount = parseFloat(configRes.data.data.group_buy_discount)
      }

      if (currentUser.value) {
        loadFavorites()
        openMyCoupons()
      }
    } catch (error) {
      console.error(error)
    } finally {
      if (isManualRefresh) closeToast()
    }
  }

  const handleGridClick = (item) => {
    if (item.type === 'filter') {
      if (item.text === '拼团') {
        activeTab.value = 3
        return
      }
      if (item.text === '秒杀') {
        activeTab.value = 4
        return
      }
      currentCategory.value = item.text
      searchKeyword.value = ''
      showToast(`进入 ${item.text}`)
      return
    }

    if (item.type === 'action') {
      if (item.act === 'coupon') openCouponCenter()
      if (item.act === 'recharge') openRecharge()
      if (item.act === 'signin') handleSignin()
      if (item.act === 'more') showMoreMenu.value = true
    }
  }

  const handleSignin = async () => {
    if (!currentUser.value) return showToast('请登录')
    const res = await signinMobile()
    if (res.data.code === 200) {
      currentUser.value.points = res.data.points
      showSigninPopup.value = true
    }
  }

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
    } catch (error) {
      console.error(error)
    }
  }

  const handleBuyNow = (item) => openProductDetail(item)

  const triggerBuyLogic = () => {
    if (!currentUser.value) {
      showToast('请登录')
      showProductDetail.value = false
      activeTab.value = 2
      return
    }

    const item = selectedItem.value
    selectedCoupon.value = null
    usePoints.value = false

    if (item.is_seckill) {
      if (item.seckill_status === 'upcoming') return showDialog({ message: '秒杀尚未开始，请等待活动开抢。' })
      if (item.seckill_status === 'sold_out') return showDialog({ message: '当前秒杀商品已售罄，请查看其他商品。' })
      if (item.seckill_status === 'ended') return showDialog({ message: '当前秒杀活动已结束。' })
      isGroupBuyMode.value = false
      showProductDetail.value = false
      showBuyDialog.value = true
      if (addressList.value.length === 0) loadAddress()
      return
    }

    if (selectedItemIsGroup.value) {
      isGroupBuyMode.value = true
      showProductDetail.value = false
      showGroupChoiceDialog.value = true
      if (addressList.value.length === 0) loadAddress()
      return
    }

    isGroupBuyMode.value = false
    showProductDetail.value = false
    showBuyDialog.value = true
    if (addressList.value.length === 0) loadAddress()
  }

  const handleSeckillFinish = () => {
    refreshSelectedSeckillState()
  }

  const stopSeckillTimer = () => {
    if (!seckillTimer.value) return
    clearInterval(seckillTimer.value)
    seckillTimer.value = null
  }

  return {
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
  }
}
