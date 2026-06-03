"use client"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import { listsApi } from "@/features/lists/api"
import { TasksProvider, useTasksContext } from "@/features/tasks/context/tasks-context"
import type { List } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { CreateTaskDialog } from "@/features/tasks/create-task-dialog"
import { TaskItem } from "@/features/tasks/task-item"
import { ArrowLeft, Loader2, CheckCircle2 } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

function ListDetailContent() {
  const router = useRouter()
  const params = useParams()
  const listId = params.id as string

  const [list, setList] = useState<List | null>(null)
  const { tasks, loading: tasksLoading } = useTasksContext()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [listId])

  const loadData = async () => {
    try {
      const listsResult = await listsApi.getLists()
      if (listsResult.success && listsResult.data) {
        const currentList = listsResult.data.find((l) => l.id === listId)
        if (!currentList) {
          router.push("/dashboard")
          return
        }
        setList(currentList)
      }
    } catch (error) {
      console.error("[TaskFlow] Load data error:", error)
      router.push("/dashboard")
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!list) {
    return null
  }

  const activeTasks = tasks.filter((t) => !t.completed)
  const completedTasks = tasks.filter((t) => t.completed)

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">TaskFlow</span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex items-start justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-4 h-4 rounded-full" style={{ backgroundColor: list.color || "#6b7280" }} />
              <h1 className="text-3xl font-bold">{list.title}</h1>
            </div>
            {list.description && <p className="text-muted-foreground">{list.description}</p>}
            <p className="text-sm text-muted-foreground mt-2">
              {tasks.length} {tasks.length === 1 ? "task" : "tasks"} total • {completedTasks.length} completed
            </p>
          </div>
          <CreateTaskDialog listId={listId} />
        </div>

        <Tabs defaultValue="active" className="w-full">
          <TabsList>
            <TabsTrigger value="active">Active ({activeTasks.length})</TabsTrigger>
            <TabsTrigger value="completed">Completed ({completedTasks.length})</TabsTrigger>
            <TabsTrigger value="all">All ({tasks.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="active" className="mt-6">
            {activeTasks.length === 0 ? (
              <div className="text-center py-12">
                <CheckCircle2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No active tasks</h3>
                <p className="text-muted-foreground mb-4">Create a new task to get started</p>
                <CreateTaskDialog listId={listId} />
              </div>
            ) : (
              <div className="space-y-3">
                {activeTasks.map((task) => (
                  <TaskItem key={task.id} task={task} />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="completed" className="mt-6">
            {completedTasks.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">No completed tasks yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {completedTasks.map((task) => (
                  <TaskItem key={task.id} task={task} />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="all" className="mt-6">
            {tasks.length === 0 ? (
              <div className="text-center py-12">
                <CheckCircle2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No tasks yet</h3>
                <p className="text-muted-foreground mb-4">Create your first task to get started</p>
                <CreateTaskDialog listId={listId} />
              </div>
            ) : (
              <div className="space-y-3">
                {tasks.map((task) => (
                  <TaskItem key={task.id} task={task} />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default function ListDetailPage() {
  const params = useParams()
  const listId = params.id as string

  return (
    <TasksProvider listId={listId}>
      <ListDetailContent />
    </TasksProvider>
  )
}
