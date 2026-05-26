export function Panel({ children, className = "" }) {
  return <section className={`panel ${className}`}>{children}</section>;
}

export function Button({ children, className = "", variant = "primary", ...props }) {
  return (
    <button className={`btn btn-${variant} ${className}`} {...props}>
      {children}
    </button>
  );
}

export function Field({ label, children }) {
  return (
    <label className="grid gap-2 text-sm text-zinc-300">
      <span>{label}</span>
      {children}
    </label>
  );
}

export function FadeIn({ children, delay = 0, className = "" }) {
  return (
    <div className={`fade-in ${className}`} style={{ animationDelay: `${delay}s` }}>
      {children}
    </div>
  );
}
