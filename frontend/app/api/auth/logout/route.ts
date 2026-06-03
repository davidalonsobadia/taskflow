import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"

export async function POST() {
  try {
    const cookieStore = await cookies()
    const token = cookieStore.get("auth-token")?.value

    // Call backend logout if token exists
    if (token) {
      try {
        await apiFetch(config.api.endpoints.backend.auth.logout, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      } catch (error) {
        // Continue with logout even if backend call fails
        console.warn("[TaskFlow] Backend logout failed:", error)
      }
    }

    // Always clear the cookie
    cookieStore.delete("auth-token")

    return NextResponse.json({
      success: true,
      message: "Logged out successfully",
    })
  } catch (error) {
    console.error("[TaskFlow] Logout error:", error)
    return NextResponse.json(
      { success: false, message: "Logout failed" },
      { status: 500 },
    )
  }
}
