import Chat from "@/components/Chat";

export default function Home() {
  return (
    <main className="flex h-screen flex-col bg-zinc-950 text-white selection:bg-blue-500/30">
      <header className="py-6 px-8 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
          Enterprise Knowledge Mesh
        </h1>
        <p className="text-zinc-400 text-sm mt-1">Multi-Agent Orchestration UI</p>
      </header>
      
      <section className="flex-1 p-6 overflow-hidden">
        <Chat />
      </section>
    </main>
  );
}
