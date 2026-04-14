import { http } from './http'


export const toggleFavoriteItem = (productId) => http.post('/api/mobile/favorite/toggle', { product_id: productId })
export const fetchFavorites = () => http.get('/api/mobile/favorites')
