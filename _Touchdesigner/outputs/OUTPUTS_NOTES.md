# Outputs Notes

## Purpose
- Holds consumers that react to shared state or explicit intents.
- Output blocks do not own truth.

## Typical Consumers
- LED renderers
- Bitwig adapters
- other external transports

## Rule
- Outputs read semantic state or semantic intents.
- Outputs do not interpret raw device events.
- If a renderer or adapter becomes reusable, keep it outside the feature block that first used it.
