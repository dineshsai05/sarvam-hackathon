# Knowledge base files

Put the source documents here, then upload them in the Sarvam dashboard:
**Workspace → Knowledge base → Create** (formats: PDF, DOCX, CSV/TSV, TXT, MD). Ingestion is
asynchronous; wait for it to finish before attaching the KB to the agent.

There is no public API for knowledge bases in the Voice Agents API reference, so uploads are
dashboard-only. Keep this folder as the source of truth and re-upload when files change.

## Suggested KBs (one coherent KB routes better than one big mixed KB)

| KB name | Description to enter in the dashboard (the agent routes on this) | Files |
|---|---|---|
| Private car insurance policies (India) | Policy wordings, brochures, coverage, exclusions, IDV, deductibles, claim process and add-ons for private-car motor insurance from ICICI Lombard, HDFC ERGO, Bajaj Allianz, Tata AIG, Acko, etc. Search this for any question about what a specific policy covers or excludes. | `policies/<insurer>_<product>.pdf` |
| Motor insurance basics (India) | Plain-language explainers: third-party vs own-damage vs comprehensive, NCB, IDV, zero depreciation, engine protect, RSA, consumables cover, IRDAI rules on third-party premiums. Search this for general "what is / is it worth it" questions. | `basics/*.md` |
| Sample premiums | Indicative annual premiums by car segment, age and cover type, clearly labelled as samples, plus a short note that live quotes come from insurer APIs. | `premiums/sample_premiums.csv` |

Tips from the Sarvam KB docs: lead with a specific description, keep each KB coherent, and prefer
reference content (no customer data). Retrieval returns the top ~500-token chunks tagged with the
source file, so short, well-headed documents work better than one 200-page PDF.
