"use client"

import type { Task } from "@/lib/types"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { EditTaskDialog } from "./edit-task-dialog"
import { DeleteTaskDialog } from "./delete-task-dialog"
import { useTasksContext } from "./context/tasks-context"
import { Calendar, Flag } from "lucide-react"
import { cn } from "@/lib/utils"
import { useState } from "react"

interface TaskItemProps {
  task: Task
}

const priorityColors = {
  low: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  medium: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  high: "bg-red-500/10 text-red-500 border-red-500/20",
}

export function TaskItem({ task }: TaskItemProps) {
  const { updateTask } = useTasksContext()
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const handleToggleComplete = async () => {
    try {
      await updateTask(task.id, { completed: !task.completed })
    } catch (error) {
      console.error("[TaskFlow] Toggle task error:", error)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
  }

  return (
    <>
      <div className="flex items-start gap-3 p-4 border rounded-lg bg-card hover:shadow-sm transition-shadow group">
        <Checkbox checked={task.completed} onCheckedChange={handleToggleComplete} className="mt-1" />
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <h4 className={cn("font-medium mb-1", task.completed && "line-through text-muted-foreground")}>
                {task.title}
              </h4>
              {task.description && <p className="text-sm text-muted-foreground mb-2">{task.description}</p>}
              <div className="flex items-center gap-2 flex-wrap">
                <Badge variant="outline" className={priorityColors[task.priority]}>
                  <Flag className="h-3 w-3 mr-1" />
                  {task.priority}
                </Badge>
                {task.dueDate && (
                  <Badge variant="outline">
                    <Calendar className="h-3 w-3 mr-1" />
                    {formatDate(task.dueDate)}
                  </Badge>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() => setShowEditDialog(true)}
                className="p-2 hover:bg-accent rounded-md transition-colors"
              >
                <span className="sr-only">Edit task</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                  <path d="m15 5 4 4" />
                </svg>
              </button>
              <button
                onClick={() => setShowDeleteDialog(true)}
                className="p-2 hover:bg-accent rounded-md transition-colors text-destructive"
              >
                <span className="sr-only">Delete task</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M3 6h18" />
                  <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                  <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <EditTaskDialog task={task} open={showEditDialog} onOpenChange={setShowEditDialog} />
      <DeleteTaskDialog task={task} open={showDeleteDialog} onOpenChange={setShowDeleteDialog} />
    </>
  )
}
