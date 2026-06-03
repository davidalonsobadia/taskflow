import { type NextRequest, NextResponse } from "next/server"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { token } = body

    // Call real backend API
    const data = await apiFetch(config.api.endpoints.backend.auth.verifyEmail, {
      method: "POST",
      body: JSON.stringify({ token }),
    })

    return NextResponse.json({
      success: true,
      message: data.message || "Email verified successfully! You can now log in.",
    })
  } catch (error) {
    console.error("[TaskFlow] Email verification error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json(
      { success: false, message: "Verification failed" },
      { status: 500 },
    )
  }
}
