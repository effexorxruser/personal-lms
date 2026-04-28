# Block 1 Source Usage Note

## Sources used

Block 1 enrichment uses only approved source ids:

- `python-docs`
- `automate-boring-stuff`
- `python-mooc`

## Cached snapshots

Fetch/cache commands were executed:

- `.venv/bin/python scripts/fetch_source.py --source-id python-docs --section all`
- `.venv/bin/python scripts/fetch_source.py --source-id automate-boring-stuff --section all`
- `.venv/bin/python scripts/fetch_source.py --source-id python-mooc --section all`

Result: target pages returned `403 Forbidden` in this environment, so snapshot text was not saved as `ok` entries.
Manifest still records retrieval attempts and errors for traceability.

## Direct web/MCP usage

- No live MCP retrieval was used for Block 1 enrichment pass.
- No external API/LLM generation was used in this pass.
- Lesson enrichment was done from approved source metadata, canonical/preferred sections, and existing pedagogical constraints.

## How sources were transformed into LMS lessons

Sources were used as backbone, then transformed into self-contained LMS content:

- Russian-first explanations of core ideas;
- runnable Python code examples inside lessons;
- command snippets + expected output;
- frequent beginner mistakes blocks;
- explicit bridge from theory to action/task;
- practical technical glossary in each lesson.

## What remains optional deep dive

External links are kept only under `What to read (EN source)` as optional deep-dive references.

They are not required steps for lesson completion and do not replace in-LMS explanation.

## No manual source hunting policy

Block 1 lessons follow no-manual-hunting policy:

- learner is not asked to leave LMS to understand core material;
- source links are optional support, not mandatory path;
- completion criteria are executable inside the LMS learning flow.
