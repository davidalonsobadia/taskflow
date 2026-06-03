"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/features/auth/hooks/use-auth"
import { useLists } from "@/features/lists/hooks/use-lists"
import { Button } from "@/components/ui/button"
import { CheckCircle2, LogOut, Loader2 } from "lucide-react"
import { config } from "@/lib/config"
import { ListsSidebar } from "@/features/lists/components/lists-sidebar"
import { CreateListDialog } from "@/features/lists/create-list-dialog"

export default function ListsPage() {
  const router = useRouter()
  const { user, loading: authLoading, logout } = useAuth()
  const { lists, loading: listsLoading } = useLists()
  const [showCreateDialog, setShowCreateDialog] = useState(false)

  if (authLoading || listsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
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

      <div className="flex-1 flex">
        <aside className="w-64 hidden md:block">
          <ListsSidebar
            lists={lists}
            onListSelect={(id) => router.push(config.routes.listDetail(id))}
            onCreateClick={() => setShowCreateDialog(true)}
          />
        </aside>

        <main className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <CheckCircle2 className="h-20 w-20 text-muted-foreground mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-3">Welcome to {config.app.name}</h2>
            <p className="text-muted-foreground mb-6">
              {lists.length === 0
                ? "Create your first list to start organizing your tasks"
                : "Select a list from the sidebar to view and manage your tasks"}
            </p>
            {lists.length === 0 && (
              <Button onClick={() => setShowCreateDialog(true)} size="lg">
                Create Your First List
              </Button>
            )}
          </div>
        </main>
      </div>

      <CreateListDialog open={showCreateDialog} onOpenChange={setShowCreateDialog} />
    </div>
  )
}
