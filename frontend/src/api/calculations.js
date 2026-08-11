import client from './client'

export const calculateHeatFlow = (points) => client.post('/calculations/heat-flow', { points })
export const getHeatFlowRecords = () => client.get('/calculations/heat-flow')
export const deleteHeatFlowRecord = (id) => client.delete(`/calculations/heat-flow/${id}`)
export const saveHeatFlowInputs = (points) => client.put('/calculations/heat-flow', { points })
