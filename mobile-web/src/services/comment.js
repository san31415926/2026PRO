import { http } from './http'


export const submitCommentByOrder = (payload) => http.post('/api/mobile/comments/add', payload)
