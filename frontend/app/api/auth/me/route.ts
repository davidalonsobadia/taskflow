import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"

export async function GET() {
  try {
    const cookieStore = await cookies()
    const token = cookieStore.get("auth-token")?.value

    if (!token) {
      return NextResponse.json(
        { success: false, message: "Not authenticated" },
        { status: 401 },
      )
    }

    // Call real backend API
    const data = await apiFetch(config.api.endpoints.backend.auth.me, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    return NextResponse.json({
      success: true,
      user: data.user || data,
    })
  } catch (error) {
    console.error("[TaskFlow] Get current user error:", error)

    if (error instanceof ApiError) {
      // If unauthorized, clear the cookie
      if (error.status === 401) {
        const cookieStore = await cookies()
        cookieStore.delete("auth-token")
      }

      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json(
      { success: false, message: "Failed to get user" },
      { status: 500 },
    )
  }
}
