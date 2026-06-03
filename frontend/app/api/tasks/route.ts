import { type NextRequest, NextResponse } from "next/server"
import { apiFetch, ApiError } from "@/lib/api-client"
import { config } from "@/lib/config"
import { getAuthToken } from "@/lib/auth"
import { type TaskResponse, transformTaskResponse } from "@/lib/types"

export async function GET(request: NextRequest) {
  try {
    const token = await getAuthToken()

    if (!token) {
      return NextResponse.json({ success: false, message: "Unauthorized" }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const listId = searchParams.get("listId")

    if (!listId) {
      return NextResponse.json({ success: false, message: "List ID is required" }, { status: 400 })
    }

    // Call backend API to get tasks - backend expects list_id query param
    const backendTasks = await apiFetch<TaskResponse[]>(
      `${config.api.endpoints.backend.tasks.base}?list_id=${listId}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    // Transform backend response to frontend format
    const tasks = backendTasks.map(transformTaskResponse)

    return NextResponse.json({
      success: true,
      data: tasks,
    })
  } catch (error) {
    console.error("[TaskFlow] Get tasks error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to fetch tasks" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const token = await getAuthToken()

    if (!token) {
      return NextResponse.json({ success: false, message: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { listId, title, description, priority, dueDate } = body

    // Backend expects list_id and due_date (snake_case)
    const requestBody = {
      list_id: Number(listId),
      title,
      description: description || null,
      priority: priority || "medium",
      due_date: dueDate || null,
    }

    // Call backend API to create task
    const backendTask = await apiFetch<TaskResponse>(config.api.endpoints.backend.tasks.base, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    })

    // Transform backend response to frontend format
    const task = transformTaskResponse(backendTask)

    return NextResponse.json({
      success: true,
      data: task,
      message: "Task created successfully",
    })
  } catch (error) {
    console.error("[TaskFlow] Create task error:", error)

    if (error instanceof ApiError) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: error.status },
      )
    }

    return NextResponse.json({ success: false, message: "Failed to create task" }, { status: 500 })
  }
}
