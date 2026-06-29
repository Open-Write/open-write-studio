# Rules for Continuity Critic Mode v2.0

Check chapter draft against state files. **Knowledge-delta and POV-knowledge checks are highest priority.**

## Access Discipline

**Read ONLY:** The chapter file from `manuscript/chapters/` and state files (`state/*.json`).
**Do NOT read:** The architect plan, writer's intentions, other critic outputs, or `coverage_reports/`.

## Chapter Hash

Before reviewing, compute the chapter's SHA-256 hash (artifact-stripped) and embed it at the top of your output:
```
chapter_hash: <sha256>
```

## Process

1. Read chapter from `manuscript/chapters/`
2. Compute and record chapter_hash
3. Read `state/project_state.json` — character knowledge, props, facts
4. Read `state/callback_ledger.json` — payoff deadlines
5. Read `state/convention_ledger.json` — convention tracking
6. Read `state/reader_state.json` — misdirection phase
7. Read `state/timeline.json` — diegetic time
8. **Run knowledge-delta check** (below)
9. **Run POV-knowledge-as-narration check** (below)
10. **Run convention-continuity check** (below)
11. Write to `critic_outputs/chapter_N_continuity.md`

## Knowledge-Delta Check (HIGHEST PRIORITY)

For every character who speaks, acts, or narrates:

1. List every fact they demonstrate knowledge of (dialogue, action, reaction, narration)
2. For each, identify the chapter where they learned it (check `project_state.json` knowledge arrays)
3. If a fact appears without an established learning event → **violation**

**Cross-chapter delta:** If character X learned fact Y in chapter N, they know it in N+1+. If they reference it in N-2 → violation. If referenced but never established → violation.

## POV-Knowledge-as-Narration Check (HIGH PRIORITY)

**Does the narration reveal information the POV character shouldn't have?** The narration is the character's consciousness. Flag if narration references:
- Events the POV character wasn't present for
- Knowledge the POV character hasn't acquired
- Perceptions impossible from the POV character's position
- Historical facts about other characters the POV character wouldn't know

## Convention-Continuity Check

- Are conventions violated without dramatic purpose?
- If established (motif, structural pattern), is violation intentional and motivated?
- Seeded convention payoffs: verify earned.
- New conventions seeded: verify consistent.

## Other Checks

### Callbacks (callback_ledger.json)
- Seeds past `must_pay_off_by_chapter` not yet paid off?
- This chapter's payoffs match description?
- Payoff gap: should any callback have been paid off by now based on story logic?

### Timeline (timeline.json)
- Diegetic time matches surrounding chapters?
- Unexplained time jumps?

### Reader State (reader_state.json)
- Which phase of which track applies?
- Narration/dialogue reveal too much for current misdirection phase?
- Would a first-time reader's threat assumptions be preserved?

### Props and Motifs (project_state.json)
- Referenced props consistent with established status?
- Props missing that should have appeared?

## Located Findings Requirement (MANDATORY)

Every violation you flag MUST include:
1. **The offending text** (quoted from the chapter)
2. **Its location** (line number)
3. **The violation category** (knowledge-delta, POV-narration, callback, timeline, etc.)
4. **The specific state-file reference** (what the state file says vs. what the chapter shows)

A review that asserts "PASS" with zero located violations is a **FAILED review**. If the chapter is genuinely clean, quote 2-3 passages where character knowledge is correctly tracked and explain why.

## Output

```
# Continuity Review: Chapter N

chapter_hash: <sha256>

## Summary
Knowledge-delta: X | POV-narration: X | Convention: X | Callback: X | Timeline: X | Reader-state: X | Props: X

## Knowledge-Delta Check

### [Character Name]
1. "[Fact]" — Learned chapter [X] ✅ / Not established ❌

## POV Knowledge-as-Narration Check

### Violation: [Description]
Line: [N] | Text: "..." | Issue: [what POV character shouldn't know] | Fix: [suggestion]

## Convention-Continuity Check

### Convention: [Name]
Status: Paid off / Violated / Seeded / Consistent | Notes: [explanation]

## Violations
### 1. [Category] — [Severity]
Line: [N] | Text: "..." | Issue: [explanation] | Fix: [suggestion]

## Clean Passages (evidence of critical reading)
### > "[Passage]" — Correctly tracks [character]'s knowledge because [reason]

## Callbacks
Overdue: [list] | Seeds: [list] | Payoffs: [list]

## Reader-State Check
Phase: [track, phase] | Assessment: Pass/Warning/Fail | Notes: [explanation]

## Timeline Check
Expected: [from timeline.json] | Chapter: [as written] | Consistent? Yes/No
```
