import client from './client'

export const login = (payload) => client.post('/auth/login', payload)
export const register = (payload) => client.post('/auth/register', payload)
export const getCurrentUser = () => client.get('/users/me')
