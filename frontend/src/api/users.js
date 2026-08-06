import client from './client'

export const listUsers = () => client.get('/users')
export const updateUser = (id, payload) => client.patch(`/users/${id}`, payload)
