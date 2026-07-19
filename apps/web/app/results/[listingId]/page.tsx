import React from 'react';

export default function ResultsPage({ params }: { params: { listingId: string } }) {
  // Şimdilik test için statik bir skor ve veri belirliyoruz. 
  // İleride bu veri veritabanından (API'den) gelecek.
  const score = 75; 
  const jobTitle = "Frontend Developer";
  const companyName = "Tech Solutions Inc.";
  const seniority = "Mid-Level";

  // Skora göre renk belirleme mantığı (Kabul Kriteri)
  const getScoreColor = (s: number) => {
    if (s <= 40) return 'bg-red-500';
    if (s <= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="container mx-auto max-w-3xl p-6 mt-10">
      <div className="bg-white rounded-2xl shadow-lg p-8 text-center border border-gray-100">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">{jobTitle}</h1>
        <p className="text-gray-500 mb-4">{companyName} • <span className="bg-gray-100 px-2 py-1 rounded text-sm">{seniority}</span></p>
        
        {/* Skor Göstergesi (Score Gauge) */}
        <div className="my-8 flex flex-col items-center">
          <div className="relative w-40 h-40 flex items-center justify-center rounded-full border-4 border-gray-100 shadow-inner">
            <div className={`absolute w-full h-full rounded-full opacity-20 ${getScoreColor(score)}`}></div>
            <span className="text-5xl font-extrabold text-gray-700">{score}</span>
          </div>
          <p className="mt-4 text-gray-600 font-medium">Eşleşme Skoru</p>
        </div>

        {/* Mini Kartlar İskeleti */}
        <div className="grid grid-cols-2 gap-4 mt-6 text-left">
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-700">Required Skills</h3>
            <p className="text-sm text-gray-500">React, TypeScript, Tailwind</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-700">Nice to Have</h3>
            <p className="text-sm text-gray-500">Next.js, GraphQL</p>
          </div>
        </div>
      </div>
    </div>
  );
}