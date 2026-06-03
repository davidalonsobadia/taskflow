// Auth feature API client
export const authApi = {
  async register(data: { name: string; email: string; password: string }) {
    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async login(data: { email: string; password: string }) {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async logout() {
    const response = await fetch("/api/auth/logout", {
      method: "POST",
    })
    return response.json()
  },

  async verifyEmail(token: string) {
    const response = await fetch("/api/auth/verify-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    })
    return response.json()
  },

  async forgotPassword(email: string) {
    const response = await fetch("/api/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    })
    return response.json()
  },

  async resetPassword(token: string, password: string) {
    const response = await fetch("/api/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password }),
    })
    return response.json()
  },

  async getCurrentUser() {
    const response = await fetch("/api/auth/me")
    return response.json()
  },
}
