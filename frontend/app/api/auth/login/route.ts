import { type NextRequest, NextResponse } from "next/server"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"
import { cookies } from "next/headers"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    // Call real backend API
    const data = await apiFetch<{ access_token: string; token_type: string; user: any }>(
      config.api.endpoints.backend.auth.login,
      {
        method: "POST",
        body: JSON.stringify({ email, password }),
      },
    )

    // Store the access token in a cookie
    const cookieStore = await cookies()
    cookieStore.set("auth-token", data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7 days
    })

    return NextResponse.json({
      success: true,
      message: "Login successful",
      user: data.user,
      token: data.access_token,
    })
  } catch (error) {
    console.error("[TaskFlow] Login error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json(
      { success: false, message: "Login failed" },
      { status: 500 },
    )
  }
}
