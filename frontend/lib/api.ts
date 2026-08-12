export type DashboardStats = { device_count: number; today_inspection_count: number; pending_maintenance_count: number; supplier_count: number };
export type Device = { id: number; device_code: string; device_name: string; device_type: string; location: string; status: string };
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
async function get<T>(path: string): Promise<T> { const response = await fetch(`${API_URL}${path}`, { next: { revalidate: 30 } }); if (!response.ok) throw new Error(`API request failed: ${response.status}`); return response.json() as Promise<T>; }
export const getStats = () => get<DashboardStats>("/api/dashboard/stats");
export const getDevices = () => get<Device[]>("/api/devices?limit=5");

