import { type NextRequest, NextResponse } from "next/server"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"
import { getAuthToken } from "@/lib/auth"
import { type TaskResponse, transformTaskResponse } from "@/lib/types"

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const token = await getAuthToken()

    if (!token) {
      return NextResponse.json({ success: false, message: "Unauthorized" }, { status: 401 })
    }

    const { id } = await params

    // Call backend API to get task by ID
    const backendTask = await apiFetch<TaskResponse>(config.api.endpoints.backend.tasks.byId(id), {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    // Transform backend response to frontend format
    const task = transformTaskResponse(backendTask)

    return NextResponse.json({
      success: true,
      data: task,
    })
  } catch (error) {
    console.error("[TaskFlow] Get task error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to fetch task" }, { status: 500 })
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

    // Transform camelCase to snake_case for backend
    const requestBody: any = {}
    if (updates.title !== undefined) {
      requestBody.title = updates.title
    }
    if (updates.description !== undefined) {
      requestBody.description = updates.description
    }
    if (updates.priority !== undefined) {
      requestBody.priority = updates.priority
    }
    if (updates.dueDate !== undefined) {
      requestBody.due_date = updates.dueDate
    }
    if (updates.completed !== undefined) {
      requestBody.completed = updates.completed
    }

    // Call backend API to update task
    const backendTask = await apiFetch<TaskResponse>(config.api.endpoints.backend.tasks.byId(id), {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    })

    // Transform backend response to frontend format
    const updatedTask = transformTaskResponse(backendTask)

    return NextResponse.json({
      success: true,
      data: updatedTask,
      message: "Task updated successfully",
    })
  } catch (error) {
    console.error("[TaskFlow] Update task error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to update task" }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const token = await getAuthToken()

    if (!token) {
      return NextResponse.json({ success: false, message: "Unauthorized" }, { status: 401 })
    }

    const { id } = await params

    // Call backend API to delete task
    const result = await apiFetch(config.api.endpoints.backend.tasks.byId(id), {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    return NextResponse.json({
      success: true,
      message: result.message || "Task deleted successfully",
    })
  } catch (error) {
    console.error("[TaskFlow] Delete task error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to delete task" }, { status: 500 })
  }
}
