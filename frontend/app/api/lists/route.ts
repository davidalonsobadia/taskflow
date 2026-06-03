import { type NextRequest, NextResponse } from "next/server"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"
import { getAuthToken } from "@/lib/auth"
import { type ListResponse, transformListResponse } from "@/lib/types"

export async function GET() {
  try {
    const token = await getAuthToken()

    if (!token) {
      return NextResponse.json({ success: false, message: "Unauthorized" }, { status: 401 })
    }

    // Call backend API to get lists
    const backendLists = await apiFetch<ListResponse[]>(config.api.endpoints.backend.lists.base, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    // Transform backend response to frontend format
    const lists = backendLists.map(transformListResponse)

    return NextResponse.json({
      success: true,
      data: lists,
    })
  } catch (error) {
    console.error("[TaskFlow] Get lists error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to fetch lists" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const token = await getAuthToken()

    if (!token) {
      return NextResponse.json({ success: false, message: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { title, description, color } = body

    // Backend expects 'name' instead of 'title'
    const requestBody = {
      name: title,
      description: description || null,
      color: color || "#dc2626",
    }

    // Call backend API to create list
    const backendList = await apiFetch<ListResponse>(config.api.endpoints.backend.lists.base, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    })

    // Transform backend response to frontend format
    const list = transformListResponse(backendList)

    return NextResponse.json({
      success: true,
      data: list,
      message: "List created successfully",
    })
  } catch (error) {
    console.error("[TaskFlow] Create list error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to create list" }, { status: 500 })
  }
}
