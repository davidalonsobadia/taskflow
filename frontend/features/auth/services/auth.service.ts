// Auth service layer for API calls
import { config } from "@/lib/config"

export const authService = {
  async register(data: { name: string; email: string; password: string }) {
    const response = await fetch(config.api.endpoints.auth.register, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async login(data: { email: string; password: string }) {
    const response = await fetch(config.api.endpoints.auth.login, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async logout() {
    const response = await fetch(config.api.endpoints.auth.logout, {
      method: "POST",
    })
    return response.json()
  },

  async verifyEmail(token: string) {
    const response = await fetch(config.api.endpoints.auth.verifyEmail, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    })
    return response.json()
  },

  async forgotPassword(email: string) {
    const response = await fetch(config.api.endpoints.auth.forgotPassword, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    })
    return response.json()
  },

  async resetPassword(token: string, password: string) {
    const response = await fetch(config.api.endpoints.auth.resetPassword, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password }),
    })
    return response.json()
  },

  async getCurrentUser() {
    const response = await fetch(config.api.endpoints.auth.me)
    return response.json()
  },
}
