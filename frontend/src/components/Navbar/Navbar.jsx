import { Bot, Palette, Search, Settings } from "lucide-react";
import { Link } from "react-router-dom";
import { useAppState } from "../../context/AppContext";

export default function Navbar() {
  const { settings, setSettings, themePresets } = useAppState();
  const activeIndex = themePresets.findIndex((theme) => theme.id === settings.themeId);

  function rotateTheme() {
    const next = themePresets[(activeIndex + 1) % themePresets.length];
    setSettings({ themeId: next.id });
  }

  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-black/45 backdrop-blur-2xl">
      <div className="mx-auto flex min-h-16 max-w-7xl items-center gap-3 px-3 md:px-5">
        <Link to="/" className="flex min-w-0 items-center gap-3">
          <span className="animated-gradient grid size-10 shrink-0 place-items-center rounded-2xl text-white shadow-xl">
            <Bot size={21} />
          </span>
          <div className="hidden min-w-0 sm:block">
            <p className="truncate text-base font-bold text-white">EchoGPT</p>
            <p className="truncate text-xs text-zinc-400">Universal media intelligence</p>
          </div>
        </Link>

        <div className="mx-auto hidden w-full max-w-xl items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.06] px-3 py-2 text-sm text-zinc-400 shadow-xl backdrop-blur md:flex">
          <Search size={16} className="shrink-0 text-zinc-500" />
          <input
            className="w-full bg-transparent text-zinc-200 outline-none placeholder:text-zinc-500"
            placeholder="Search transcripts, notes, timestamps"
            type="search"
          />
        </div>

        <div className="ml-auto flex items-center gap-2">
          <button className="icon-btn" type="button" onClick={rotateTheme} aria-label="Change theme">
            <Palette size={18} />
          </button>
          <Link className="icon-btn" to="/settings" aria-label="Settings">
            <Settings size={18} />
          </Link>
          <div className="grid size-10 place-items-center rounded-2xl border border-white/10 bg-white/10 text-sm font-bold text-white">
            RY
          </div>
        </div>
      </div>
      <div className="px-3 pb-3 md:hidden">
        <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.06] px-3 py-2 text-sm text-zinc-400">
          <Search size={16} />
          <input className="w-full bg-transparent outline-none" placeholder="Search EchoGPT" type="search" />
        </div>
      </div>
    </header>
  );
}
