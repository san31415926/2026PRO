import { http } from './http'


export const rechargeBalance = (amount) => http.post('/api/mobile/recharge', { amount })
export const updateProfile = (payload) => http.post('/api/mobile/profile/update', payload)
export const updatePassword = (payload) => http.post('/api/mobile/profile/password', payload)
export const uploadImage = (formData) => http.post('/api/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
export const upgradeVipLevel = (level) => http.post('/api/mobile/vip/upgrade', { level })
