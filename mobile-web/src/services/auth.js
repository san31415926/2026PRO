import { http } from './http'


export const loginMobile = (payload) => http.post('/api/mobile/login', payload)
export const registerMobile = (payload) => http.post('/api/mobile/register', payload)
export const signinMobile = () => http.post('/api/mobile/signin')
export const logoutMobile = () => http.post('/api/mobile/logout')
export const fetchSessionUser = () => http.get('/api/mobile/session_user')
