// Lists feature API client
import type { List } from "@/lib/types"

export const listsApi = {
  async getLists(): Promise<{ success: boolean; data?: List[] }> {
    const response = await fetch("/api/lists")
    return response.json()
  },

  async createList(data: { title: string; description?: string; color?: string }) {
    const response = await fetch("/api/lists", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async updateList(id: string, data: { title?: string; description?: string; color?: string }) {
    const response = await fetch(`/api/lists/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async deleteList(id: string) {
    const response = await fetch(`/api/lists/${id}`, {
      method: "DELETE",
    })
    return response.json()
  },
}
