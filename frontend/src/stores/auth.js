import { reactive } from 'vue'

const state = reactive({
  token: sessionStorage.getItem('token') || '',
  user: JSON.parse(sessionStorage.getItem('user') || 'null'),
})

export function useAuthStore() {
  function setToken(token) {
    state.token = token
    sessionStorage.setItem('token', token)
  }

  function setUser(user) {
    state.user = user
    sessionStorage.setItem('user', JSON.stringify(user))
  }

  function logout() {
    state.token = ''
    state.user = null
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('user')
  }

  function isLoggedIn() {
    return !!state.token
  }

  return {
    get token() { return state.token },
    get user() { return state.user },
    setToken,
    setUser,
    logout,
    isLoggedIn,
  }
}
