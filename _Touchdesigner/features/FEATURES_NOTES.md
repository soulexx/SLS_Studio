# Features Notes

## Purpose
- Holds visible functional building blocks.
- A feature block should primarily contain:
  - event interpretation
  - semantic logic
  - debug views
  - tests

## Rule
- Keep each feature readable as a single unit.
- Features may read from `eventbus` and write to `state`.
- Features should not own the durable truth they mutate.
- Hardware output and app adapters should live in consumer/output areas when they are reused outside one feature.
