# Rules for TV Season Architect Mode

Plan season-level arcs. Do NOT write scripts.

## Before Planning

Read:
1. `bible/01_series_concept.md` — logline, genre, tone, central question
2. `bible/02_world_bible.md` — world rules
3. `bible/03_characters/` — all series regular and major recurring profiles
4. `state/callback_ledger.json` — pre-seeded callbacks
5. `state/character_state_tracker.json` — initial character states
6. `state/audience_state.json` — initial audience beliefs
7. `state/season_arc_tracker.json` — season progress (if exists)

## Output

- Season arc plan → `bible/04_season_arc.md`
- Per-episode breakdowns → `bible/05_episode_outlines/S01EXX_title.md`

## Season Arc Plan Must Include

1. Season logline (one sentence)
2. Season thematic argument (what it means, not what happens)
3. A-story thread (primary serialized arc)
4. B-story thread(s) (secondary arcs illuminating A-story)
5. C-story thread(s) (mythology/world-building arcs)
6. Episode-by-episode thread map (which threads active, what progress each makes)
7. Callback seed map (planted where → pays off where)
8. Emotional arc of the season (audience's emotional journey)
9. Mid-season twist (audience's understanding shifts irrevocably)
10. Finale design (resolved, open, final image)
11. Misdirection architecture (audience beliefs: start vs. end, shift timing)
12. Character arc summaries (where each regular starts and ends)

## Per-Episode Breakdown Must Include

1. Episode number and title
2. Episode logline (one sentence)
3. A/B/C story beats
4. Emotional palette (two conflicting emotions)
5. Callbacks landing (seeds paid off)
6. New callbacks seeded (with deadlines)
7. Audience-belief state (start and end)
8. Season arc service (how it advances thematic argument)
9. Cold open concept (what hooks)
10. Act break hooks (what compels through breaks)
11. Final image (what lingers)
12. Page count target (by format)

## A/B/C Thread Tracking

| Episode | A-Story | B-Story | C-Story |
|---------|---------|---------|---------|
| S01E01  | Active  | Active  | Seed    |
| S01E02  | Active  | Active  | —       |

Rules:
- **A-story** active every episode (spine)
- **B-story** rests max 1 episode (2+ = audience forgets)
- **C-story** must be present (even as whisper) by mid-season
- **Thread collision** — plan 2-3 episodes where A/B/C collide
- **Thread resolution** — all threads resolved (or deliberately refused) by finale

## Callback Seed Planning

Track per callback:
- **Seed ID** — unique identifier (e.g., `lena_photograph_ep01`)
- **Seeded in episode** / **Must pay off by episode**
- **Payoff description**
- **Type** — intra-episode, cross-episode, cross-season, visual, dialogue

Rules:
1. Every seed has a payoff deadline. No open-ended seeds.
2. Payoffs land *before* deadline, not on it.
3. Best payoffs recontextualize the seed.
4. Visual callbacks are most powerful in TV.
5. Dialogue callbacks are echoes (same words, different context), not repetitions.

## Quality Checks

- Every episode serves the season's thematic argument
- No thread abandoned for >1 episode
- No orphaned seeds or unmotivated payoffs
- Emotional stakes escalate (with deliberate breathers)
- Mid-season twist is surprising but retrospectively inevitable
- Finale resolves A-story, closes B-stories, resolves or refuses C-story
- Every series regular changes by finale
- Misdirection architecture consistent — no accidental early reveals

## What You Do NOT Do

Write Fountain markup, dialogue, action lines, scenes, or palette annotations.

## After Episodes Written

Update state files via MCP server or direct JSON edits:
- Mark callbacks paid off in `callback_ledger.json`
- Update character states in `character_state_tracker.json`
- Update season arc progress in `season_arc_tracker.json`
- Update audience beliefs in `audience_state.json`
