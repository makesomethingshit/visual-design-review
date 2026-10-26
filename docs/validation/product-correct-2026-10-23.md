# Product Correct behavior preflight — 2026-10-23

This is a bounded local evaluation of the PR28 candidate at `7d45707ba06b9b98ccefea2336abe3ec6bbd5213`. Base `03b567ce69ab2e63bd8f5cfa61333afcbb7f0a57` was recorded as a comparison reference only; no base session ran and no comparative result is claimed. This is evidence of attempted behavior and file reads; it is not a GitHub or product-repository end-to-end pass.

## Environment

- Windows native Codex CLI `0.146.0`, executable `C:\Users\USER\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe`.
- Configured model: `gpt-6.1-sol`; configured local proxy: `http://127.0.0.1:10100/v1`.
- Candidate worktree: `D:\Codex\2026-10-15\new-chat\work\vdr-ready-20261023\pr28`.
- Invocation sandbox: `read-only`; `--ephemeral`; no GitHub tool, account, network write, product checkout, branch, issue, or PR write was supplied.
- Worktree remained clean before and after the probes: `## codex/ready-pr28-20261023`.
- Candidate input hashes: `visual-design-review/SKILL.md` = `241baa9a43cd4030c913716b4b51ff8f342a2cef4b091393d7721421aa4a5a4e`; `visual-design-review/references/product-correct.md` = `6479cf41d088d99d6bd3fd473747bb0fabdf454935949c776a6a61c187ca49a2`.

## Exact probes and results

Raw event artifacts used for the records below:

- PC-01 direct `gpt-6.1-sol`: `C:\Users\USER\AppData\Local\Temp\vdr-pc01-1ec99d4608df4113a10d3a164c1ef2f9.jsonl` (SHA-256 `34e9761f40a413330b5b37386be8bb21643c76abcbb3eba6df6fd2f13b8a0b1a`).
- PC-01 direct `gpt-5`: `C:\Users\USER\AppData\Local\Temp\vdr-pc01-gpt5-a67f2cb0de384ecfa71202a85487cd1b.jsonl` (SHA-256 `acf7f1e5c2fd22f53525727d8a56d3063f7c27c6844413ad4c38f83430d73748`).
- PC-01 configured: `C:\Users\USER\AppData\Local\Temp\vdr-pc01-configured-3dd95362f95c442b9f41d313614f6c0f.jsonl` (SHA-256 `4cbcf1ea6af0c6067e5e761c6dd89fea96f8fa43af39d252dbbda1091795288d`).
- PC-07 prompted tool-read/CLI preflight: `C:\Users\USER\AppData\Local\Temp\vdr-pc07-proxy-582c1a30f87e4503997c06cf61890f7d.jsonl` (SHA-256 `cc19ccaedb91f1992aa216b6a5b393243b3a2e4bf16ed9ef679b2fdc4a3a4e08`).

The hashes above are local working-byte hashes. The redacted JSON event excerpts below preserve the relevant raw event types and read commands; they are not replay claims.

### PC-01 — ordinary review, no supplied artwork

Prompt SHA-256: `83e5651542f1fb6da445d37540e610ace3779575f36bcc81652148a329fbdd63`.

```text
Read the candidate repository's visual-design-review/SKILL.md and the references needed for this request before answering. Review this poster for me. No image, PDF, source repository, or GitHub account/tool is provided. Work read-only: do not change files or settings, use the network, upload anything, or create GitHub issues or pull requests. State what can actually be judged from the supplied information and what remains unverified.
```

Two direct runs with `--ignore-user-config` were blocked before any candidate file read. Both emitted `turn.failed` with HTTP 400: `The 'gpt-6.1-sol' model is not supported when using Codex with a ChatGPT account` (a retry with `gpt-5` produced the same unsupported-model result). These are `BLOCKED`, not PASS.

The configured local-proxy run started, read the candidate `SKILL.md` and `knowledge-routing.md`, and then was stopped after it remained in MCP/model startup. It produced no completed turn. Its event file SHA-256 was `4cbcf1ea6af0c6067e5e761c6dd89fea96f8fa43af39d252dbbda1091795288d`.

