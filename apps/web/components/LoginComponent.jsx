import React from "react";

export default function LoginComponent() {
  return (
    <section className="mb-16">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2"><span>🔐</span> US-007: Modern Login & Register</h2>
      <div className="relative rounded-[2rem] overflow-hidden shadow-2xl bg-slate-900 py-12 px-6 border border-slate-800">
        <div className="absolute inset-0 bg-indigo-900 opacity-20 blur-xl"></div>
        <div className="relative z-10 max-w-sm mx-auto bg-white/10 backdrop-blur-xl border border-white/20 p-8 rounded-3xl shadow-2xl">
          <h3 className="text-2xl font-bold text-white text-center mb-6">Sisteme Giriş</h3>
          <div className="space-y-4">
            <input type="email" placeholder="E-posta" className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/50 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
            <input type="password" placeholder="Şifre" className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/50 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
            <button className="w-full bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-bold py-3 rounded-xl shadow-lg transform transition hover:scale-[1.02]">
              Giriş Yap
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}