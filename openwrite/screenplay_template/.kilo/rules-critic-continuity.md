# Rules for Continuity Critic Mode

Check scene draft against four state files. **Knowledge-delta check is highest priority.**

## Process

1. Read scene from `script/scenes/`
2. Read `state/project_state.json` — character knowledge, props, facts
3. Read `state/callback_ledger.json` — payoff deadlines
4. Read `state/timeline.json` — diegetic time
5. Read `state/audience_state.json` — misdirection phase
6. **Run knowledge-delta check** (below)
7. Write to `critic_outputs/scene_N_continuity.md`

## Knowledge-Delta Check (HIGHEST PRIORITY)

For every character who speaks or acts:

1. List every fact they demonstrate knowledge of (dialogue, action, reaction)
2. For each, identify the scene where they learned it (check `project_state.json` knowledge arrays)
3. If a fact appears without an established learning event → **violation**

**Example:** A character says "The pattern correlates with classified program run windows" — but the program name isn't established as something they know. Should say "classified run windows from this facility."

**Cross-scene delta:** If character X learned fact Y in scene N, they know it in N+1+. If they reference it in N-2 → violation. If referenced but never established → violation.

## Other Checks

### Callbacks (callback_ledger.json)
- Seeds past `must_pay_off_by_scene` not yet paid off?
- Does this scene pay off callbacks? Verify payoff matches description.
- Does this scene seed new callbacks?
- Payoff gap: should any callback have been paid off by now based on story logic?

### Timeline (timeline.json)
- Diegetic time matches surrounding scenes?
- Act 3: countdown correct?
- Unexplained time jumps?

### Audience State (audience_state.json)
- Which phase of which track applies?
- Action lines reveal too much for current misdirection phase?
- Would a first-time viewer's threat assumptions be preserved?

### Props (project_state.json)
- Referenced props consistent with established status?
- Missing props that should have appeared?

## Output

```
# Continuity Review: Scene N

## Summary
Knowledge-delta violations: X | Callback issues: X | Timeline: X | Audience-state: X | Props: X

## Knowledge-Delta Check

### [Character Name]
1. "[Fact]" — Learned scene [X] ✅ / Not established ❌

## Violations
### 1. [Category] — [Severity]
Line: [N] | Text: "..." | Issue: [explanation] | Fix: [suggestion]

## Callbacks
Overdue: [list] | Seeds: [list] | Payoffs: [list]

## Audience-State
Phase: [track, phase] | Assessment: Pass/Warning/Fail | Notes: [explanation]

## Timeline
Expected: [from timeline.json] | Scene: [as written] | Consistent? Yes/No
```
