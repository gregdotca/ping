---
rating: B2b
spec: "0.1"
updated: 2026-10-11
---

# AI Code Rating

**ACR B2b** (Maintainer: Experienced · AI Share: 26–50% · Oversight: Reviewed)

This project is rated with [AI Code Rating](https://aicoderating.com/spec/0.1/), spec version 0.1.

## How AI Was Used

The maintainer wrote the original app, template, and Docker setup without AI. Later changes were made with an AI coding agent: escaping user input in the ping results, closing an open redirect, no longer pinging visitors' own IPs on their first visit, a clearer message for IPv6 addresses, dependency updates and pins, building the Tailwind and daisyUI CSS in the Docker image instead of loading it from a CDN, automatic dark mode, and an accessible label for the address field. The maintainer decided on each change, read the full diff before committing it, and tested the deployed site. The agent also wrote the documentation.

The AI's changes are also reviewed by a second AI, Codex, and the two go back and forth until Codex doesn't find any more issues. This review doesn't change the oversight level. Commits where the AI changed code are marked with `Co-Authored-By: Claude Code`, and commits Codex reviewed are marked with `Reviewed-By: Codex`.
