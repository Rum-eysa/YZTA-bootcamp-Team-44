import React, { useState } from "react";

export default function AiMatchComponent({ isDark }) {
  const [copied, setCopied] = useState(false);
  const matchScore = 92;

  const handleCopy = () => {
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="mb-16">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2"><span>🧠</span> US-008, 009, 015, 026: AI Eşleştirme Motoru</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className={`p-8 rounded-[2rem] shadow-xl border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <h3 className="text-xl font-bold mb-6">📄 CV ve Hedef İlan</h3>
          <div className="space-y-4">
            <div className={`border-2 border-dashed rounded-2xl p-6 text-center ${isDark ? 'border-slate-600' : 'border-slate-300'}`}>
              <div className="text-3xl mb-2">📁</div>
              <p className="font-semibold">CV.pdf yüklendi</p>
            </div>
            <input type="text" defaultValue="https://linkedin.com/jobs/view/frontend-dev" className={`w-full border rounded-xl px-4 py-3 outline-none ${isDark ? 'bg-slate-900 border-slate-700 text-white' : 'bg-slate-50 border-slate-200'}`} />
            <button className="w-full bg-slate-800 text-white font-bold py-3 rounded-xl shadow-md hover:bg-black transition flex justify-center items-center gap-2">
              <span>⚡</span> AI ile Analiz Et
            </button>
          </div>
        </div>

        <div className="space-y-6">
          <div className={`p-6 rounded-[2rem] shadow-xl border flex items-center justify-between ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div>
              <h3 className="text-lg font-bold">🎯 Ajan Skoru</h3>
              <div className="mt-2 flex gap-2">
                <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-md font-bold">React</span>
                <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-md font-bold">Tailwind</span>
              </div>
            </div>
            <div className="relative w-20 h-20 flex items-center justify-center">
              <span className="absolute text-xl font-black text-green-500">%{matchScore}</span>
            </div>
          </div>

          <div className={`p-6 rounded-[2rem] shadow-xl border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-bold">✍️ Önyazı</h3>
              <button onClick={handleCopy} className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${copied ? 'bg-green-500 text-white' : 'bg-indigo-100 text-indigo-700'}`}>
                {copied ? '✅ Kopyalandı' : '📋 Kopyala'}
              </button>
            </div>
            <div className={`p-3 rounded-xl text-xs leading-relaxed font-serif ${isDark ? 'bg-slate-900 text-slate-300' : 'bg-slate-50 text-slate-700'}`}>
              "Sayın İlgili, Açmış olduğunuz pozisyon ile yakından ilgileniyorum. Geliştirdiğim AI projelerindeki mimarim ile şirketinize değer katabilirim..."
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}