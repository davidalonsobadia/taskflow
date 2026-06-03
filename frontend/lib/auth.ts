// Authentication utilities
import { cookies } from "next/headers"
import { apiFetch, ApiError } from "./api-client"
import { config } from "./config"

/**
 * Get the current authenticated user from the backend API
 * @returns User object or null if not authenticated
 */
export async function getCurrentUser() {
  const cookieStore = await cookies()
  const token = cookieStore.get("auth-token")?.value

  if (!token) return null

  try {
    const data = await apiFetch(config.api.endpoints.backend.auth.me, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    return data.user || data
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      // Token is invalid, clear it
      cookieStore.delete("auth-token")
    }
    return null
  }
}

/**
 * Require authentication, throw error if not authenticated
 * @returns User object
 * @throws Error if not authenticated
 */
export async function requireAuth() {
  const user = await getCurrentUser()
  if (!user) {
    throw new Error("Unauthorized")
  }
  return user
}

/**
 * Get the auth token from cookies
 * @returns Token string or null
 */
export async function getAuthToken(): Promise<string | null> {
  const cookieStore = await cookies()
  return cookieStore.get("auth-token")?.value || null
}
