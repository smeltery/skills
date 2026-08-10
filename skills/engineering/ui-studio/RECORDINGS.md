# Screen Recording Intake

Use this guide when a video or animated recording is a reference. A recording
provides ordered visual evidence, but it does not make the underlying interface
navigable or expose inaccessible states.

## Establish the contract

Record the file or link, duration, dimensions, frame rate when known, revision,
rights mode, artifact policy, and the product question it should answer. Confirm
whether audio, pointer position, touch indicators, captions, or annotations are
meaningful evidence.

Never upload a private recording to an external transcription, vision, or frame
extraction service without explicit authorization. Keep extracted frames and
transcripts under ignored runtime state unless the artifact policy permits a
redacted durable form.

## Build an ordered observation map

Review the complete recording once before extracting details. Then record:

1. timestamps for each distinct state and transition;
2. visible trigger evidence, such as a pointer, touch indicator, focus movement,
   typed value, scroll, or narration;
3. the state before, transition behavior, resulting state, feedback, and
   recovery path;
4. observable timing ranges rather than invented exact durations;
5. viewport changes, overlays, occlusion, cuts, speed changes, and editing that
   make timing or causality uncertain.

Extract the smallest frame set that preserves the relevant sequence: before,
trigger, transition midpoint only when informative, after, and recovery. Keep
timestamps and source identifiers attached so frames are never treated as
unrelated screenshots.

## Confidence and limitations

Classify each observation as:

- `observed` — directly visible in an unbroken sequence;
- `inferred` — likely but not directly demonstrated;
- `unknown` — hidden by editing, framing, occlusion, or missing input evidence.

A recording cannot prove DOM order, accessible names, keyboard behavior,
responsive rules outside its dimensions, network behavior, error recovery, or
states it does not show. Route those gaps to a navigable source, repository UI,
additional recording, or the Direction gate. Never describe inferred input or
timing as exercised behavior.

## Synthesis output

Add ordered rows to the source ledger with timestamps, confidence, retained
frame identifiers, and limitations. Translate only supported interaction rules
into the trait matrix. Delete session-scoped frames, audio, transcripts, and
temporary conversions at the retention boundary.
