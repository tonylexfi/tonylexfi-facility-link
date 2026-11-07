# Facility Link Resolver

Link facility records with exact keys while explicitly abstaining on ambiguous or conflicting matches.

An original task authored for tonylexfi's COMP 480/580 milestone. The case data and task logic were created for this package; no Empiric/Federico task implementation was copied. The MCP packaging scaffold follows [NanoAgent](https://github.com/RUSH-LAB/nanoagent). All observations are synthetic fixtures, not live research.

## Tools

| Tool | Input / output | Purpose |
|---|---|---|
| `read_case` | `CaseInput` / `DataOutput` | Read a typed immutable case |
| `write_result` | `AnswerInput` / `ResultOutput` | Save the complete proposed answer |
| `reference` | `CaseInput` / `ReferenceOutput` | Hidden pinned snapshot, unavailable to the agent |

Task `tonylexfi-facility-link` uses the `agent` runner and the first two tools. Task types are `CaseInput` and `ResultOutput`. The reference tool runs before the model. Every shape is declared in `contract.py`.

### Exact success rules

Match each incoming record, sorted by id. If site_key is nonempty, match that key exactly; do not fall back to name/address if it is unknown. Otherwise all name_key/address_key/zip_code must be nonempty and equal to the registry strings exactly. One match => return its id and method site_key or composite. Multiple matches => facility_id null, method ambiguous. Zero => null, unmatched. Do not trim, casefold, fuzzy-match or convert ZIP to a number; the keys are already prepared.

The verifier checks the actual `result.json`, its submitted path/count and the pinned reference. It computes the required answer in pure Python and compares exact JSON values. All rows and summary values must match; duplicates, missing rows, extra properties, and Boolean/integer substitutions fail. The score is 1 only for complete success, otherwise 0. No LLM is used as a judge.

## Layout

`nanoagent.yaml` declares the runtime, permissions and task. `contract.py` declares all typed inputs/outputs. `src/plugin/` serves the tools and includes fixtures. `verifier/` contains pure deterministic checks. `tests/` contains executable tests, task inputs and hand-written gold answers. `ui/` uses the standard schema renderer; `product/` describes the plugin. Run logs and report evidence are kept outside this repository.

## Develop and run

Requires Python 3.12 or newer, Git and uv. Install a NanoAgent version supporting `nanoagent.plugin/v0001` (validated with 0.7.0 at framework commit 57714f6).

```bash
uv sync --locked --extra dev
uv run --offline pytest -q
uv run --offline ruff check .
uv lock --check --offline
nanoagent plugin inspect .
```

First installation downloads locked dependencies; all plugin tools and tests subsequently work offline. The runtime is `uv run --frozen python -m plugin` and NanoAgent supplies `NANOAGENT_WORKSPACE`. Choose `{"case":"standard"}` or `{"case":"boundary"}` in RUSH Lab. The model ends with a structured submit of the path and count returned by write_result.

For a local model run, use `tests/run_agent.sh standard` after exporting `OPENROUTER_API_KEY`. The key is used by the harness, never by a plugin tool. The script defaults to the course model and writes evidence to a folder outside the repository. See its documented environment variables before changing the model.

### Tests and limitations

Tests include correct and boundary gold answers, wrong decisions with correct counts, duplicate rows, missing output/reference/files, mismatched cases, malformed JSON and contracts, extra properties, traversal paths, symlinks and type-sensitive equality. The verifier is run twice by the NanoAgent sandbox to enforce determinism.

The benchmark assumes prepared keys and an authoritative site-id namespace. It does not perform fuzzy matching, entity normalization or legal-entity resolution. A unique exact composite can still conflate real facilities if the supplied registry is wrong.

The fixtures make the task reproducible, not representative of every real data problem. Model trajectories need not be deterministic even when the verdict is. This package neither publishes a dataset nor executes changes against a real system.
