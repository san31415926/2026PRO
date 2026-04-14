import { createOrder, fetchMyOrders, confirmReceipt, cancelOrderById, fetchOrderDetail, fetchOrderLogistics } from '../services/order'
import { checkoutCart } from '../services/cart'
import { submitCommentByOrder } from '../services/comment'
import { fetchSessionUser } from '../services/auth'

export function useOrderCenter(options) {
  const {
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
  } = options

  const openOrderList = () => {
    showAllOrders.value = true
  }

  const handleCartCheckout = () => {
    if (checkedCartItems.value.length === 0) return showToast('请选择商品')
    const hasSeckillItem = checkedCartItems.value.some(
      (item) => item.is_seckill || (item.category && item.category.includes('秒杀'))
    )
    if (hasSeckillItem && isSeckillExpired.value) {
      return showDialog({ message: '购物车里包含已失效的秒杀商品，请移除后再结算。' })
    }
    usePoints.value = false
    selectedCoupon.value = null
    showCartConfirm.value = true
    if (addressList.value.length === 0) loadAddress()
  }

  const ensureSessionMatchesCurrentUser = async () => {
    try {
      const sessionRes = await fetchSessionUser()
      if (sessionRes.data.code !== 200 || !currentUser.value) return false
      const sessionId = String(sessionRes.data.data.id)
      const currentId = String(currentUser.value.id)
      return sessionId === currentId
    } catch (error) {
      return false
    }
  }

  const processPay = async (submitRequest, data, amountToPay) => {
    if (isPaySubmitting.value) return
    if (!selectedAddrId.value) return showToast('请先选择地址')

    const sessionMatched = await ensureSessionMatchesCurrentUser()
    if (!sessionMatched) {
      return showDialog({
        title: '登录态已切换',
        message: '当前浏览器里的登录账号和页面显示账号不一致。请重新登录当前账号，或使用无痕窗口/其他浏览器测试第二个账号。',
      })
    }

    isPaySubmitting.value = true
    showLoadingToast({ message: '正在验证支付...', forbidClick: true, duration: 0 })
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))
      const res = await submitRequest(data)
      closeToast()
      if (res.data.code === 200) {
        currentUser.value.balance = res.data.balance
        currentUser.value.points = res.data.points
        lastPaidAmount.value = amountToPay
        lastOrderGroupCode.value = res.data.group_code || null
        showBuyDialog.value = false
        showCartConfirm.value = false
        showPaySuccess.value = true
        loadData()
        pendingGroupAction.value = null
        inputGroupCode.value = ''
      } else {
        showToast(res.data.msg)
      }
    } catch (error) {
      closeToast()
      showToast('网络请求失败')
    } finally {
      isPaySubmitting.value = false
    }
  }

  const confirmSingleOrder = async () => {
    await processPay(
      createOrder,
      {
        product_id: selectedItem.value.id,
        address_id: selectedAddrId.value,
        coupon_id: selectedCoupon.value?.id,
        use_points: usePoints.value,
        group_action: isGroupBuyMode.value ? pendingGroupAction.value : null,
        group_code: isGroupBuyMode.value ? inputGroupCode.value : null,
      },
      calculateFinalPrice.value,
    )
  }

  const confirmCartOrder = async () => {
    await processPay(
      checkoutCart,
      {
        cart_ids: checkedCartItems.value.map((item) => item.id),
        address_id: selectedAddrId.value,
        coupon_id: selectedCoupon.value?.id,
        use_points: usePoints.value,
      },
      calculateCartFinalPrice.value,
    )
  }

  const finishPayment = (target) => {
    showPaySuccess.value = false
    activeTab.value = target === 'order' ? 2 : 0
  }

  const loadMyOrders = async () => {
    if (!currentUser.value) return
    const res = await fetchMyOrders()
    if (res.data.code === 200) myOrderList.value = res.data.data
  }

  const confirmOrderReceipt = async (order) => {
    await confirmReceipt(order.id)
    showSuccessToast('确认收货完成')
    loadMyOrders()
  }

  const cancelOrder = async (order) => {
    showDialog({
      title: '取消订单',
      message: '确定取消这笔订单吗？金额会退回到账户余额。',
      showCancelButton: true,
    })
      .then(async () => {
        const res = await cancelOrderById(order.id)
        if (res.data.code === 200) {
          showSuccessToast('订单已取消，余额已退回')
          if (currentUser.value) currentUser.value.balance = res.data.balance
          showOrderDetail.value = false
          loadMyOrders()
        } else {
          showToast(res.data.msg)
        }
      })
      .catch(() => {})
  }

  const viewOrderDetail = async (id) => {
    showLoadingToast('加载中...')
    try {
      const res = await fetchOrderDetail(id)
      const logisticsRes = await fetchOrderLogistics(id)
      if (res.data.code === 200) {
        currentOrderDetail.value = res.data.data
        logisticsTraces.value = logisticsRes.data.data || []
        showOrderDetail.value = true
      }
    } finally {
      closeToast()
    }
  }

  const openComment = (order) => {
    commentForm.order_id = order.id
    commentForm.content = ''
    commentForm.rating = 5
    showCommentDialog.value = true
  }

  const submitComment = async () => {
    const res = await submitCommentByOrder(commentForm)
    if (res.data.code === 200) {
      showSuccessToast('评价成功')
      loadMyOrders()
      showCommentDialog.value = false
    }
  }

  return {
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
  }
}
