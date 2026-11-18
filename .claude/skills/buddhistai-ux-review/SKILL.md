---
name: buddhistai-ux-review
description: Run an EGM Goldfish review of a BuddhistAI design document with EGM's own reviewers plus BuddhistAI user personas. Use before building any change that users see (pages, forms, install steps, site or app UI).
---

# BuddhistAI UX review

Source of truth: BuddhistAI/knowledge-base. Copies of this skill in other repos must match it.

Needs the EGM plugin (`claude plugin marketplace add google/elephant-goldfish-model`, then `claude plugin install egm@egm`). The repo's `.claude/settings.json` offers it. If your session cannot start fresh subagents, stop: a review in the same context is not a Goldfish review.

## 1. Get the persona files

In the knowledge-base repo, use `ux/` as it is. In any other repo, download these files from `https://raw.githubusercontent.com/BuddhistAI/knowledge-base/main/` into `.egm-context/` (it is in `.gitignore`), keeping the paths:

- `ux/personas/translator.md`, `project-lead.md`, `funder.md`, `skill-builder.md`, `benchmark-publisher.md`
- `ux/journeys/*.md` (the five journey files listed in `ux/README.md`)
- `ux/standards/journey-standard.md`

## 2. Choose the reviewers

Read the design's `journeys` field. Use the persona reviewers of each journey, plus EGM's built-in reviewers:

| Journey | Persona reviewers | EGM reviewer |
| --- | --- | --- |
| find-and-use-a-skill | translator, project-lead | `comprehension` |
| share-know-how | translator, skill-builder | `comprehension` |
| get-measured | skill-builder | `implementation_readiness` |
| share-a-benchmark | benchmark-publisher | `structural` |
| understand-the-field | funder | `zoom_out` |

Always add `design_critic`. Map every persona reviewer to the standard `ux/standards/journey-standard.md`. Map EGM reviewers to their usual EGM standards.

## 3. Run the EGM review loop

Read the EGM `egm-review-loop` skill (`${CLAUDE_PLUGIN_ROOT}/skills/egm-review-loop/SKILL.md`) and follow it, with these inputs:

- `TargetFile`: the design document.
- `SemanticTarget`: `full file`.
- `Reviewers`: the EGM shortnames plus the persona file paths (a path with a `/` is read as a custom reviewer).
- `Standards`: as in step 2.
- `GoldfishContext`: the journey files the design names, and the current page files or URLs it changes (save each URL as a local file first).

Tell each persona reviewer to use Mode REVIEW. The loop stops after two clean rounds in a row (no open Blocker or Major finding) or after 5 rounds.

## 4. Record the result

Fill in the design's "Goldfish review" section: date, reviewers that ran, open findings and accepted risks. Set `state: reviewed`. Put a one-line summary in the pull request under "EGM review".
