# ADR-0009: Capability Model

**Status:** Accepted (2026-08-17)
**Date:** 2026-08-17
**Depends on:** ADR-0004, ADR-0005
**Blocking:** `contracts/capability/`, routing ใน gateway ทุกตัว

## Context

โครง 10 module เดิมและ contract P0 ที่ลิสต์ไว้ครอบ `agent` `model` `provider` `tool` — แต่ **ไม่มี `capability`** ทั้งที่การ routing จริงไม่ได้ถามว่า *"ใช้ provider ไหน"* แต่ถามว่า **"agent ไหนทำสิ่งนี้ได้"**

capability ปรากฏใน `ref/` **4 ที่ ในรูปแบบที่ต่างกันหมด** และไม่มีใครเป็นเจ้าของ:

| ที่มา | รูปแบบ |
| --- | --- |
| [`ai-subscription-oauth-gateway §8`](../ref/ai-subscription-oauth-gateway-blueprint.md) | yaml `capabilities: {coding: true, tools: true, streaming: true, subscription: true}` — boolean map ต่อ provider |
| [`ai-subscription-oauth-gateway §7`](../ref/ai-subscription-oauth-gateway-blueprint.md) | function `supports(provider)` `supports(auth_type)` `supports(model)` — predicate |
| [`distributed-gateway` Phase 3](../ref/distributed-multi-agent-gateway-blueprint.md) | json `capabilities: {docker, git, network}` + `agents: {opencode, claude-code, gemini}` — แยก infra capability ออกจาก agent list |
| [`distributed-gateway` Phase 3](../ref/distributed-multi-agent-gateway-blueprint.md) | `target: {agent: "auto", requirements: {coding: true, docker: true, budget: "free"}}` — requirement ฝั่ง task |
| [`backend-os §7`](../ref/enterprise-agent-backend-os-blueprint.md) | tool yaml มี `permission` `risk_level` `approval_required` — capability ระดับ tool |

และ [ADR-0005 option C2](0005-agent-runtime-boundary.md) ทำให้ capability **จำเป็น** ไม่ใช่ optional: เมื่อ execution เดินได้ 2 เส้นทาง (native / provider) ต้องมีอะไรบอกว่าเส้นทางไหนรองรับอะไร

## สิ่งที่ capability ต้องตอบ

```text
1. agent/provider ตัวนี้ทำอะไรได้      → declaration
2. task นี้ต้องการอะไร                 → requirement
3. อะไร match กับอะไร                  → resolution
```

สามอย่างนี้เป็น **schema คนละตัว** — ที่มาทั้ง 4 ข้างบนปนสองอย่างแรกเข้าด้วยกัน

## Options

### A. `contracts/capability/` เป็น first-class มี 3 schema (แนะนำ)

```text
contracts/capability/
├── capability.yaml       taxonomy — รายชื่อ capability ที่มีอยู่ + นิยาม + ระดับความเสี่ยง
├── declaration.yaml      provider/agent ประกาศว่าตัวเองมีอะไร
└── requirement.yaml      task ระบุว่าต้องการอะไร (+ soft/hard)
```

taxonomy ตั้งต้นจาก review + ที่ปรากฏใน ref:

```yaml
capabilities:
  - code_execution
  - github
  - browser
  - filesystem
  - shell
  - git
  - mcp
  - vision
  - long_context
  - autonomous_execution
  - streaming
  - docker
  - network_egress
```

* ✅ routing ถามได้ตรง ๆ ว่า "ใครทำ `browser` + `github` ได้" โดยไม่ต้องรู้จักชื่อ provider
* ✅ agent ที่เขียนเองประกาศ capability ได้เท่าเทียมกับ Claude Code — ต่อกับ ADR-0005 C2 พอดี
* ✅ แยก declaration/requirement ทำให้ `agent: "auto"` ของ distributed-gateway ทำงานได้จริง
* ✅ capability ผูก `risk_level` ได้ (เช่น `shell`, `network_egress`, `autonomous_execution` = สูง) → ต่อกับ [ADR-0010](0010-risk-approval-taxonomy.md) และ policy
* ❌ ต้องดูแล taxonomy ไม่ให้บวมและไม่ให้ซ้อนกันเอง → ต้องมีกฎว่าเพิ่ม capability ใหม่ต้องผ่าน ADR หรือ minor bump

