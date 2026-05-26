import React from "react";
import { AlertTriangle } from "lucide-react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error) {
    console.error("EchoGPT UI error", error);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div className="grid min-h-screen place-items-center bg-black p-4 text-zinc-100">
        <div className="glass-card max-w-md p-6 text-center">
          <span className="mx-auto mb-4 grid size-12 place-items-center rounded-2xl bg-red-500/15 text-red-200">
            <AlertTriangle size={22} />
          </span>
          <h1 className="text-xl font-semibold text-white">Something went wrong</h1>
          <p className="mt-2 text-sm text-zinc-400">Refresh the page to restore the EchoGPT interface.</p>
          <button className="btn btn-primary mt-5" type="button" onClick={() => window.location.reload()}>
            Reload
          </button>
        </div>
      </div>
    );
  }
}
