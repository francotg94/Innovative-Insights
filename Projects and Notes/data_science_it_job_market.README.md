data_science_it_job_market.html — quick notes

- Location: Projects and Notes/data_science_it_job_market.html
- Purpose: Interactive Plotly chart showing average salary by role over time. Bubble size approximates job openings.
- Research Scientist bubble: intentionally enlarged via roleSizeMultiplier = { 'Research Scientist': 4.0 } in the file.

How to open

- Open the file in any modern browser (double-click or use `open` on macOS):
  open "Projects and Notes/data_science_it_job_market.html"

Notes / next steps

- Replace the sample dataset with your real CSV/JSON. See the `sampleData` array at the top of the script.
- If you want different bubble scaling, edit `roleSizeMultiplier` or adjust the `baseSizes` calculation in `buildTraces()`.
- I validated the HTML structure locally (xmllint) and committed the cleaned file.
