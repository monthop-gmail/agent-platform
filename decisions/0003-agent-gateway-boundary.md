# ADR-0003: Agent Gateway Boundary

**Status:** Accepted (2026-08-17)
**Date:** 2026-08-17
**Depends on:** ADR-0002
**Blocking:** `contracts/` ทั้งหมด — **นี่คือ vocabulary gate**

## Context

ชื่อ `agent-gateway` ถูกใช้เรียก **3 ระบบที่คนละทิศทาง traffic** ในเอกสาร `ref/` และทั้งสามเสนอชื่อ repo ทับกัน

| # | ที่มา | ทิศทาง | หน้าที่ | ชื่อ repo ที่เสนอ |
| --- | --- | --- | --- | --- |
| 1 | [`naming-convention`](../ref/naming-convention-ecosystem.md) + [`backend-os §4`](../ref/enterprise-agent-backend-os-blueprint.md) | **inbound** | agent ภายนอก (Claude/Codex) เข้ามาหา enterprise backend ผ่าน MCP/A2A + auth + policy + approval + audit | `agent-gateway` |
| 2 | [`ai-subscription-oauth-gateway`](../ref/ai-subscription-oauth-gateway-blueprint.md) | **outbound** | เราถือ subscription/OAuth ไปเรียก provider ข้างนอก — credential broker + capability router | `ai-agent-gateway` |
| 3 | [`distributed-multi-agent-gateway`](../ref/distributed-multi-agent-gateway-blueprint.md) | **fan-out** | รับ task จาก ChatGPT → broker → worker หลัง NAT → coding agent | `agent-gateway` |

ทั้งสามเป็นระบบที่ต้องมีจริงและ **ไม่ทับหน้าที่กัน** — ปัญหาอยู่ที่ชื่อเท่านั้น ถ้าปล่อยไว้จะสร้าง repo ชนกันและ contract จะฝังคำที่กำกวม

นอกจากนี้ [`decisions-first plan`](../ref/agent-platform-decisions-first-plan.md) Phase 0 ระบุว่า ADR นี้ต้องตอบด้วยว่า **gateway / runtime / adapter ใครทำอะไร** โดยไม่ซ้อนกัน

## Options — การตั้งชื่อ

### A. แยกชื่อตามทิศทาง (แนะนำ)

| ระบบ | ชื่อ | เหตุผล |
| --- | --- | --- |
| inbound | **`agent-gateway`** | เก็บชื่อเดิมไว้กับตัวที่อยู่ในลิสต์ 7 core repos และ module `agent-gateway/` ของ repo นี้ |
| outbound | **`model-gateway`** | สิ่งที่มันคุมคือ model/provider credential ไม่ใช่ agent |
| fan-out | **`agent-fleet`** | สิ่งที่มันคุมคือ worker fleet — ตรงกับคำที่ blueprint ใช้เอง ("Distributed Worker / Fleet") |

* ✅ ชื่อบอกหน้าที่ ไม่ต้องอ่านเอกสารก็เดาถูก
* ✅ `agent-gateway` ไม่ต้องเปลี่ยน → module dir ปัจจุบันใช้ได้เลย
* ❌ ทีมที่อ่าน blueprint #2/#3 มาก่อนต้องเรียนชื่อใหม่

ชื่อสำรองที่พิจารณา: outbound → `provider-broker`, `subscription-broker`, `credential-broker` · fan-out → `task-dispatcher`, `worker-gateway`, `agent-dispatcher`

### B. ใช้ `agent-gateway` เป็นร่มเดียว มี 3 ชั้นข้างใน

```text
agent-gateway/
├── inbound/
├── outbound/
└── fleet/
```

* ✅ ชื่อเดียว จำง่าย
* ❌ 3 ระบบนี้ deploy คนละที่ scale คนละแบบ (inbound = public API, outbound = ถือ secret, fleet = broker + worker หลัง NAT) — ยัดรวมทำให้ blast radius ของ secret ใหญ่ขึ้น
* ❌ ขัดกับ blueprint #3 ที่สั่งชัดว่า "ให้แยกเป็น repo ใหม่"

### C. เปลี่ยนชื่อ inbound เป็นอย่างอื่น (เช่น `agent-ingress`) แล้วให้ `agent-gateway` เป็นชื่อกลาง

