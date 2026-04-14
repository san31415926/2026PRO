import { http } from './http'


export const createOrder = (payload) => http.post('/api/mobile/order', payload)
export const fetchMyOrders = () => http.get('/api/mobile/my_orders')
export const confirmReceipt = (id) => http.post(`/api/mobile/orders/${id}/confirm`)
export const cancelOrderById = (id) => http.post(`/api/mobile/orders/${id}/cancel`)
export const fetchOrderDetail = (id) => http.get(`/api/mobile/orders/${id}`)
export const fetchOrderLogistics = (id) => http.get(`/api/mobile/orders/${id}/logistics`)
