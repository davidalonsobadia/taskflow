"use client"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { CheckCircle2, Plus } from "lucide-react"
import type { List } from "@/lib/types"
import { cn } from "@/lib/utils"

interface ListsSidebarProps {
  lists: List[]
  selectedListId?: string
  onListSelect: (listId: string) => void
  onCreateClick: () => void
}

export function ListsSidebar({ lists, selectedListId, onListSelect, onCreateClick }: ListsSidebarProps) {
  return (
    <div className="flex flex-col h-full border-r bg-card">
      <div className="p-4 border-b">
        <Button onClick={onCreateClick} className="w-full">
          <Plus className="h-4 w-4 mr-2" />
          New List
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {lists.length === 0 ? (
            <div className="text-center py-8 px-4">
              <CheckCircle2 className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-sm text-muted-foreground">No lists yet</p>
              <p className="text-xs text-muted-foreground mt-1">Create your first list to get started</p>
            </div>
          ) : (
            lists.map((list) => (
              <button
                key={list.id}
                onClick={() => onListSelect(list.id)}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-md transition-colors",
                  "hover:bg-accent hover:text-accent-foreground",
                  selectedListId === list.id && "bg-accent text-accent-foreground",
                )}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: list.color || "#dc2626" }} />
                  <span className="font-medium truncate">{list.title}</span>
                </div>
                {list.description && <p className="text-xs text-muted-foreground mt-1 truncate">{list.description}</p>}
              </button>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
