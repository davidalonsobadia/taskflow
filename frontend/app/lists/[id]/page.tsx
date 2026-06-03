"use client"

import { useState } from "react"
import { useRouter, useParams } from "next/navigation"
import { useAuth } from "@/features/auth/hooks/use-auth"
import { useLists } from "@/features/lists/hooks/use-lists"
import { TasksProvider, useTasksContext } from "@/features/tasks/context/tasks-context"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CheckCircle2, LogOut, Loader2, Plus } from "lucide-react"
import { config } from "@/lib/config"
import { ListsSidebar } from "@/features/lists/components/lists-sidebar"
import { ListHeader } from "@/features/lists/components/list-header"
import { CreateListDialog } from "@/features/lists/create-list-dialog"
import { EditListDialog } from "@/features/lists/edit-list-dialog"
import { DeleteListDialog } from "@/features/lists/delete-list-dialog"
import { CreateTaskDialog } from "@/features/tasks/create-task-dialog"
import { TaskItem } from "@/features/tasks/task-item"

function ListDetailContent() {
  const router = useRouter()
  const params = useParams()
  const listId = params.id as string

  const { user, loading: authLoading, logout } = useAuth()
  const { lists, loading: listsLoading } = useLists()
  const { tasks, loading: tasksLoading } = useTasksContext()

  const [showCreateListDialog, setShowCreateListDialog] = useState(false)
  const [showEditListDialog, setShowEditListDialog] = useState(false)
  const [showDeleteListDialog, setShowDeleteListDialog] = useState(false)
  const [showCreateTaskDialog, setShowCreateTaskDialog] = useState(false)

  const currentList = lists.find((l) => l.id === listId)
  const activeTasks = tasks.filter((t) => !t.completed)
  const completedTasks = tasks.filter((t) => t.completed)

  if (authLoading || listsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!currentList) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">List not found</h2>
          <Button onClick={() => router.push(config.routes.lists)}>Go to Lists</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">{config.app.name}</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">
                Welcome, <strong>{user?.name}</strong>
              </span>
              <Button variant="ghost" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-64 hidden md:block">
          <ListsSidebar
            lists={lists}
            selectedListId={listId}
            onListSelect={(id) => router.push(config.routes.listDetail(id))}
            onCreateClick={() => setShowCreateListDialog(true)}
          />
        </aside>

        <main className="flex-1 flex flex-col overflow-hidden">
          <ListHeader
            list={currentList}
            taskCount={tasks.length}
            onEdit={() => setShowEditListDialog(true)}
            onDelete={() => setShowDeleteListDialog(true)}
          />

          <div className="flex-1 overflow-auto">
            <div className="container mx-auto p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">Tasks</h2>
                <Button onClick={() => setShowCreateTaskDialog(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Task
                </Button>
              </div>

              {tasksLoading ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : tasks.length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircle2 className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">No tasks yet</h3>
                  <p className="text-muted-foreground mb-6">Add your first task to get started</p>
                  <Button onClick={() => setShowCreateTaskDialog(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Task
                  </Button>
                </div>
              ) : (
                <Tabs defaultValue="active" className="w-full">
                  <TabsList>
                    <TabsTrigger value="active">Active ({activeTasks.length})</TabsTrigger>
                    <TabsTrigger value="completed">Completed ({completedTasks.length})</TabsTrigger>
                    <TabsTrigger value="all">All ({tasks.length})</TabsTrigger>
                  </TabsList>

                  <TabsContent value="active" className="space-y-2 mt-4">
                    {activeTasks.length === 0 ? (
                      <p className="text-center text-muted-foreground py-8">No active tasks</p>
                    ) : (
                      activeTasks.map((task) => <TaskItem key={task.id} task={task} />)
                    )}
                  </TabsContent>

                  <TabsContent value="completed" className="space-y-2 mt-4">
                    {completedTasks.length === 0 ? (
                      <p className="text-center text-muted-foreground py-8">No completed tasks</p>
                    ) : (
                      completedTasks.map((task) => <TaskItem key={task.id} task={task} />)
                    )}
                  </TabsContent>

                  <TabsContent value="all" className="space-y-2 mt-4">
                    {tasks.map((task) => (
                      <TaskItem key={task.id} task={task} />
                    ))}
                  </TabsContent>
                </Tabs>
              )}
            </div>
          </div>
        </main>
      </div>

      <CreateListDialog open={showCreateListDialog} onOpenChange={setShowCreateListDialog} />
      <EditListDialog open={showEditListDialog} onOpenChange={setShowEditListDialog} list={currentList} />
      <DeleteListDialog
        open={showDeleteListDialog}
        onOpenChange={setShowDeleteListDialog}
        list={currentList}
        onSuccess={() => router.push(config.routes.lists)}
      />
      <CreateTaskDialog open={showCreateTaskDialog} onOpenChange={setShowCreateTaskDialog} listId={listId} />
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
