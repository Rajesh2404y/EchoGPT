import { Clock3, LayoutDashboard, MessageSquareText, Settings, UploadCloud } from "lucide-react";
import { NavLink } from "react-router-dom";

const items = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/upload", icon: UploadCloud, label: "Upload" },
  { to: "/chat", icon: MessageSquareText, label: "Chat" },
  { to: "/history", icon: Clock3, label: "History" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

function NavItems({ compact = false }) {
  return items.map(({ to, icon: Icon, label }) => (
    <NavLink
      key={to}
      to={to}
      className={({ isActive }) => `nav-item ${compact ? "justify-center" : ""} ${isActive ? "nav-item-active" : ""}`}
      title={label}
    >
      <Icon size={18} />
      {!compact && <span>{label}</span>}
    </NavLink>
  ));
}

export default function Sidebar() {
  return (
    <>
      <aside className="hidden min-h-[calc(100vh-4rem)] border-r border-white/10 bg-[var(--sidebar)]/70 p-3 backdrop-blur-xl md:block">
        <nav className="grid gap-1">
          <NavItems />
        </nav>
        <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.06] p-3 text-xs text-zinc-400">
          <p className="font-semibold text-zinc-200">AI stack</p>
          <p className="mt-1">Whisper, BGE, ChromaDB, Ollama</p>
        </div>
      </aside>

      <nav className="fixed inset-x-3 bottom-3 z-40 grid grid-cols-5 gap-1 rounded-2xl border border-white/10 bg-black/70 p-2 shadow-2xl backdrop-blur-2xl md:hidden">
        <NavItems compact />
      </nav>
    </>
  );
}
