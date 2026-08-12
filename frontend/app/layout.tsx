import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "SmartCampus AI Copilot", description: "智慧校园运维与供应链 AI Agent 平台" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="zh-CN"><body>{children}</body></html>; }

