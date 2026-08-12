import type { DashboardStats, Device } from "@/lib/api";
import { RagChat } from "@/components/rag-chat";
export function Dashboard({ stats, devices }: { stats: DashboardStats; devices: Device[] }) {
  const cards = [["设备总数", stats.device_count], ["今日巡检", stats.today_inspection_count], ["待处理工单", stats.pending_maintenance_count], ["供应商", stats.supplier_count]];
  return <main className="mx-auto min-h-screen max-w-7xl px-6 py-10">
    <header className="mb-10"><div className="mb-3 inline-flex rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-300">Knowledge Intelligence · V0.2</div><h1 className="text-4xl font-semibold tracking-tight text-white">SmartCampus <span className="text-cyan-300">AI Copilot</span></h1><p className="mt-3 text-slate-400">智慧校园运维与供应链 AI Agent 平台</p></header>
    <section className="mb-8 grid gap-4 md:grid-cols-4">{cards.map(([label,value]) => <article key={label} className="panel p-5"><p className="text-sm text-slate-400">{label}</p><p className="mt-2 text-3xl font-semibold text-white">{value}</p></article>)}</section>
    <div className="grid gap-6 lg:grid-cols-[1.45fr_.8fr]">
      <RagChat />
      <aside className="panel p-6"><div className="mb-5 flex items-center justify-between"><h2 className="font-medium text-white">设备态势</h2><span className="text-xs text-slate-500">实时数据</span></div><div className="space-y-3">{devices.map(d => <div key={d.id} className="rounded-xl bg-slate-900/70 p-4"><div className="flex items-start justify-between gap-3"><div><p className="text-sm text-white">{d.device_name}</p><p className="mt-1 text-xs text-slate-500">{d.location}</p></div><span className={`mt-1 h-2.5 w-2.5 rounded-full ${d.status === "online" ? "bg-emerald-400" : d.status === "warning" ? "bg-amber-400" : "bg-rose-400"}`}/></div></div>)}</div></aside>
    </div></main>;
}
