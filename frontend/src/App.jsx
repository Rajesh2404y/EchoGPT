import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar/Navbar";
import Sidebar from "./components/Sidebar/Sidebar";
import Loader from "./components/Loader/Loader";
import { AppProvider } from "./context/AppContext";

const Home = lazy(() => import("./pages/Home"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Chat = lazy(() => import("./pages/Chat"));
const History = lazy(() => import("./pages/History"));
const Settings = lazy(() => import("./pages/Settings"));
const Upload = lazy(() => import("./pages/Upload"));

export default function App() {
  return (
    <AppProvider>
      <div className="app-shell text-zinc-100 transition-colors duration-300">
        <Navbar />
        <div className="app-body mx-auto grid max-w-7xl grid-cols-1 md:grid-cols-[240px_1fr]">
          <Sidebar />
          <main className="app-main">
            <Suspense fallback={<div className="grid min-h-[420px] place-items-center"><Loader label="Loading EchoGPT" /></div>}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/upload" element={<Upload />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/chat/:chatId" element={<Chat />} />
                <Route path="/history" element={<History />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Suspense>
          </main>
        </div>
      </div>
    </AppProvider>
  );
}
