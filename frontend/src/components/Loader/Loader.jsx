export default function Loader({ label = "Processing media" }) {
  return (
    <div className="flex items-center gap-3 text-sm text-zinc-300">
      <span className="typing-loader" />
      {label}
    </div>
  );
}
