import { type NextRequest, NextResponse } from "next/server"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { token, password } = body

    // Call real backend API
    const data = await apiFetch(config.api.endpoints.backend.auth.resetPassword, {
      method: "POST",
      body: JSON.stringify({ token, new_password: password }),
    })

    return NextResponse.json({
      success: true,
      message: data.message || "Password reset successfully! You can now log in with your new password.",
    })
  } catch (error) {
    console.error("[TaskFlow] Reset password error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json(
      { success: false, message: "Password reset failed" },
      { status: 500 },
    )
  }
}
