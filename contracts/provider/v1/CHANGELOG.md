# provider/v1

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม [ADR-0004](../../../decisions/0004-agent-vs-model-provider.md)
- base + 2 specialization: `provider` · `model-provider` · `agent-provider`
- ไม่มี field `capabilities` โดยตรง — อ้าง `capability/v1/declaration` ตาม [ADR-0009](../../../decisions/0009-capability-model.md)
