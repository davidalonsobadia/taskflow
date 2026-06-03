// Tasks hook for state management
"use client"

import { useState, useEffect, useCallback } from "react"
import { tasksService } from "../services/tasks.service"
import type { Task } from "@/lib/types"

export function useTasks(listId: string) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTasks = useCallback(async () => {
    if (!listId) return
    try {
      setLoading(true)
      const result = await tasksService.getTasks(listId)
      if (result.success && result.data) {
        setTasks(result.data)
      }
    } catch (err) {
      setError("Failed to fetch tasks")
    } finally {
      setLoading(false)
    }
  }, [listId])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  const createTask = async (data: {
    title: string
    description?: string
    priority?: "low" | "medium" | "high"
    dueDate?: string
  }) => {
    try {
      const result = await tasksService.createTask({ ...data, listId })
      if (result.success) {
        await fetchTasks()
        return { success: true }
      }
      return { success: false, error: result.error }
    } catch (err) {
      return { success: false, error: "Failed to create task" }
    }
  }

  const updateTask = async (
    id: string,
    data: {
      title?: string
      description?: string
      completed?: boolean
      priority?: "low" | "medium" | "high"
      dueDate?: string
    },
  ) => {
    try {
      const result = await tasksService.updateTask(id, data)
      if (result.success) {
        await fetchTasks()
        return { success: true }
      }
      return { success: false, error: result.error }
    } catch (err) {
      return { success: false, error: "Failed to update task" }
    }
  }

  const deleteTask = async (id: string) => {
    try {
      const result = await tasksService.deleteTask(id)
      if (result.success) {
        await fetchTasks()
        return { success: true }
      }
      return { success: false, error: result.error }
    } catch (err) {
      return { success: false, error: "Failed to delete task" }
    }
  }

  return { tasks, loading, error, createTask, updateTask, deleteTask, refetch: fetchTasks }
}
