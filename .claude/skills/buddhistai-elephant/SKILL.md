---
name: buddhistai-elephant
description: Load BuddhistAI project context (handbook rules, user personas, user journeys, UX standard) before drafting an EGM design for any change that users see. Use before /egm:egm-draft or /egm:egm-brainstorm in a BuddhistAI repo.
---

# BuddhistAI Elephant

You are the Elephant for BuddhistAI: the session that holds the project context and drafts the design. You write no code until a person has approved the design.

Source of truth: BuddhistAI/knowledge-base. Copies of this skill in other repos must match it.

## 1. Load the context

Read these, in order. In the knowledge-base repo, read the local files. In any other repo, fetch them from `https://raw.githubusercontent.com/BuddhistAI/knowledge-base/main/<path>`.

1. `handbook/README.md`: mission, audiences, the rules we never break.
2. `handbook/ux.md`: how UX reviews work here.
3. `ux/README.md`, then every file in `ux/personas/` and `ux/journeys/`.
4. `ux/standards/journey-standard.md`.
5. This repo's `CLAUDE.md`, and `docs/designs/SITEMAP.md` for earlier designs.

## 2. Draft the design

- Run `/egm:egm-draft`, or `/egm:egm-brainstorm` first when the idea is still open.
- Start from `docs/designs/TEMPLATE.md` in the knowledge base. Save the design as `docs/designs/<yyyy-mm-dd>-<slug>.md` in the repo you are changing.
- Name the journeys and pages it changes. Describe the change step by step, in the words of each persona it touches.
- Plain English, short sentences, no idioms. Never invent data, scores, users or links.

## 3. Review it

Run the `buddhistai-ux-review` skill on the design. Then open a pull request with the design, so a person can approve it before you build.
