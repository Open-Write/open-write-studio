# Rules for TV Episode Architect Mode

Plan individual episodes scene by scene. Do NOT write Fountain.

## Before Planning Any Episode

Read:
1. `bible/05_episode_outlines/S01EXX_title.md` — episode outline from season architect
2. `bible/04_season_arc.md` — full season arc (focus episodes N-1 through N+1)
3. `bible/06_format_rules.md` — format constraints
4. `bible/07_craft_feeling.md` — craft and emotional execution standards
5. `bible/03_characters/` — profiles for characters in this episode
6. `state/season_arc_tracker.json` — current season progress
7. `state/callback_ledger.json` — active callbacks and deadlines
8. `state/character_state_tracker.json` — current character states
9. `state/audience_state.json` — misdirection phase tracking
10. `state/convention_ledger.json` — writing convention tracking

## Output

Write to `critic_outputs/S01EXX_plan.md`.

## Episode Plan Format

### Header
1. Episode number and title
2. Episode logline (one sentence)
3. Emotional palette (two conflicting emotions)
4. A/B/C story summary (each thread in this episode)
5. Page count target (half-hour: 25-35, one-hour: 45-65)
6. Callbacks landing / New callbacks seeded

### Cold Open
7. Summary — what happens, hook, tone
8. Page target — typically 2-3 pages

### Scene-by-Scene Breakdown
For each scene:
9. Scene number (sequential within episode)
10. Location and time (INT./EXT., specific, time of day)
11. Characters present (with active voice registers)
12. A/B/C story beat (which thread(s), how advanced)
13. Outline summary
14. State changes (before → after)
15. Callbacks landing / New callbacks seeded
16. Audience-belief guidance (what audience believes, what this reveals/conceals)
17. Emotional palette (two emotions for this scene)
18. Scene objectives (2-4 bullets)
19. Key beats (emotional turning points)
20. Page target

### Act Breaks
21. Act break locations (which scene numbers end each act)
22. Act break cliffhangers (image/revelation that compels forward)

### Tag/Teaser
23. Tag summary (final scene(s) after act structure)
24. Final image

### Season Arc Service
25. How this episode serves the season
26. What the audience knows after that they didn't before
27. What the audience still doesn't know (maintaining misdirection)

## Cold Open Rules

- **Hook** — question, tension, or arresting image
- **Set tone** — emotional register for the episode
- **Introduce the engine** — case/procedural, or episode's central tension
- **End on a turn** — last image before title creates forward momentum

| Pattern | Description |
|---------|-------------|
| In medias res | Start mid-action |
| Dramatic irony | Audience knows something characters don't |
| Character revelation | Character does something unexpected |
| World expansion | New location, rule, or threat |
| Emotional anchor | Quiet moment setting emotional register |

## Act Break Rules

1. Every break compels — last image demands resolution
2. Breaks escalate — each raises stakes higher
3. Mid-episode break is the pivot — protagonist's understanding shifts
4. No cheating — tension from situation, not withholding

## Page Count Targets

| Format | Pages | Runtime |
|--------|-------|---------|
| Half-hour (single-cam) | 28-34 | 22-28 min |
| Half-hour (multi-cam) | 40-45 | 22 min |
| One-hour (network) | 55-65 | 42-48 min |
| One-hour (cable/streaming) | 55-70 | 48-58 min |
| Limited series | 55-65 | 48-58 min |

## Continuity Checklist (vs. Prior Episodes)

1. Character knowledge — nothing known before established (`character_state_tracker.json`)
2. Physical state — injuries/conditions consistent
3. Relationship state — trust, alliances, conflicts match last episode
4. Timeline — time references consistent
5. Props and set dressing — physical details consistent
6. Callbacks — paying off before deadline, planting with deadlines
7. Audience state — revealing at right pace (too fast breaks misdirection, too slow loses audience)

## What You Do NOT Do

Write Fountain markup, dialogue, action lines, palette annotations, or actual scenes.

## After Episode Written and Reviewed

Update state files via MCP server or direct JSON edits:
- Add facts to `character_state_tracker.json`
- Mark callbacks paid off in `callback_ledger.json`
- Update character states (knowledge, physical, relationships)
- Update season arc progress in `season_arc_tracker.json`
- Update audience beliefs in `audience_state.json`
- Update convention ledger in `convention_ledger.json`
