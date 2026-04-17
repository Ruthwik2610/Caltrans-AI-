---
tags: [memory, caltrans, institutional-memory, operating-model]
created: 2026-04-15
status: active
---

# 🧠 Caltrans Project Memory Plan

> [!abstract] Purpose
> This note turns the vault structure into a working memory system for the Caltrans CUCP project.
> The goal is to keep project facts, decisions, precedents, and open questions in one predictable loop.

## 1. What Counts as Project Memory

Project memory should capture only information that helps the team make the next decision faster.

- **Facts**: stable project details, inputs, data sources, and document references.
- **Decisions**: choices made about logic, UX, models, scoring, or deployment.
- **Precedents**: human overrides and evaluation rules that should be reused later.
- **Open questions**: unresolved items that need a future decision or review.
- **Status signals**: what is done, blocked, in progress, or awaiting review.

## 2. Canonical Sources

These are the files we should treat as the source of truth for memory-related work.

- `src/memory_db.json`: live precedent store for CUCP overrides.
- `src/memory_manager.py`: add, stage, commit, and consolidate memory behavior.
- `30-Institutional-Memory/Institutional Memory.base`: human-readable view of the precedent data.
- `40-Meetings/Development Log.md`: chronological record of work and decisions.
- `50-Tasks/Project Delivery Evaluator Progress.md`: feature progress and outstanding implementation items.
- `00-Architecture/Architecture Overview.md`: system-level context for how memory fits into the app.

## 3. Memory Workflow

Use the same loop every time we learn something new.

1. Capture the new fact, decision, or override in a meeting note or task note.
2. Classify it as fact, decision, precedent, or open question.
3. If it is a precedent, add it to `src/memory_db.json` through `src/memory_manager.py`.
4. Reflect the precedent in `Institutional Memory.base` so it is visible in Obsidian.
5. Summarize the change in `40-Meetings/Development Log.md`.
6. If the item affects delivery work, update `50-Tasks/Project Delivery Evaluator Progress.md`.

## 4. Memory Taxonomy

### Level 1: Fact Extraction

- Raw narrative details from nomination or evaluation documents.
- Direct observations that do not require policy interpretation.
- Document-specific values that can be checked against source text.

### Level 2: Interpretation

- Legal or policy classification decisions.
- How a fact should be interpreted under 49 CFR Part 26 or project rules.
- Anything that requires a human judgment call beyond direct extraction.

### Level 3: Threshold Decision

- Final pass or fail style outcomes.
- Borderline calls that depend on evidentiary weight.
- Decisions that should be reused as precedents later.

## 5. Note Structure We Should Keep Using

- **Architecture notes** explain how the system works.
- **Research notes** store source material and citations.
- **Logic-flow notes** show how decisions are made step by step.
- **Institutional-memory notes** store reusable precedents and rules.
- **Meeting notes** record decisions, tradeoffs, and follow-ups.
- **Task notes** track current implementation work and open backlog items.

## 6. Operating Rules

- Keep the memory store small and useful; do not save every transient thought.
- Prefer one clear precedent over many near-duplicates.
- Write decisions in plain language that a future reviewer can understand quickly.
- Link every memory item back to the code or source note that created it.
- Update Obsidian after the code or data changes, not instead of them.

## 7. First Working Sprint

- Create a real `Active Sprint` note for current work items.
- Add the first set of project precedents from `src/memory_db.json`.
- Backfill a research note for `49 CFR Part 26` so the legal context has a home.
- Capture the next CUCP / project delivery decision in the Development Log.
- Keep the MOC pointed at live notes only, not placeholders.

## 8. Success Criteria

- A new precedent can be captured in one pass without hunting for the right file.
- A reviewer can open the MOC and find the current memory system immediately.
- The Development Log reflects meaningful decisions, not just activity.
- The Obsidian base mirrors the live memory JSON closely enough to be useful.

