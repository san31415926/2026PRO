import { loginMobile, registerMobile } from '../services/auth'
import { rechargeBalance, updateProfile, updatePassword, uploadImage, upgradeVipLevel } from '../services/profile'

export function useAccountCenter(options) {
  const {
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
  } = options

  const openRecharge = () => {
    if (!currentUser.value) return showToast('请登录')
    rechargeAmount.value = ''
    showRecharge.value = true
  }

  const submitRecharge = async () => {
    if (!rechargeAmount.value) return showToast('请输入金额')
    showLoadingToast({ message: '正在验证支付...', forbidClick: true, duration: 0 })
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))
      const res = await rechargeBalance(rechargeAmount.value)
      closeToast()
      if (res.data.code === 200) {
        showSuccessToast('充值成功')
        if (currentUser.value) currentUser.value.balance = res.data.balance
        showRecharge.value = false
        rechargeAmount.value = ''
      } else {
        showToast(res.data.msg || '充值失败')
      }
    } catch (error) {
      closeToast()
      showToast('网络错误')
    }
  }

  const onLogin = async () => {
    try {
      const res = await loginMobile(loginForm)
      if (res.data.code === 200) {
        currentUser.value = res.data.data
        heroText.value = res.data.data.hero_text || DEFAULT_HERO_TEXT
        showSuccessToast('欢迎回来')
        loadData()
      } else {
        showToast(res.data.msg)
      }
    } catch (error) {
      showToast('登录失败')
    }
  }

  const onRegister = async () => {
    const res = await registerMobile(regForm)
    if (res.data.code === 200) {
      showSuccessToast(res.data.newcomer_coupon_received ? '注册成功，新人券已到账' : '注册成功')
      loginTab.value = 0
      loginForm.username = regForm.username
    } else {
      showToast(res.data.msg)
    }
  }

  const logout = () => {
    showDialog({
      title: '提示',
      message: '确定要切换账号吗？',
      showCancelButton: true,
    }).then(() => {
      currentUser.value = null
      heroText.value = DEFAULT_HERO_TEXT
      loginForm.username = ''
      loginForm.password = ''
      cartList.value = []
      myOrderList.value = []
      favoriteList.value = []
      myUsableCoupons.value = []
      coupons.value.forEach((coupon) => {
        coupon.got = false
      })
      favIds.value = []
      showSuccessToast('已退出登录')
      activeTab.value = 2
    })
  }

  const openEditName = () => {
    editingName.value = currentUser.value.nickname
    showEditNameDialog.value = true
  }

  const submitEditName = async () => {
    if (!editingName.value) return showToast('昵称不能为空')
    const res = await updateProfile({ nickname: editingName.value })
    if (res.data.code === 200) {
      currentUser.value.nickname = editingName.value
      showSuccessToast('修改成功')
    } else {
      showToast(res.data.msg)
    }
  }

  const resetChangePasswordForm = () => {
    changePasswordForm.old_password = ''
    changePasswordForm.new_password = ''
    changePasswordForm.confirm_password = ''
  }

  const openChangePasswordDialog = () => {
    resetChangePasswordForm()
    showChangePasswordDialog.value = true
  }

  const submitChangePassword = async () => {
    if (!changePasswordForm.old_password || !changePasswordForm.new_password || !changePasswordForm.confirm_password) {
      return showToast('请填写完整信息')
    }
    if (changePasswordForm.new_password.length < 6) return showToast('新密码至少 6 位')
    if (changePasswordForm.new_password !== changePasswordForm.confirm_password) {
      return showToast('两次输入的新密码不一致')
    }
    const res = await updatePassword({
      old_password: changePasswordForm.old_password,
      new_password: changePasswordForm.new_password,
    })
    if (res.data.code === 200) {
      showChangePasswordDialog.value = false
      resetChangePasswordForm()
      showSuccessToast('密码已更新')
    } else {
      showToast(res.data.msg)
    }
  }

  const openEditHeroText = () => {
    editingHeroText.value = heroText.value
    showEditHeroDialog.value = true
  }

  const submitEditHeroText = () => {
    const text = (editingHeroText.value || '').trim()
    if (!text) return showToast('文案不能为空')
    if (text.length > HERO_TEXT_MAX) return showToast(`最多 ${HERO_TEXT_MAX} 个字`)
    updateProfile({ hero_text: text })
      .then((res) => {
        if (res.data.code === 200) {
          heroText.value = res.data.hero_text || text
          if (currentUser.value) currentUser.value.hero_text = heroText.value
          showEditHeroDialog.value = false
          showSuccessToast('修改成功')
        } else {
          showToast(res.data.msg || '修改失败')
        }
      })
      .catch(() => showToast('网络错误'))
  }

  const handleAvatarChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    showLoadingToast({ message: '上传中...', forbidClick: true, duration: 0 })
    try {
      const uploadRes = await uploadImage(form)
      if (uploadRes.data.code !== 200) {
        closeToast()
        return showToast('上传失败')
      }
      const url = uploadRes.data.url
      const res = await updateProfile({ avatar: url })
      closeToast()
      if (res.data.code === 200) {
        currentUser.value.avatar = url
        showSuccessToast('头像已更新')
      } else {
        showToast(res.data.msg)
      }
    } catch (error) {
      closeToast()
      showToast('网络错误')
    }
    event.target.value = ''
  }

  const upgradeVip = () => {
    if (!currentUser.value) return showToast('请登录')
    showVipModal.value = true
  }

  const openVipCenter = () => upgradeVip()

  const selectVip = (level) => {
    if (!currentUser.value) return showToast('请登录')
    if (currentUser.value.level >= level) return showToast('当前等级已满足')
    pendingVipLevel.value = level
    showVipModal.value = false
    showVipPayDialog.value = true
  }

  const confirmVipPay = async () => {
    showLoadingToast({ message: '处理中...', forbidClick: true, duration: 0 })
    try {
      const res = await upgradeVipLevel(pendingVipLevel.value)
      closeToast()
      if (res.data.code === 200) {
        currentUser.value.level = res.data.level
        showSuccessToast('升级成功')
        showVipPayDialog.value = false
      } else {
        showToast(res.data.msg)
      }
    } catch (error) {
      closeToast()
      showToast('网络错误')
    }
  }

  return {
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
  }
}
