import { Dashboard } from "@/components/dashboard";
import {
  getDevices,
  getStats,
  type DashboardStats,
  type Device,
} from "@/lib/api";

export const dynamic = "force-dynamic";

const fallback: DashboardStats = {
  device_count: 10,
  today_inspection_count: 4,
  pending_maintenance_count: 4,
  supplier_count: 5,
};

export default async function Home() {
  let stats = fallback;
  let devices: Device[] = [];

  try {
    [stats, devices] = await Promise.all([getStats(), getDevices()]);
  } catch {}

  return <Dashboard stats={stats} devices={devices} />;
}
