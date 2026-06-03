// Domain Types

export interface User {
  id: string
  name: string
  email: string
  password: string
  emailVerified: boolean
  verificationToken?: string
  resetToken?: string
  resetTokenExpiry?: number
  createdAt: string
}

// Backend API response types (snake_case)
export interface ListResponse {
  id: number
  user_id: number
  name: string
  description?: string | null
  color: string
  task_count?: number
  completed_count?: number
  created_at: string
  updated_at: string
}

// Frontend types (camelCase for easier use in components)
export interface List {
  id: string
  userId: string
  title: string
  description?: string
  color: string
  taskCount?: number
  completedCount?: number
  createdAt: string
  updatedAt: string
}

// Backend API response types (snake_case)
export interface TaskResponse {
  id: number
  list_id: number
  title: string
  description?: string | null
  completed: boolean
  priority: "low" | "medium" | "high"
  due_date?: string | null
  created_at: string
  updated_at: string
}

// Frontend types (camelCase for easier use in components)
export interface Task {
  id: string
  listId: string
  title: string
  description?: string
  completed: boolean
  priority: "low" | "medium" | "high"
  dueDate?: string
  createdAt: string
  updatedAt: string
}

export interface AuthResponse {
  success: boolean
  message?: string
  user?: Omit<User, "password">
  token?: string
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// Transformation utilities to convert between backend and frontend types
export function transformListResponse(backendList: ListResponse): List {
  return {
    id: String(backendList.id),
    userId: String(backendList.user_id),
    title: backendList.name,
    description: backendList.description || undefined,
    color: backendList.color,
    taskCount: backendList.task_count,
    completedCount: backendList.completed_count,
    createdAt: backendList.created_at,
    updatedAt: backendList.updated_at,
  }
}

export function transformTaskResponse(backendTask: TaskResponse): Task {
  return {
    id: String(backendTask.id),
    listId: String(backendTask.list_id),
    title: backendTask.title,
    description: backendTask.description || undefined,
    completed: backendTask.completed,
    priority: backendTask.priority,
    dueDate: backendTask.due_date || undefined,
    createdAt: backendTask.created_at,
    updatedAt: backendTask.updated_at,
  }
}
