# F1–F3 follow-up verification

2026-10-18. This record supersedes the earlier **unexecuted** final-gate/routing status,
not its historical raw results. The original 52 records remain unchanged.

## Changes and execution sequence
C and J expected_decisions now explicitly reject unsupported severity, including
Minor when impact itself is unverified. F/G remain true-positive controls. Expectations
were not supplied to the reviewed model.

Three separate frozen prompt snapshots and their raw records are retained:

| Batch | Snapshot | Raw records | Outcome |
| --- | --- | --- | --- |
| First final-file replay | [followup](followup/tested-instructions.txt) | [20 runs](followup/runs.jsonl) | C-1 repeats unsupported Major; J-1/J-2 assign unsupported Minor |
| Classification-sequence correction | [recheck](recheck/tested-instructions.txt) | [20 runs](recheck/runs.jsonl) | C both conditional; J-1 still assigns Minor to a newly assumed task |
| Provided-goal evidence gate | [verified](verified/tested-instructions.txt) | [20 runs](verified/runs.jsonl) | C/J conditional in both repeats; F/G defects detected in both repeats |

The correction removes the example's Major anchor and makes finding construction
explicit: observed difference → evidence of loss against a provided goal/constraint →
severity. A hypothetical better task is not evidence of failure; Probable/Hypothesis
cannot supply missing impact evidence. Confirmed document/production failures remain
Defects without requiring a separate audience experiment. No example-specific aesthetic
exception, dependency, numeric standard, or automatic upload was added.

Each batch has its own cases and prompt-template JSON. Exact inputs can be reconstructed
as documented in [evaluation replay](README.md). Behavioral runs inject that batch's
snapshot; native routing uses the installed skill. Same requested model `gpt-6.1-sol`,
medium reasoning, CLI `0.163.0-alpha.10.2`, fresh ephemeral read-only sessions.
Internal model revision/seed remains unexposed.

## F1: final behavioral replay
Final run IDs use `verified-behavior-<case>-<repeat>`, repeat 1 and 2.

| Case | Observed result | Judgment |
| --- | --- | --- |
| C | Interpretation / Exploratory / Hypothesis; no confirmed Minor/Major/Critical from missing image/legend/impact | Impact gate passes twice |
| J | A/B/C conditional exploration; placeholder content and fictional history not turned into defects; D limited to visible board | Impact gate passes twice |
| F | Wrong approved event date identified as Defect in both; intent does not excuse it | Defect retention passes twice |
| G | 120 PPI against required 240 PPI identified as Defect in both; RGB accepted, physical appearance unverified | Defect retention passes twice |

Main reviewer read all eight raw responses. A separate read-only agent also compared all
eight with the cases and synthetic PNG; no writes, new model executions, or network
access were delegated. Its adjudication agrees on these scoped outcomes. This is an
agent-assisted judgment, not a human-user study or proof of general quality improvement.
A further read-only report-consistency audit was stopped without a final response;
it adds no validation evidence.

Remaining differences: F uses Major in repeat 1 and Critical in repeat 2. Detection is
stable, exact severity is not. Both G responses distinguish RGB compliance from visual
Strength. This is a scoped regression pass, not an all-quality pass; raw outputs remain
unchanged. Final behavior was not rerun across
A/B/D/E/H/I in this follow-up; their earlier records remain the evidence for those cases.

## F2: stricter regression expectations
The root [cases.json](cases.json) and batch copies explicitly reject unsupported Major
in C and unsupported Minor or higher for B/C in J when actual target loss is absent.
They also require distinguishing visible sign differences from actual reading loss.
F/G retain their confirmed-error controls. Expected decisions are evaluator data,
not included in the model prompts. Per-record prompt hashes are reproducible from the
saved templates, snapshots and case input.

## F3: actual Codex discovery and file reads
Final IDs use `verified-routing-R<case>-<repeat>`.

| Route | 2-run observation | Judgment |
| --- | --- | --- |
| R1 explicit skill mention | SKILL.md + review-protocol.md actually read | Pass 2/2 |
| R2 natural poster critique | SKILL.md + review-protocol.md actually read | Pass 2/2 |
| R3 natural editorial critique | SKILL.md + review-protocol + composition/typography/editorial refs actually read | Pass 2/2 |
| R4 CSS syntax review | No target-skill read events; answer stays on CSS behavior | Pass 2/2 |
| R5 UI accessibility review | No target-skill read events; answer stays on accessible button name | Pass 2/2 |
| R6 code review | No target-skill read events; answer stays on Python error behavior | Pass 2/2 |

This is native skill discovery, not injected instructions. The common suffix only permits
reading a relevant skill and preserves read-only/no-network constraints; it does not name
which skill to choose. R1 alone explicitly names the skill. Windows sandbox is specified
as `unelevated` per invocation; no user configuration was edited. That override and UTF-8
fallback differ from the earlier failed probe, so no single root cause is inferred.

Initial PowerShell reads garbled Korean. Models then actually executed Python JSON reads
with ensure_ascii encoding. Those successful exit-0 read events decode to the final
installed files exactly. [Read evidence](verified/read-evidence.jsonl) preserves tool event
status and decoded file contents without local absolute paths. Record-level decoded
file hashes match the frozen source and final installation. Successful declarations alone
are not counted. In negative routes, both the full local command trace and final answer
were checked; lack of a target read alone does not prove all internal model routing state.
No claim is made about every natural phrase or every machine configuration.

Interim native batches overlapped installation updates. Their end-of-run hashes are
explicitly not native snapshot evidence. Use the final frozen verified batch for F3.
The original full local CLI event logs remain scratch material; public read-evidence is a
content-preserving projection of the successful document-read events, not full telemetry.

## Real usage supplied by the user
The supplied shared ChatGPT session was read in the browser. It confirms repeated use
and offers qualitative examples relevant to severity calibration. Its source images,
internal skill-load traces, and exact installed revision were not verified here. It is
not counted as a controlled routing or comparative trial. Neither that conversation nor
user artwork/links are copied into this public package.

## Scope of completion
F1's final severity regression, F2's expectation gap, and F3's six fixed routing cases
are covered by inspectable completed runs. Exact severity repeatability, all finding-type
labels, all natural language routing, physical output, and historical correctness are not
certified. Existing baseline results do not establish a general improvement claim.
