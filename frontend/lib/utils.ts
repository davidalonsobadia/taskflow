import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { randomUUID } from "crypto"

export function generateId(): string {
  return randomUUID()
}

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
