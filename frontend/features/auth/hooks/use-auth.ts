// Auth hook for state management
"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { authService } from "../services/auth.service"
import { config } from "@/lib/config"

export function useAuth() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const result = await authService.getCurrentUser()
      if (result.success) {
        setUser(result.user)
      } else {
        router.push(config.routes.login)
      }
    } catch (err) {
      setError("Failed to authenticate")
      router.push(config.routes.login)
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
      setUser(null)
      router.push(config.routes.login)
    } catch (err) {
      setError("Failed to logout")
    }
  }

  return { user, loading, error, logout, refetch: checkAuth }
}
