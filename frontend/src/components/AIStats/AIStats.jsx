import { FileAudio, FileText, MessageSquareText, Video } from "lucide-react";
import { LazyMotion, domAnimation, m } from "framer-motion";
import { memo, useEffect, useMemo, useState } from "react";
import { getStats } from "../../services/statsService";

const fallbackStats = {
  videos_processed: 0,
  audio_files: 0,
  questions_asked: 0,
  summaries_generated: 0,
};

function AnimatedNumber({ value }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const target = Number(value || 0);
    if (target === 0) {
      setCurrent(0);
      return;
    }
    const duration = 700;
    const start = performance.now();
    let frame;

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      setCurrent(Math.round(target * progress));
      if (progress < 1) frame = requestAnimationFrame(tick);
    }

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  return current.toLocaleString();
}

function AIStats() {
  const [stats, setStats] = useState(fallbackStats);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    getStats()
      .then((data) => {
        if (!active) return;
        setStats({ ...fallbackStats, ...data });
      })
      .catch(() => {
        if (active) setStats(fallbackStats);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const cards = useMemo(
    () => [
      {
        title: "Videos Processed",
        value: stats.videos_processed,
        icon: Video,
        tone: "primary",
      },
      {
        title: "Audio Files",
        value: stats.audio_files,
        icon: FileAudio,
        tone: "secondary",
      },
      {
        title: "Questions Asked",
        value: stats.questions_asked,
        icon: MessageSquareText,
        tone: "accent",
      },
      {
        title: "Summaries Generated",
        value: stats.summaries_generated,
        icon: FileText,
        tone: "soft",
      },
    ],
    [stats]
  );

  return (
    <section className="grid gap-4">
      <div>
        <p className="text-sm font-semibold text-[var(--accent)]">Insights</p>
        <h2 className="mt-1 text-2xl font-bold text-white">AI Statistics</h2>
      </div>
      <LazyMotion features={domAnimation}>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {cards.map(({ title, value, icon: Icon, tone }, index) => (
            <m.div
              key={title}
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, delay: index * 0.08 }}
              whileHover={{ scale: 1.04, y: -4 }}
              className={`stat-card stat-card-${tone} group relative overflow-hidden rounded-2xl border border-white/10 bg-black/40 p-5 shadow-xl backdrop-blur transition-all duration-300 hover:shadow-2xl`}
            >
              <div className="stat-card-gradient absolute inset-x-0 top-0 h-1" />
              <div className="stat-card-glow absolute -right-8 -top-8 size-28 rounded-full opacity-20 blur-2xl transition-opacity duration-300 group-hover:opacity-35" />
              <div className="relative flex items-start justify-between gap-4">
                <span className="stat-card-icon grid size-12 place-items-center rounded-2xl text-white shadow-xl">
                  <Icon size={22} />
                </span>
                <span className="rounded-full border border-white/10 bg-white/10 px-2 py-1 text-[11px] font-semibold text-zinc-300">
                  Live
                </span>
              </div>
              <div className="relative mt-6">
                <p className="text-sm text-zinc-400">{title}</p>
                <p className="mt-2 text-3xl font-bold text-white">
                  {loading ? <span className="skeleton inline-block h-9 w-20 rounded-lg" /> : <AnimatedNumber value={value} />}
                </p>
              </div>
            </m.div>
          ))}
        </div>
      </LazyMotion>
    </section>
  );
}

export default memo(AIStats);
