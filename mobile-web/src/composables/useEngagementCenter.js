import { fetchCouponMarket, fetchMyCoupons, claimCoupon } from '../services/coupon'
import { toggleFavoriteItem, fetchFavorites } from '../services/favorite'

export function useEngagementCenter(options) {
  const {
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
  } = options

  const openMyCoupons = async () => {
    if (!currentUser.value) return
    const res = await fetchMyCoupons()
    if (res.data.code === 200) {
      myUsableCoupons.value = res.data.data
    }
  }

  const openCouponCenter = async () => {
    showCoupon.value = true
    const res = await fetchCouponMarket()
    if (res.data.code === 200) {
      coupons.value = res.data.data.map((coupon) => ({ ...coupon, got: false }))
      if (currentUser.value) {
        const myRes = await fetchMyCoupons()
        if (myRes.data.code === 200) {
          const myCouponNames = myRes.data.data.map((coupon) => coupon.name)
          coupons.value.forEach((coupon) => {
            if (myCouponNames.includes(coupon.name)) coupon.got = true
          })
        }
      }
    }
  }

  const handleGetCoupon = async (coupon) => {
    if (!currentUser.value) return showToast('请登录')
    try {
      const res = await claimCoupon(coupon.id)
      if (res.data.code === 200) {
        showSuccessToast('领取成功')
        coupon.got = true
        openMyCoupons()
      } else {
        if (res.data.msg.includes('已领取')) coupon.got = true
        showToast(res.data.msg)
      }
    } catch (error) {
      showToast('网络错误')
    }
  }

  const openCheckoutCouponSelector = async () => {
    if (!currentUser.value) return showToast('请登录')
    await openMyCoupons()
    showMyCouponSelector.value = true
  }

  const viewMyWalletCoupons = async () => {
    if (!currentUser.value) return showToast('请登录')
    await openMyCoupons()
    showOwnedCouponsPopup.value = true
  }

  const loadFavorites = async () => {
    const res = await fetchFavorites()
    if (res.data.code === 200) {
      favoriteList.value = res.data.data
      favIds.value = res.data.data.map((item) => item.id)
    }
  }

  const toggleFavorite = async (item) => {
    if (!currentUser.value) return showToast('请登录')
    const res = await toggleFavoriteItem(item.id)
    if (res.data.code === 200) {
      if (res.data.action === 'add') {
        showSuccessToast('收藏成功，宝贝已经躺在我的收藏里面啦')
        favIds.value.push(item.id)
      } else {
        showToast('已取消收藏')
        const index = favIds.value.indexOf(item.id)
        if (index > -1) favIds.value.splice(index, 1)
      }
      if (showFavorites.value) loadFavorites()
    }
  }

  return {
    openCouponCenter,
    handleGetCoupon,
    openMyCoupons,
    openCheckoutCouponSelector,
    viewMyWalletCoupons,
    toggleFavorite,
    loadFavorites,
  }
}
