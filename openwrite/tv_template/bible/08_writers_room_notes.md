# Writers' Room Notes

*Protocol and creative guidelines for the simulated writers' room. This document governs how episodes are planned, reviewed, and revised. Adapted from editorial review and iterative revision protocols for episodic TV production.*

*See also: [`04_season_arc.md`](04_season_arc.md) for the season-level arc, [`06_format_rules.md`](06_format_rules.md) for format rules, [`07_craft_feeling.md`](07_craft_feeling.md) for craft standards.*

---

## I. THE WRITERS' ROOM MODEL

### What This Is

In a real TV writers' room, a team of writers collaborates on story development, breaks stories into episodes, and assigns scripts. This template simulates that process using AI modes:

| Room Role | AI Mode Equivalent | Responsibility |
|-----------|-------------------|----------------|
| **Showrunner** | Human creator | Final creative authority. Approves outlines, reviews scripts, makes casting-level decisions. |
| **Staff Writer** | Screenwriter mode | Writes the script based on the approved outline. |
| **Story Editor** | Architect mode | Plans scenes before they are written. Produces the scene-by-scene outline. |
| **Script Coordinator** | Continuity critic | Tracks character knowledge, callbacks, timeline, and cross-episode consistency. |
| **Researcher** | Bible auditor | Verifies the bible for contradictions before generation. |
| **Network Executive** | Adversarial reader | Reads cold, without the bible. Reports what's on the page, not what was intended. |
| **Standards & Practices** | Show-don't-tell critic | Mechanical enforcement of format rules. |
| **Acting Coach** | Voice critic | Per-character voice consistency. |
| **Tone Consultant** | Palette critic | Emotional palette verification. |
| **Script Doctor** | Cutter | Conditional — removes only flagged material. |

### The Room's Rules

1. **The showrunner has final say.** AI modes propose; the human disposes.
2. **The bible is law.** No episode contradicts the bible without an amendment to the bible first.
3. **The format rules are non-negotiable.** Every scene loads `06_format_rules.md`.
4. **Cross-episode consistency is everyone's job.** The script coordinator (continuity critic) catches what others miss.
5. **The adversarial reader reads cold.** No bible access. No prior episode context. What's on the page is what's on the page.

---

## II. THE EPISODE PRODUCTION PIPELINE

### Step 1: Story Break

Before any writing begins, the writers' room breaks the story:

1. **Present the episode concept** — What is the A-story? B-story? C-story?
2. **Identify the emotional arc** — What does the protagonist feel at the start vs. the end?
3. **Identify the callbacks** — What seeds are planted? What seeds are paid off?
4. **Identify the act breaks** — Where are the hooks?
5. **Review against the season arc** — Does this episode serve the season?

**Output:** Completed [`05_episode_outlines/S01EXX_title.md`](05_episode_outlines/_template.md)

### Step 2: Editorial Review

Before generation, run the outline through editorial personas (see [`skills/editorial_review_protocol.md`](../skills/editorial_review_protocol.md)):

- **Lara Marsh** (contest/studio reader) — Does the story work? Are the acts balanced?
- **Dr. Elena Vasquez** (literary fiction editor) — Is the thematic architecture sound?
- **Marcus Webb** (development executive) — Can this be shot? Is it marketable?

All three must return positive verdicts before proceeding.

### Step 3: Scene Planning

The architect plans each scene:

1. Load the episode outline + adjacent episode outlines
2. Load character profiles for all characters in the scene
3. Load `06_format_rules.md`
4. Load state files (audience state, callback ledger, character state)
5. Produce a scene plan: what happens, emotional palette, information asymmetry, callbacks

**Output:** `critic_outputs/S01EXX_scene_NN_plan.md`

### Step 4: Script Writing

The screenwriter writes each scene:

1. Load the scene plan
2. Load `06_format_rules.md` (every scene)
3. Load relevant character profiles
4. Write in Fountain markup
5. Re-read for clarity and economy before moving on

**Output:** `scripts/scenes/S01EXX/NN_scene_title.fountain`

### Step 5: Critic Pipeline

After each scene is written, run the critics:

1. **Show-don't-tell critic** — Mechanical enforcement
2. **Voice critic** (one per character) — voice consistency
3. **Palette critic** — Emotional palette verification
4. **Continuity critic** — Cross-episode state/callback review
5. **Naturalism critic** — AI-tell detection

Address all flagged issues before moving to the next scene.

### Step 6: Episode Assembly

After all scenes are written and critiqued:

1. Run `python tools/episode_assemble.py --episode S01E01`
2. Run `python tools/page_count.py --episode S01E01` — verify within target
3. Run `python tools/parenthetical_audit.py --episode S01E01` — verify under limit
4. Run `python tools/convention_scan.py` — update convention ledger

### Step 7: Episode-Level Review

After assembly:

1. **Adversarial reader** — Cold coverage of the assembled episode
2. **Cross-episode callback check** — `python tools/callback_check.py --episode S01E01`
3. **Iterative revision** — Apply revisions based on coverage feedback

### Step 8: Episode Lock

Once the episode passes all reviews:

1. Update `state/character_state_tracker.json` with end-of-episode states
2. Update `state/season_arc_tracker.json` with episode progress
3. Update `state/audience_state.json` with end-of-episode audience beliefs
4. Archive critic outputs
5. Lock the episode — no further changes without explicit showrunner approval

