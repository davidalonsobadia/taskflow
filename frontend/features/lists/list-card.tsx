"use client"

import type { List } from "@/lib/types"
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { EditListDialog } from "./edit-list-dialog"
import { DeleteListDialog } from "./delete-list-dialog"
import { ListTodo } from "lucide-react"

interface ListCardProps {
  list: List
  taskCount: number
  onListUpdated: () => void
  onListDeleted: () => void
  onListClick: () => void
}

export function ListCard({ list, taskCount, onListUpdated, onListDeleted, onListClick }: ListCardProps) {
  return (
    <Card className="cursor-pointer hover:shadow-md transition-shadow group">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1" onClick={onListClick}>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: list.color || "#6b7280" }} />
              <CardTitle className="text-lg">{list.title}</CardTitle>
            </div>
            {list.description && <CardDescription className="mb-2">{list.description}</CardDescription>}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <ListTodo className="h-4 w-4" />
              <span>
                {taskCount} {taskCount === 1 ? "task" : "tasks"}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <EditListDialog list={list} onListUpdated={onListUpdated} />
            <DeleteListDialog list={list} onListDeleted={onListDeleted} />
          </div>
        </div>
      </CardHeader>
    </Card>
  )
}
