export function useGroupPurchase(options) {
  const {
    pendingGroupAction,
    inputGroupCode,
    isGroupBuyMode,
    showGroupChoiceDialog,
    showJoinGroupInput,
    showBuyDialog,
    showToast,
  } = options

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

  const startNewGroup = () => {
    pendingGroupAction.value = 'create'
    showGroupChoiceDialog.value = false
    showBuyDialog.value = true
  }

  const joinGroup = () => {
    if (!inputGroupCode.value) return showToast('请输入拼团码')
    pendingGroupAction.value = 'join'
    showBuyDialog.value = true
  }

  return {
    cancelGroupChoice,
    openJoinGroupDialog,
    buyGroupItemDirectly,
    startNewGroup,
    joinGroup,
  }
}
