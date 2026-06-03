import { type NextRequest, NextResponse } from "next/server"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, email, password } = body

    // Call real backend API
    const data = await apiFetch(config.api.endpoints.backend.auth.register, {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    })

    // Log verification token if present (for development)
    if (data.verification_token) {
      console.log(`[TaskFlow] Verification token for ${email}: ${data.verification_token}`)
    }

    return NextResponse.json({
      success: true,
      message: data.message || "Registration successful! Please check your email to verify your account.",
      user: data.user,
    })
  } catch (error) {
    console.error("[TaskFlow] Registration error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json(
      { success: false, message: "Registration failed" },
      { status: 500 },
    )
  }
}
