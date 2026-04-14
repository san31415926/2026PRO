<template>
  <van-popup
    :show="show"
    class="sheet-popup mobile-shell-popup"
    position="bottom"
    :style="{ height: '100%', background: 'rgba(84, 49, 36, 0.18)' }"
    @update:show="updateShow"
  >
    <div class="popup-mobile-shell address-shell">
      <van-nav-bar title="地址管理" left-arrow @click-left="updateShow(false)" />
      <div class="popup-mobile-content address-content">
        <van-radio-group :model-value="selectedAddrId" @update:model-value="updateSelectedAddrId">
          <div
            v-for="addr in addressList"
            :key="addr.id"
            class="addr-box"
            @click="selectAddress(addr.id)"
          >
            <van-radio :name="addr.id" style="margin-right:12px;"></van-radio>
            <div class="addr-content">
              <div class="addr-topline">
                <b>{{ addr.name }} {{ addr.phone }}</b>
                <van-tag v-if="addr.is_default" plain type="danger" round>默认地址</van-tag>
              </div>
              <span class="addr-detail">{{ addr.detail }}</span>
              <div class="addr-actions">
                <van-button
                  v-if="!addr.is_default"
                  plain
                  round
                  size="small"
                  type="primary"
                  @click.stop="setDefaultAddress(addr.id)"
                >
                  设为默认
                </van-button>
              </div>
            </div>
          </div>
        </van-radio-group>
        <van-button type="danger" block round style="margin-top:18px;" @click="emit('open-add-form')">新增地址</van-button>
      </div>
    </div>
  </van-popup>
</template>

<script setup>
defineProps({
  show: Boolean,
  addressList: { type: Array, default: () => [] },
  selectedAddrId: { type: Number, default: null },
  setDefaultAddress: { type: Function, required: true },
})

const emit = defineEmits(['update:show', 'update:selectedAddrId', 'open-add-form'])

const updateShow = value => emit('update:show', value)
const updateSelectedAddrId = value => emit('update:selectedAddrId', value)
const selectAddress = id => {
  emit('update:selectedAddrId', id)
  emit('update:show', false)
}
</script>
