import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind class names conditionally, resolving conflicting
 * utility classes (the standard shadcn/ui `cn` helper).
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
