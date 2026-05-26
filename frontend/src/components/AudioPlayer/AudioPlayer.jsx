export default function AudioPlayer({ src }) {
  return (
    <audio className="w-full" controls src={src}>
      <track kind="captions" />
    </audio>
  );
}
