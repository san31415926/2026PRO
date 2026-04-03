import { http } from './http'


export const fetchAddressList = () => http.get('/api/mobile/address')
export const createAddress = (payload) => http.post('/api/mobile/address', payload)
export const switchDefaultAddress = (id) => http.post(`/api/mobile/address/${id}/default`)
