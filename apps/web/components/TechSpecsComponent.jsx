import React from "react";

export default function TechSpecsComponent({ isDark }) {
  return (
    <section className="mb-16">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2"><span>🚀</span> US-030, 036: Performans & Testler</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        <div className={`p-6 rounded-[2rem] shadow-xl border font-mono text-sm overflow-hidden ${isDark ? 'bg-slate-900 border-slate-700' : 'bg-black border-slate-800'} text-slate-300`}>
           <div className="flex items-center justify-between mb-4 pb-4 border-b border-slate-800">
             <span className="text-slate-400">Cypress E2E (US-030)</span>
             <span className="text-green-500 font-bold">4 Passing</span>
           </div>
           <ul className="space-y-3 text-xs">
             <li className="flex items-center gap-2"><span className="text-green-500">✓</span> Kullanıcı girişi başarılı (1.2s)</li>
             <li className="flex items-center gap-2"><span className="text-green-500">✓</span> Form doğrulamaları (0.8s)</li>
             <li className="flex items-center gap-2"><span className="text-green-500">✓</span> API analiz isteği (2.1s)</li>
             <li className="flex items-center gap-2"><span className="text-green-500">✓</span> UI sonucu çizdi (0.4s)</li>
           </ul>
        </div>

        <div className={`p-8 rounded-[2rem] shadow-xl border flex flex-col justify-center items-center ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <h3 className="text-lg font-bold mb-6 text-center w-full">Lighthouse Skoru</h3>
          <div className="flex gap-4 sm:gap-8 justify-center w-full">
            {[{ label: "Performans", score: 98 }, { label: "Erişilebilirlik", score: 100 }, { label: "Best Practice", score: 100 }, { label: "SEO", score: 100 }].map((item, idx) => (
              <div key={idx} className="flex flex-col items-center gap-2">
                <div className="w-14 h-14 rounded-full border-4 border-green-500 flex items-center justify-center text-green-600 font-bold text-sm bg-green-50">
                  {item.score}
                </div>
                <span className={`text-[10px] font-bold text-center w-16 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{item.label}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
}