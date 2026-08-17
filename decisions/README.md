# Decisions (ADR)

ที่เก็บข้อตัดสินใจระดับ **ecosystem** — เรื่องที่ผูกหลาย repo และเปลี่ยนภายหลังแพง

ADR ในโฟลเดอร์นี้เป็น **authority** ของศัพท์และขอบเขต ถ้าเอกสารใน [`../ref/`](../ref/) ขัดกับ ADR ที่ Accepted แล้ว → ADR ชนะ (ref เป็นบันทึกดิบตามเวลา ไม่ใช่ข้อตกลง)

## กติกา

* หนึ่งไฟล์ = หนึ่งข้อตัดสินใจ ตั้งเลขเรียงไม่ซ้ำ ไม่ลบไฟล์เก่า
* Status: `Proposed` → `Accepted` / `Rejected` → `Superseded by NNNN`
* แก้ ADR ที่ Accepted แล้วไม่ได้ — ต้องเขียนตัวใหม่ที่ supersede
* ADR ต้องมี **Options ที่พิจารณา** ไม่ใช่แค่คำตอบ เพื่อให้คนมาใหม่รู้ว่าทำไมไม่เลือกทางอื่น
* repo ลูกเก็บ spec ภายในที่ `rfcs/` ของตัวเอง (เช่น `devfactory-core/rfcs/`) และ **ห้ามแก้ contract กลางเอง**

## สถานะปัจจุบัน

ทั้ง 8 ตัวเป็น `Proposed` — ช่อง **Decision ยังว่าง รอเคาะ** แต่ละไฟล์มี Context + Options + Recommendation ให้แล้ว

| ADR | เรื่อง | ปัญหาที่แก้ | Blocking อะไร |
| --- | --- | --- | --- |
| [0001](0001-platform-scope.md) | Platform scope | repo นี้ implement หรือไม่ / mono vs multi-repo | ทุกอย่าง |
| [0002](0002-core-repository-naming.md) | Core repository naming | ชื่อ core repo มี 4 เวอร์ชันในเอกสาร | 0003, module mapping |
| [0003](0003-agent-gateway-boundary.md) | Agent gateway boundary | `agent-gateway` มี 3 ความหมายคนละทิศ | contracts, module mapping |
| [0004](0004-agent-vs-model-provider.md) | Agent vs model provider | LLM / Agent / Coding Agent ปนกัน | `contracts/provider/` |
| [0005](0005-agent-runtime-boundary.md) | Agent runtime boundary | runtime / harness / workflow / sandbox ทับกัน | `contracts/execution/` |
| [0006](0006-contract-versioning.md) | Contract versioning | ใครเป็นเจ้าของ contract, แก้ยังไง | contracts ทั้งหมด |
| [0007](0007-multi-tenancy.md) | Multi-tenancy | tenant model 3 แบบใน 3 เอกสาร | `contracts/identity/` |
| [0008](0008-reference-stack.md) | Reference stack | Cloudflare vs Python vs Node | น้อยสุด (contract ไม่ผูก tech) |

## ลำดับที่ควรเคาะ

```text
0001 (scope)
  ↓
0002 (ชื่อ) ── 0004 (ศัพท์ provider)
  ↓                ↓
0003 (gateway) ── 0005 (runtime)      ← vocabulary/boundary gate
  ↓
0006 (versioning) ── 0007 (tenancy)
  ↓
0008 (stack)
  ↓
contracts/ P0
```

**0003 + 0004 + 0005 คือ vocabulary/boundary gate** ตาม [decisions-first plan](../ref/agent-platform-decisions-first-plan.md) Phase 2 — ห้ามเขียน `contracts/` ก่อนสามตัวนี้ Accepted ไม่งั้น schema จะฝังศัพท์ที่ยังไม่ตกลง

## ที่มา

Context ในแต่ละ ADR ดึงจาก [`../ref/`](../ref/) (11 ไฟล์ raw) และจากการอ่าน repo จริง 3 ตัว — สรุปไว้ที่ [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) และ [`../ref/existing-repos.md`](../ref/existing-repos.md)
