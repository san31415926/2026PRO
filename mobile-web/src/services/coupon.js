import { http } from './http'


export const fetchCouponMarket = () => http.get('/api/mobile/coupon/market')
export const fetchMyCoupons = () => http.get('/api/mobile/coupon/my')
export const claimCoupon = (id) => http.post('/api/mobile/coupon/get', { id })