### B. capability เป็น field ของ provider

* ✅ ง่ายสุด ไม่มี contract ใหม่
* ❌ ตอบได้แค่ทาง provider — ถามย้อนว่า "ใครทำ X ได้" ต้อง scan ทุก provider
* ❌ task requirement ไม่มีที่อยู่ → `agent: "auto"` ทำไม่ได้
* ❌ capability ของ **worker** (docker, network) ไม่ใช่ของ provider — distributed-gateway แยกไว้ถูกแล้ว

### C. ใช้ tool list เป็น capability โดยปริยาย

* ✅ ไม่มี taxonomy ให้ดูแล
* ❌ capability บางอย่างไม่ใช่ tool (`long_context`, `vision`, `streaming`)
* ❌ tool เปลี่ยนบ่อยกว่า capability → routing จะไม่นิ่ง

## Decision

**A** — `contracts/capability/` เป็น first-class มี 3 schema: **`capability.yaml`** (taxonomy) · **`declaration.yaml`** (ใครมีอะไร) · **`requirement.yaml`** (task ต้องการอะไร)
พร้อมแยก 3 ระดับ scope (provider / worker-host / tool) และกติกา **unknown capability = ไม่มี**

**Reason:** routing จริงถามว่า "ใครทำสิ่งนี้ได้" ไม่ใช่ "ใช้ provider ไหน" ซึ่งตอบย้อนทางไม่ได้ถ้า capability เป็น field ของ provider · ADR-0005 C2 ทำให้ execution เดินได้ 2 เส้นทาง จึงต้องมี declaration บอกว่าเส้นทางไหนรองรับอะไร — capability จึงจำเป็น ไม่ใช่ของเพิ่มทีหลัง · แยก declaration ออกจาก requirement เพราะที่มาทั้ง 4 แบบใน ref ปนสองอย่างนี้เข้าด้วยกัน ทำให้ `agent: "auto"` ทำงานไม่ได้ · ปฏิเสธ C เพราะ capability บางอย่างไม่ใช่ tool (`long_context`, `vision`, `streaming`) และ tool เปลี่ยนบ่อยกว่า capability

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

`contracts/provider/*.yaml` **ห้าม** มี field `capabilities` ของตัวเอง ต้องอ้าง `declaration.yaml` เพื่อไม่ให้ประกาศซ้ำสองที่แล้วไม่ตรงกัน

## Consequences ถ้าเลือก A

* `contracts/capability/` เข้าลิสต์ P0 (เดิมมี 12 หมวด → 13)
* `contracts/provider/*.yaml` **ไม่มี** field `capabilities` เอง แต่อ้าง `declaration.yaml` — ป้องกันการประกาศซ้ำสองที่แล้วไม่ตรงกัน
* capability มี 3 ระดับ scope ที่ห้ามปนกัน:

| scope | ตัวอย่าง | เจ้าของ |
| --- | --- | --- |
| provider capability | `long_context`, `vision`, `streaming` | model/agent provider |
| worker/host capability | `docker`, `network_egress`, `filesystem` | worker ที่รัน (ตาม distributed-gateway) |
| tool capability | `github`, `browser` | tool registry |

* เพิ่ม capability ใหม่ = เพิ่มค่าใน enum → ไม่ breaking ([ADR-0006](0006-contract-versioning.md)) แต่ **ลบหรือเปลี่ยนความหมาย = breaking**
* consumer ต้อง fallback อย่างปลอดภัยเมื่อเจอ capability ที่ไม่รู้จัก — ถือว่า "ไม่มี" ไม่ใช่ "มี"

## Sources

[`../ref/agent-platform-adr-review.md`](../ref/agent-platform-adr-review.md) ข้อ 4 · [`../ref/ai-subscription-oauth-gateway-blueprint.md`](../ref/ai-subscription-oauth-gateway-blueprint.md) §7, §8, §10, §11 · [`../ref/distributed-multi-agent-gateway-blueprint.md`](../ref/distributed-multi-agent-gateway-blueprint.md) Phase 3 · [`../ref/enterprise-agent-backend-os-blueprint.md`](../ref/enterprise-agent-backend-os-blueprint.md) §7
