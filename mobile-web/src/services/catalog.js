import { http } from './http'


export const fetchProducts = () => http.get('/api/products')
export const fetchBanners = () => http.get('/api/banners')
export const fetchSystemConfig = () => http.get('/api/common/config')
export const fetchProductComments = (productId) => http.get(`/api/products/${productId}/comments`)
