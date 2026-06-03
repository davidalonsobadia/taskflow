// Tasks feature API client
import type { Task } from "@/lib/types"

export const tasksApi = {
  async getTasks(listId: string): Promise<{ success: boolean; data?: Task[] }> {
    const response = await fetch(`/api/tasks?listId=${listId}`)
    return response.json()
  },

  async createTask(data: {
    listId: string
    title: string
    description?: string
    priority?: "low" | "medium" | "high"
    dueDate?: string
  }) {
    const response = await fetch("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async updateTask(
    id: string,
    data: {
      title?: string
      description?: string
      completed?: boolean
      priority?: "low" | "medium" | "high"
      dueDate?: string
    },
  ) {
    const response = await fetch(`/api/tasks/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async deleteTask(id: string) {
    const response = await fetch(`/api/tasks/${id}`, {
      method: "DELETE",
    })
    return response.json()
  },
}
