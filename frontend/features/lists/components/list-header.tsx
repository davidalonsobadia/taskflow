"use client"

import { Button } from "@/components/ui/button"
import { MoreVertical } from "lucide-react"
import type { List } from "@/lib/types"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

interface ListHeaderProps {
  list: List
  taskCount: number
  onEdit: () => void
  onDelete: () => void
}

export function ListHeader({ list, taskCount, onEdit, onDelete }: ListHeaderProps) {
  return (
    <div className="border-b bg-card p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: list.color || "#dc2626" }} />
            <h1 className="text-3xl font-bold">{list.title}</h1>
          </div>
          {list.description && <p className="text-muted-foreground">{list.description}</p>}
          <p className="text-sm text-muted-foreground mt-2">
            {taskCount} {taskCount === 1 ? "task" : "tasks"}
          </p>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={onEdit}>Edit List</DropdownMenuItem>
            <DropdownMenuItem onClick={onDelete} className="text-destructive">
              Delete List
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
