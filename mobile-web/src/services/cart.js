import { http } from './http'


export const fetchCartList = () => http.get('/api/mobile/cart/list')
export const addCartItem = (productId) => http.post('/api/mobile/cart/add', { product_id: productId })
export const updateCartItem = (id, num) => http.post('/api/mobile/cart/update', { id, num })
export const checkoutCart = (payload) => http.post('/api/mobile/cart/checkout', payload)
