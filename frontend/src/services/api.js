const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const API_USER = import.meta.env.VITE_API_USER ?? 'admin'
const API_PASS = import.meta.env.VITE_API_PASS ?? 'admin'

const authHeader = () => {
  const token = btoa(`${API_USER}:${API_PASS}`)
  return { Authorization: `Basic ${token}` }
}

const handleResponse = async (response) => {
  if (response.status === 401) {
    throw new Error('Unauthorized')
  }
  return response.json()
}

export const apiFetch = async (path, options = {}) => {
  const headers = {
    ...options.headers,
    ...authHeader()
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  })
  return handleResponse(response)
}

export const apiKeyFetch = async (path, options = {}) => {
  const response = await fetch(`${API_BASE}${path}`, options)
  return handleResponse(response)
}
