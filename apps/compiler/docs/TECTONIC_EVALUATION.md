# Tectonic LaTeX Pipeline — Risk ve Karar

## Özet

**Karar: Tectonic birincil, XeLaTeX fallback ikincil derleyici.** Basit belgeler Tectonic ile hızlı derlenir; AltaCV gibi karmaşık şablonlarda Tectonic başarısız olursa aynı container içinde XeLaTeX devreye girer.

## Ölçülen Kriterler

| Kriter | Hedef | Durum |
|--------|-------|-------|
| Docker image build | Başarılı | `apps/compiler/Dockerfile` |
| Derleme süresi (warm cache) | < 5s | `scripts/smoke-test.sh` |
| PDF doğrulama | Geçerli PDF | `scripts/validate-pdf.py` |
| Hata yönetimi | Anlamlı stderr | `422` + `invalid.tex` testi |
| Çoklu dosya | `.cls`, `.bib`, görseller | `POST /compile` multi-file |

## Riskler

| Risk | Etki | Azaltma |
|------|------|---------|
| Resmi Docker image yok | Bakım yükü | Pinned binary (v0.16.9) + multi-arch Dockerfile |
| Bundle indirme (network) | Cold start yavaş | Build-time cache priming + `compiler_cache` volume |
| AltaCV / pdfx | Tectonic SIGSEGV | Otomatik XeLaTeX fallback |
| Untrusted `.tex` input | TeX shell escape | İzole container, non-root user, timeout |
| Image boyutu | TeX Live paketleri | Yalnızca gerekli texlive paketleri |

## Karar Matrisi

| Kriter | Tectonic | Tectonic + XeLaTeX fallback | Pandoc |
|--------|----------|----------------------------|--------|
| Image boyutu | ~150MB | ~800MB | ~500MB |
| Basit belge hızı | Yüksek | Yüksek (Tectonic) | Orta |
| AltaCV uyumu | Düşük | Yüksek | Düşük |
| Bakım | Orta | Orta | Düşük |

## Fallback Stratejisi

1. Tectonic dene (hızlı, reproducible)
2. Başarısız olursa XeLaTeX + biber (AltaCV, custom `.cls`)
3. Her iki engine de başarısız → `422` + birleşik stderr
