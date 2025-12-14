import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function cleanJsonString(jsonString: string): string {
  // Remove markdown code block delimiters (```json ... ```)
  const cleanedString = jsonString.replace(/^```json\s*/, '').replace(/```$/, '');
  return cleanedString.trim();
}
