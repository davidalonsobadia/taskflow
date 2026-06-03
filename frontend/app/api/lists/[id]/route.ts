import { type NextRequest, NextResponse } from "next/server"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"
import { getAuthToken } from "@/lib/auth"
import { type ListResponse, transformListResponse } from "@/lib/types"

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const token = await getAuthToken()

    if (!token) {
      return NextResponse.json({ success: false, message: "Unauthorized" }, { status: 401 })
    }

    const { id } = await params

    // Call backend API to get list by ID
    const backendList = await apiFetch<ListResponse>(config.api.endpoints.backend.lists.byId(id), {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    // Transform backend response to frontend format
    const list = transformListResponse(backendList)

    return NextResponse.json({
      success: true,
      data: list,
    })
  } catch (error) {
    console.error("[TaskFlow] Get list error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to fetch list" }, { status: 500 })
  }
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const token = await getAuthToken()

    if (!token) {
      return NextResponse.json({ success: false, message: "Unauthorized" }, { status: 401 })
    }

    const { id } = await params
    const updates = await request.json()

    // Transform 'title' to 'name' if present (frontend uses 'title', backend uses 'name')
    const requestBody: any = {}
    if (updates.title !== undefined) {
      requestBody.name = updates.title
    }
    if (updates.description !== undefined) {
      requestBody.description = updates.description
    }
    if (updates.color !== undefined) {
      requestBody.color = updates.color
    }

    // Call backend API to update list
    const backendList = await apiFetch<ListResponse>(config.api.endpoints.backend.lists.byId(id), {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    })

    // Transform backend response to frontend format
    const updatedList = transformListResponse(backendList)

    return NextResponse.json({
      success: true,
      data: updatedList,
      message: "List updated successfully",
    })
  } catch (error) {
    console.error("[TaskFlow] Update list error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to update list" }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const token = await getAuthToken()

    if (!token) {
      return NextResponse.json({ success: false, message: "Unauthorized" }, { status: 401 })
    }

    const { id } = await params

    // Call backend API to delete list
    const result = await apiFetch(config.api.endpoints.backend.lists.byId(id), {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    return NextResponse.json({
      success: true,
      message: result.message || "List deleted successfully",
    })
  } catch (error) {
    console.error("[TaskFlow] Delete list error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to delete list" }, { status: 500 })
  }
}
