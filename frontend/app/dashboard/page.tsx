"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { authApi } from "@/features/auth/api"
import { listsApi } from "@/features/lists/api"
import type { List } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { CreateListDialog } from "@/features/lists/create-list-dialog"
import { ListCard } from "@/features/lists/list-card"
import { CheckCircle2, LogOut, Loader2 } from "lucide-react"

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [lists, setLists] = useState<List[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const userResult = await authApi.getCurrentUser()
      if (!userResult.success) {
        router.push("/login")
        return
      }
      setUser(userResult.user)

      const listsResult = await listsApi.getLists()
      if (listsResult.success && listsResult.data) {
        setLists(listsResult.data)
      }
    } catch (error) {
      console.error("[TaskFlow] Load data error:", error)
      router.push("/login")
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await authApi.logout()
    router.push("/login")
  }

  // TODO: Fetch task count from API when lists/tasks endpoints are updated
  const getTaskCount = (_listId: string) => {
    return 0
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">TaskFlow</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">
                Welcome, <strong>{user?.name}</strong>
              </span>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">My Lists</h1>
            <p className="text-muted-foreground">Organize your tasks into lists and stay productive</p>
          </div>
          <CreateListDialog onListCreated={loadData} />
        </div>

        {lists.length === 0 ? (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <CheckCircle2 className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h2 className="text-2xl font-semibold mb-2">No lists yet</h2>
              <p className="text-muted-foreground mb-6">Create your first list to start organizing your tasks</p>
              <CreateListDialog onListCreated={loadData} />
            </div>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {lists.map((list) => (
              <ListCard
                key={list.id}
                list={list}
                taskCount={getTaskCount(list.id)}
                onListUpdated={loadData}
                onListDeleted={loadData}
                onListClick={() => router.push(`/dashboard/lists/${list.id}`)}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
