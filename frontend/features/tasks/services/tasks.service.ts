// Tasks service layer for API calls
import { config } from "@/lib/config"
import type { Task } from "@/lib/types"

export const tasksService = {
  async getTasks(listId: string): Promise<{ success: boolean; data?: Task[] }> {
    const response = await fetch(`${config.api.endpoints.tasks.base}?listId=${listId}`)
    return response.json()
  },

  async createTask(data: {
    listId: string
    title: string
    description?: string
    priority?: "low" | "medium" | "high"
    dueDate?: string
  }) {
    const response = await fetch(config.api.endpoints.tasks.base, {
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
    const response = await fetch(config.api.endpoints.tasks.byId(id), {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async deleteTask(id: string) {
    const response = await fetch(config.api.endpoints.tasks.byId(id), {
      method: "DELETE",
    })
    return response.json()
  },
}
