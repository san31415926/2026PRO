import { createAddress, fetchAddressList, switchDefaultAddress } from '../services/address'


export function useAddressBook({
  addressList,
  selectedAddrId,
  newAddr,
  showAddAddrForm,
  showSuccessToast,
  showToast,
}) {
  const resetNewAddress = () => {
    newAddr.name = ''
    newAddr.phone = ''
    newAddr.detail = ''
    newAddr.is_default = false
  }

  const loadAddress = async () => {
    const res = await fetchAddressList()
    if (res.data.code === 200) {
      addressList.value = res.data.data
      const defaultAddr = addressList.value.find(item => item.is_default)
      if (defaultAddr) selectedAddrId.value = defaultAddr.id
      else if (addressList.value.length > 0 && !selectedAddrId.value) selectedAddrId.value = addressList.value[0].id
    }
  }

  const saveAddress = async () => {
    await createAddress(newAddr)
    showSuccessToast('成功')
    await loadAddress()
    showAddAddrForm.value = false
    resetNewAddress()
  }

  const setDefaultAddress = async (id) => {
    const res = await switchDefaultAddress(id)
    if (res.data.code === 200) {
      selectedAddrId.value = id
      showSuccessToast('默认地址已更新')
      await loadAddress()
    } else {
      showToast(res.data.msg || '设置失败')
    }
  }

  return {
    loadAddress,
    saveAddress,
    setDefaultAddress,
    resetNewAddress,
  }
}