---

## III. THE ROOM'S CREATIVE GUIDELINES

### On Story

1. **Every episode must have a case.** Even mythology-heavy episodes need a procedural engine. The audience needs a reason to watch this week.
2. **Every case must connect to the themes.** A case that is only a case is a waste of an episode. The case should illuminate the season's central question.
3. **The B-story must not be filler.** If the B-story could be cut without losing anything, cut it. Every subplot must earn its screen time.
4. **The C-story (mythology) must advance.** Each episode must give the audience one new piece of the mythology puzzle. Not a revelation — a piece. The audience should feel like they're assembling something.

### On Character

1. **Characters must change.** A character who is the same in Episode 10 as Episode 1 is a wasted character. The change can be subtle — a shift in posture, a line that echoes earlier dialogue — but it must be there.
2. **Characters must be specific.** "She is sad" is not a character note. "She puts her coffee mug down with the handle facing exactly 45 degrees from the edge of the desk, the way she does when she's about to cry and won't" is a character note.
3. **Characters must surprise.** If the audience can predict every line of dialogue, the character is a type, not a person. The best character moments are the ones that feel inevitable in retrospect but surprising in the moment.
4. **Characters must have secrets.** Not plot secrets — emotional secrets. The thing they don't say. The thing they almost say. The thing they say that means the opposite.

### On Dialogue

1. **Subtext, always.** Characters do not name their emotional states.
2. **Specificity, always.** "I'm fine" is not dialogue. "I'm fine. Pass the salt" is dialogue — because the salt is specific and the deflection is visible.
3. **Economy, always.** If a line can be cut without losing meaning, cut it.
4. **Distinctiveness, always.** If you cover the character names, can you tell who is speaking? If not, the voices aren't distinct enough.

### On Structure

1. **The cold open must hook.** If the audience checks their phone during the cold open, you've lost them.
2. **Act breaks must compel.** The last image before each act break should be something the audience needs to see resolved.
3. **The final image must linger.** The last thing the audience sees should stay with them after the screen goes dark.
4. **The episode must be self-contained.** Even in a heavily serialized show, each episode must have a beginning, middle, and end. The audience should feel satisfied by the episode, not just by the season.

---

## IV. CROSS-EPISODE CONTINUITY

### The Continuity Bible

In addition to the series bible, maintain a running continuity document that tracks:

1. **Character knowledge states** — What each character knows at the end of each episode
2. **Physical states** — Injuries, illnesses, sleep deprivation that carry across episodes
3. **Relationship states** — Who trusts whom, who is in conflict, who has unresolved tension
4. **Timeline** — How much time has passed in the show's world
5. **Props and set dressing** — What is established about the physical world

This feeds into [`../state/character_state_tracker.json`](../state/character_state_tracker.json) and [`../state/season_arc_tracker.json`](../state/season_arc_tracker.json).

### The "Previously On" Test

Before finalizing an episode, ask: "If there were no 'previously on' recap, would the audience still understand this episode?" If the answer is no, the episode is too dependent on prior episodes and needs more self-contained clarity.

### The "New Viewer" Test

For the pilot and mid-season premiere, ask: "If this is the first episode someone watches, will they understand enough to keep watching?" These episodes need to onboard new viewers without boring returning ones.

---

## V. THE REVISION PROTOCOL FOR TV

### Per-Episode Revisions

After the adversarial reader's coverage, assess the revision scope (see [`skills/iterative_revision_protocol.md`](../skills/iterative_revision_protocol.md)):

| Scope | What Changes | Example |
|-------|-------------|---------|
| **Surface** | Specific sentences, word choices | Interiority violations, repetitive tics |
| **Scene** | Scene-level restructuring | Pacing issues, underdeveloped scenes |
| **Structural** | Episode-level changes | Missing scenes, wrong act breaks |
| **Voice** | Voice rule adjustments | Character voice drift |
| **Naturalism** | AI-tell pattern fixes | Em-dash overuse, triplet closings |

### Per-Season Revisions

After all episodes are assembled, run a season-level revision:

1. **Adversarial reader** on the full season
2. **Continuity check** across all episodes
3. **Callback audit** — all seeds paid off
4. **Character arc audit** — all arcs complete
5. **Thematic coherence audit** — the season's argument holds

### Diminishing Returns

Apply the same diminishing-returns tracking as the screenplay template. If two consecutive revisions produce no improvement, the episode has reached its ceiling. Stop and move on.

---

## VI. THE ROOM'S ETHICS

1. **Never use AI to simulate a real person's voice without disclosure.** The named personas (Lara Marsh, Dr. Elena Vasquez, Marcus Webb) are fictional constructs, not real people.
2. **The human creator has final authority.** AI modes propose; the human decides. Always.
3. **Track what the AI produces.** Every scene, every revision, every critic output is logged. The human can audit the process at any time.
4. **The goal is the best show possible.** Not the fastest show. Not the cheapest show. The best show.

---

*This document is the operating manual for the writers' room. It governs the process, not the content. The content comes from the bible, the outlines, and the craft guide. The process ensures that the content is produced consistently, reviewed rigorously, and revised until it reaches its ceiling.*