* ❌ ต้องแก้ทั้ง module dir + ลิสต์ 7 core repos + backend-os blueprint §4 (มากที่สุด) โดยได้ประโยชน์น้อยกว่า A

## Options — เส้นแบ่ง Gateway / Runtime / Adapter

ข้อเสนอ (ให้ ADR-0005 ยืนยันฝั่ง runtime):

| ชั้น | รับผิดชอบ | **ห้าม** ทำ |
| --- | --- | --- |
| **Gateway** | authn/authz, tenant resolution, tool discovery, policy check, approval trigger, quota/rate limit, audit emit, request normalization | ตัดสินใจแทน agent · เก็บ business state · เรียก model เอง |
| **Runtime** | agent loop, session/state, context assembly, tool call orchestration, lifecycle (spawn/resume/cancel) | ตัดสิน governance เอง · เข้าถึง backend resource ตรง ๆ · ถือ provider credential |
| **Adapter** | แปลง protocol/credential ของ provider หรือ runtime ภายนอกให้เป็น contract กลาง | มี business logic · ตัดสินใจ policy |

ข้อ "ห้าม" ของ Runtime มาจาก `devfactory-core` RFC-0004 (*"Execution making governance decisions — forbidden"*) ซึ่งตรงกับ [`navi-security-agent §3`](../ref/navi-security-agent-blueprint.md) (**AI ≠ Authority**) และ [`backend-os §4`](../ref/enterprise-agent-backend-os-blueprint.md) (ห้าม agent แตะ backend resource ตรง) — **3 แหล่งเห็นตรงกัน**

## Decision

**A** — แยกชื่อตามทิศทาง traffic:

| ระบบ | ชื่อที่ lock |
| --- | --- |
| inbound (agent ภายนอก → enterprise backend) | **`agent-gateway`** |
| outbound (เราถือ subscription → provider) | **`model-gateway`** |
| fan-out (task → broker → worker หลัง NAT) | **`agent-fleet`** |

และ **ยืนยันตารางเส้นแบ่ง Gateway / Runtime / Adapter** ในหัวข้อด้านบนตามที่เขียนไว้ รวมรายการ "ห้ามทำ" ของแต่ละชั้น

**Reason:** ทั้งสามเป็นระบบที่ต้องมีจริงและไม่ทับหน้าที่กัน ปัญหาอยู่ที่ชื่อเท่านั้น · ปฏิเสธ B (ร่มเดียว) เพราะทั้งสาม deploy และ scale คนละแบบ และการรวม outbound (ที่ถือ credential) เข้ากับ inbound (public API) ทำให้ blast radius ของ secret ใหญ่ขึ้นโดยไม่จำเป็น · ปฏิเสธ C เพราะต้องแก้มากที่สุดโดยได้ประโยชน์น้อยกว่า A

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

ห้ามใช้คำว่า "gateway" เดี่ยว ๆ ใน contract หรือเอกสารใหม่ — ต้องระบุว่าตัวไหน

## Consequences ถ้าเลือก A

* `ref/ai-subscription-oauth-gateway-blueprint.md` → ชื่อ repo เปลี่ยนเป็น `model-gateway` (เนื้อหาไม่ต้องแก้)
* `ref/distributed-multi-agent-gateway-blueprint.md` → ชื่อ repo เปลี่ยนเป็น `agent-fleet` (โครง `gateway/` + `worker/` ข้างในคงเดิมได้)
* `contracts/` ต้องมีคำสามคำนี้แยกกันชัด ห้ามใช้คำว่า "gateway" เดี่ยว ๆ ใน schema
* ต้องเพิ่ม `model-gateway` และ `agent-fleet` ในลิสต์ repo ของ ecosystem

## Sources

[`../ref/naming-convention-ecosystem.md`](../ref/naming-convention-ecosystem.md) · [`../ref/enterprise-agent-backend-os-blueprint.md`](../ref/enterprise-agent-backend-os-blueprint.md) §4 · [`../ref/ai-subscription-oauth-gateway-blueprint.md`](../ref/ai-subscription-oauth-gateway-blueprint.md) · [`../ref/distributed-multi-agent-gateway-blueprint.md`](../ref/distributed-multi-agent-gateway-blueprint.md) · [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) §1
