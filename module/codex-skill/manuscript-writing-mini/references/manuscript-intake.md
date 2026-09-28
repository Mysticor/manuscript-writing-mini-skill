# Intake contract
Inventory the complete handoff; read central facts, ledgers and limitations first. Read selected bibliography, visual inventories and original assets at use. Treat prose/cards
as navigation, not substitutes for data or original sources. Verify package hashes
when provided; reject paths escaping package root. Preserve original inputs.
Canonical snapshots live in inputs/handoff; map equivalent user file layouts with
--input-map JSON, record mapping, do not invent missing files. The map's keys are
canonical filenames and values are relative source paths. A legacy handoff without
optional visual inventories is allowed and recorded as MISSING_BUT_NONBLOCKING.

Audit: actual research, strongest real result, supported vs bounded claims, failed
hypotheses, actual method/data/stats, assets/candidate literature visuals, journal
and blockers. Classify every missing item as AVAILABLE, MISSING_BUT_NONBLOCKING,
AUTHOR_INPUT_NEEDED or BLOCKING. A missing central result blocks Results and final
readiness; continue only independent planning/grounded sections. Do not redesign
experiments or silently relabel planning hypotheses as findings. Explain a required
Stage 1 return for substantive missing evidence, without automatically switching.
Intake scripts check source/result links and IDs; Agent must understand core facts and actually verify each selected source at use. Test-only/blocked upstream readiness cannot be used as production evidence.


## Literature evidence schema v2
The authoritative schema is research-planning/references/literature-evidence-schema.json
(resolve through the installed research-planning Skill). Consume the existing three
literature_*_inventory.csv files directly; do not create parallel renamed inventories.
local_pdf_path is the original, asset_path the internal reader copy;
structured_data_path is a reliably transcribed table. All resolve relative to the
handoff root. source_pointer/source_block_id retain original figure/panel/page context.
importance=REFERENCE_ONLY/CANDIDATE/KEY_VISUAL is Stage 1 triage, not final selection.
POSSIBLE_REPRODUCED/POSSIBLE_ADAPTED/POSSIBLE_SYNTHESIS_SOURCE remain provisional.
PREPARED_SOURCE_INDEX or LEGACY_NEEDS_ENRICHMENT is never Stage 2 VERIFIED.
Choose candidates using role/claim/relevance, then reopen originals and write new
source_verification records. Unknown licence, unavailable full text or unreliable
transcription must remain explicit. Never infer publication permission from a crop.
Older minimal inventories remain readable; Stage 1 export normalizes their aliases.
