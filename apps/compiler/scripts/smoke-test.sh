#!/bin/sh
set -e

OUT=/tmp/smoke-out
BENCH=/tmp/smoke-bench
mkdir -p "$OUT" "$BENCH"

# Gerçek örnek belge: derleme + PDF doğrulama (süre ölçülmez)
tectonic fixtures/sample.tex --outdir "$OUT"
python3 scripts/validate-pdf.py "$OUT/sample.pdf"
echo "Sample document OK"

# Benchmark: cache ısıt, ardından süre ölç
tectonic fixtures/benchmark.tex --outdir "$BENCH"
rm -f "$BENCH/benchmark.pdf"

START=$(python3 -c "import time; print(time.time())")
tectonic fixtures/benchmark.tex --outdir "$BENCH"
END=$(python3 -c "import time; print(time.time())")

python3 scripts/validate-pdf.py "$BENCH/benchmark.pdf"

ELAPSED_MS=$(python3 -c "print(int(($END - $START) * 1000))")
echo "Compile time: ${ELAPSED_MS}ms"

if [ "$ELAPSED_MS" -ge 5000 ]; then
  echo "FAIL: compile exceeded 5s (${ELAPSED_MS}ms)"
  exit 1
fi

echo "Smoke test passed"
