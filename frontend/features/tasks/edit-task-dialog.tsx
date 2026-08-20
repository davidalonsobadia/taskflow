"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useTasksContext } from "./context/tasks-context"
import type { Recurrence, Task } from "@/lib/types"

interface EditTaskDialogProps {
  task: Task
  open: boolean
  onOpenChange: (open: boolean) => void
  onTaskUpdated?: () => void
}

export function EditTaskDialog({ task, open, onOpenChange, onTaskUpdated }: EditTaskDialogProps) {
  const [title, setTitle] = useState(task.title)
  const [description, setDescription] = useState(task.description || "")
  const [priority, setPriority] = useState<"low" | "medium" | "high">(task.priority)
  const [dueDate, setDueDate] = useState(task.dueDate ? task.dueDate.split("T")[0] : "")
  const [recurrence, setRecurrence] = useState<Recurrence>(task.recurrence)
  const [loading, setLoading] = useState(false)
  const { updateTask } = useTasksContext()

  useEffect(() => {
    setTitle(task.title)
    setDescription(task.description || "")
    setPriority(task.priority)
    setDueDate(task.dueDate ? task.dueDate.split("T")[0] : "")
    setRecurrence(task.recurrence)
  }, [task])

  // A recurring task needs a due date to anchor the rule (mirrors the backend rule).
  const recurrenceNeedsDueDate = recurrence !== "none" && !dueDate

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (recurrenceNeedsDueDate) return
    setLoading(true)

    try {
      const result = await updateTask(task.id, {
        title,
        description,
        priority,
        dueDate: dueDate || undefined,
        recurrence,
      })
      if (result.success) {
        onOpenChange(false)
        onTaskUpdated?.()
      }
    } catch (error) {
      console.error("[TaskFlow] Update task error:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit task</DialogTitle>
            <DialogDescription>Update your task details</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                placeholder="e.g., Complete project proposal"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                placeholder="Add more details..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Select value={priority} onValueChange={(value: any) => setPriority(value)}>
                  <SelectTrigger id="priority">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="dueDate">Due Date (optional)</Label>
                <Input id="dueDate" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="recurrence">Recurrence</Label>
              <Select value={recurrence} onValueChange={(value: Recurrence) => setRecurrence(value)}>
                <SelectTrigger id="recurrence">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  <SelectItem value="daily">Daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="monthly">Monthly</SelectItem>
                </SelectContent>
              </Select>
              {recurrenceNeedsDueDate && (
                <p className="text-sm text-destructive">A due date is required for recurring tasks.</p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={loading || recurrenceNeedsDueDate}>
              {loading ? "Saving..." : "Save changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