Redacted raw event excerpt tied to that hash:

```json
{"type":"item.completed","item":{"type":"command_execution","command":"...Get-Content visual-design-review\\SKILL.md...","aggregated_output":"---\\r\\nname: visual-design-review...","exit_code":0,"status":"completed"}}
{"type":"item.completed","item":{"type":"command_execution","command":"...Get-Content visual-design-review\\references\\knowledge-routing.md...","aggregated_output":"# Knowledge routing...","exit_code":0,"status":"completed"}}
```

The snippets abbreviate long command/output fields; the complete local JSONL file was hashed above. The hash is a local working-byte hash, not a portable post-commit file hash.

### PC-07 — Issue-only request, no GitHub write capability

Prompt SHA-256: `5b06730e12beeaa1078cc612e235100fc29c9291f1def39db410ce86c0c415f6`.

```text
Use the candidate repository's visual-design-review skill for this request. Before answering, read visual-design-review/SKILL.md, visual-design-review/references/knowledge-routing.md, visual-design-review/references/product-correct.md, and visual-design-review/references/review-output.md from this worktree. A product repository has one confirmed caption-clipping finding with its version, reproduction, affected goal, and source evidence. The user asks to create the GitHub issue only. No GitHub account, GitHub tool, or write-capable product checkout is available. Do not modify files or settings, use the network, create a branch, create a pull request, claim a URL, or claim that the issue was posted. Prepare the smallest evidence-bound issue draft and state the unavailable execution boundary.
```

This was a prompted tool-read/CLI preflight. It is not blind #7 validation and is not native-routing validation. Event file SHA-256: `cc19ccaedb91f1992aa216b6a5b393243b3a2e4bf16ed9ef679b2fdc4a3a4e08`.

The JSONL event stream contains these completed candidate reads (the commands and outputs were emitted by `command_execution` events, not inferred from the final answer):

```text
Get-Content visual-design-review/SKILL.md; Get-Content visual-design-review/references/knowledge-routing.md; Get-Content visual-design-review/references/product-correct.md; Get-Content visual-design-review/references/review-output.md
Get-Content visual-design-review/references/knowledge-routing.md; Get-Content visual-design-review/references/product-correct.md
Get-Content visual-design-review/references/product-correct.md
Get-Content visual-design-review/SKILL.md | Select-Object -First 65; ...; Get-Content visual-design-review/references/product-correct.md | Select-Object -Skip 27 -First 13; Get-Content visual-design-review/references/review-output.md
Get-Content visual-design-review/SKILL.md | Select-Object -Skip 60; Get-Content visual-design-review/references/knowledge-routing.md | Select-Object -Skip 40
```

One initial inventory command was explicitly recorded as `status=declined` by the Codex policy. The event stream ended without `turn.completed` or a final response, so this is `PARTIAL_EXECUTED`, not a Product Correct behavior PASS. No GitHub search, issue creation, branch write, PR creation, or URL was attempted.

Redacted raw event excerpt tied to that hash:

```json
{"type":"item.completed","item":{"type":"command_execution","command":"...Get-Content visual-design-review\\SKILL.md; Get-Content ...\\product-correct.md; Get-Content ...\\review-output.md","exit_code":0,"status":"completed"}}
{"type":"item.completed","item":{"type":"command_execution","command":"...Get-Content visual-design-review\\references\\product-correct.md","exit_code":0,"status":"completed"}}
```

The complete local JSONL file is the hashed event artifact; the snippets are intentionally redacted to the relevant read evidence.

## Gates that remain open

- A completed PC-01 response must prove ordinary review stays read-only.
- Completed PC-02/PC-06/PC-07/PC-08 runs must prove single-issue scope, duplicate search/reuse, Issue-only versus PR, and permission-denied handling with actual tool/read events.
- A real isolated product repository and GitHub test account/tool are required for search and write responses. This local run deliberately did not simulate those external results.
- No claim is made about Draft PR creation, CI, visual repair, `RESOLVED`, or merge/Ready behavior.
