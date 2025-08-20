#!/usr/bin/env bash
# Quick smoke check: ensure required HTML elements exist
FILE="Projects and Notes/data_science_it_job_market.html"
for id in roleSelect chart csvFile loadCsvBtn applyBtn resetBtn downloadCsv; do
  if ! grep -q "id=\"$id\"" "$FILE"; then
    echo "MISSING: $id"
    exit 2
  fi
done
echo "SMOKE OK"
exit 0
