"use client"

import { createContext, useContext, type ReactNode } from "react"
import { useTasks } from "../hooks/use-tasks"
import type { Task } from "@/lib/types"

interface TasksContextValue {
  tasks: Task[]
  loading: boolean
  error: string | null
  createTask: (data: {
    title: string
    description?: string
    priority?: "low" | "medium" | "high"
    dueDate?: string
  }) => Promise<{ success: boolean; error?: string }>
  updateTask: (
    id: string,
    data: {
      title?: string
      description?: string
      completed?: boolean
      priority?: "low" | "medium" | "high"
      dueDate?: string
    }
  ) => Promise<{ success: boolean; error?: string }>
  deleteTask: (id: string) => Promise<{ success: boolean; error?: string }>
  refetch: () => Promise<void>
}

const TasksContext = createContext<TasksContextValue | null>(null)

interface TasksProviderProps {
  listId: string
  children: ReactNode
}

export function TasksProvider({ listId, children }: TasksProviderProps) {
  const tasksHook = useTasks(listId)

  return <TasksContext.Provider value={tasksHook}>{children}</TasksContext.Provider>
}

export function useTasksContext() {
  const context = useContext(TasksContext)
  if (!context) {
    throw new Error("useTasksContext must be used within a TasksProvider")
  }
  return context
}

