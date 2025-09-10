import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
export const MAIN_URL = "http://3.17.36.74:8000";
export const LOCAL_URL = "http://localhost:8000";

export const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  (process.env.NODE_ENV === "development" ? LOCAL_URL : MAIN_URL);