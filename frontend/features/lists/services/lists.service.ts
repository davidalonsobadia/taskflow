// Lists service layer for API calls
import { config } from "@/lib/config"
import type { List } from "@/lib/types"

export const listsService = {
  async getLists(): Promise<{ success: boolean; data?: List[] }> {
    const response = await fetch(config.api.endpoints.lists.base)
    return response.json()
  },

  async createList(data: { title: string; description?: string; color?: string }) {
    const response = await fetch(config.api.endpoints.lists.base, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async updateList(id: string, data: { title?: string; description?: string; color?: string }) {
    const response = await fetch(config.api.endpoints.lists.byId(id), {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  async deleteList(id: string) {
    const response = await fetch(config.api.endpoints.lists.byId(id), {
      method: "DELETE",
    })
    return response.json()
  },
}
