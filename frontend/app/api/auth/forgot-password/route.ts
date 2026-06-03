import { type NextRequest, NextResponse } from "next/server"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email } = body

    // Call real backend API
    const data = await apiFetch(config.api.endpoints.backend.auth.forgotPassword, {
      method: "POST",
      body: JSON.stringify({ email }),
    })

    // Log reset token if present (for development)
    if (data.reset_token) {
      console.log(`[TaskFlow] Password reset token for ${email}: ${data.reset_token}`)
    }

    return NextResponse.json({
      success: true,
      message: data.message || "If an account exists with this email, a password reset link has been sent.",
    })
  } catch (error) {
    console.error("[TaskFlow] Forgot password error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json(
      { success: false, message: "Request failed" },
      { status: 500 },
    )
  }
}
