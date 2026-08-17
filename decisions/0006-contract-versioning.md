# ADR-0006: Contract Versioning & Ownership

**Status:** **Accepted** — Versioning: `Accepted (2026-08-17)` · Ownership: `Accepted (2026-08-18)`
**Date:** 2026-08-17 · ownership resolved 2026-08-18
**Depends on:** ADR-0001
**Blocking:** —

## Context

ถ้า `agent-platform` เป็นเจ้าของ contract ที่ทุก repo ต้องใช้ร่วม ต้องตอบก่อนว่า **ใครแก้ได้ แก้แล้วคนอื่นพังไหม**

ปัญหาจริงที่มีอยู่แล้ว:

* `devfactory-core` มี `rfcs/0001`–`0004` เป็น **Status: Draft** ทั้ง 4 ตัว และ `GOVERNANCE.md` ระบุว่า **Architecture Owner ของ repo นั้น** มีอำนาจตัดสินสุดท้าย — ถ้า `agent-platform` ยก RFC เหล่านี้มาเป็น canonical แล้วต้นทางแก้ทีหลัง จะ drift ทันที
* `ref/` 11 ไฟล์เป็นบันทึกดิบที่ขัดกันเองหลายจุด — ต้องมีกฎว่าอะไรมีผลผูกพัน อะไรเป็นแค่บันทึก
* `ai-web-harness` และ `navi-ims` มีของรันอยู่แล้ว — contract v1 ต้องไม่ทำให้ของที่รันอยู่ผิดทันที

`devfactory-core/GOVERNANCE.md` ให้แบบที่ใช้ได้เลย: **RFC required for architectural change** · **majority maintainer approval** · **decisions are logged**

## Options — รูปแบบ version

### A. Directory per major + additive-only ภายใน major (แนะนำ)

```text
contracts/
├── agent/
│   ├── v1/
│   │   ├── agent.schema.yaml
│   │   └── CHANGELOG.md
│   └── v2/
└── event/
    └── v1/
```

* breaking change = สร้าง `v2/` ใหม่ `v1/` ยังอยู่จน consumer ย้ายครบ
* ภายใน major เพิ่ม optional field ได้ · ห้ามลบ field · ห้ามเปลี่ยนความหมาย · ห้ามเปลี่ยน required
* ✅ consumer pin version ได้ตรง ๆ ไม่ต้องอ่าน CHANGELOG
* ✅ รองรับ 2 version พร้อมกันช่วงย้าย
* ❌ ไฟล์ซ้ำเยอะเมื่อขึ้น major

### B. Semver ในไฟล์ (`version: 1.2.0` ใน schema)

* ✅ ไฟล์เดียวต่อ contract
* ❌ consumer ที่ pin `1.x` ต้องเชื่อว่าเราไม่เผลอ breaking — ตรวจอัตโนมัติยากกว่า

### C. Schema registry ภายนอก

* ❌ ต้องมี service = ขัด ADR-0001 option A (repo ไม่ implement)

## Options — ความเป็นเจ้าของ

### A2. `agent-platform` เป็น owner, repo ลูกเป็น consumer (แนะนำ)

```text
agent-platform/contracts/     canonical — แก้ได้ผ่าน ADR เท่านั้น
        ↓ consume
devfactory-core · navi-security-agent · enterprise-knowledge · agent-fleet · ...
        rfcs/ ของตัวเอง = spec ภายใน ห้ามแก้ contract กลาง
```

กฎที่ตามมา:

1. แก้ contract ต้องมี ADR ใน `decisions/` — ตามแบบ `devfactory-core/GOVERNANCE.md`
2. repo ลูกที่อยากเปลี่ยน contract ต้องเปิด issue ที่ `agent-platform` ไม่ใช่แก้ในบ้านตัวเอง
3. `devfactory-core` RFC 0001–0004 ที่ยกมาเป็น canonical ต้อง **ตกลงกับ Architecture Owner ต้นทางก่อน** และบันทึกว่า authority ย้ายมาแล้ว
4. contract ที่ยังไม่ผ่านขั้นนี้ให้ marked `Status: Draft` ใน `contracts/` เพื่อไม่ให้ใครเข้าใจผิดว่าใช้ได้

* ✅ มีจุดเดียวที่เป็นความจริง
* ❌ ต้องคุยกับ owner ของ `devfactory-core` ก่อน — เป็นงานคน ไม่ใช่งานเอกสาร

### B2. Federated — แต่ละ repo เป็นเจ้าของ contract ของ domain ตัวเอง แล้ว platform รวม index

* ✅ ทีมเดินเร็ว ไม่ต้องรอ approve
* ❌ กลับไปสู่ปัญหาเดิม (schema เดียวกันคนละ field) ซึ่งเป็นเหตุผลที่สร้าง repo นี้

### C2. แยกตาม semantics / wire schema ⭐ (เพิ่มเมื่อ 2026-08-18)

เสนอโดย Architecture Owner ของ `devfactory-core` ใน [RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) เมื่อเราถามเป็นคำถามสองทาง (A2 หรือ B2)

| ใคร | ถืออะไร |
| --- | --- |
| repo ต้นทาง | **semantics** — vocabulary (`APPROVE`/`REJECT`/`REQUIRE_CHANGES` · event types 7 ตัว) และ guarantees |
| `agent-platform` | **canonical wire schema** — field name, type, JSON Schema, `$ref`, versioning, conformance suite, consumer registry |

* ✅ **A2 กับ B2 ผิดแบบเดียวกัน** — มองว่า *ความหมาย* กับ *รูปร่างบน wire* เป็นก้อนเดียวที่แยกไม่ได้
* ✅ ปัญหาที่ ADR นี้ตั้งใจแก้ ("schema เดียวกันคนละ field") เป็น **schema failure** — รวมศูนย์ schema ก็แก้ได้แล้ว ไม่จำเป็นต้องรวมศูนย์ semantics ด้วย
* ✅ `no execution without APPROVE` เป็น direction lock ของ repo ต้นทาง ไม่ใช่รายละเอียดการ serialize — ถ้ายกทั้งก้อน ความหมายของ `APPROVE` จะแก้ได้ผ่าน ADR ของ repo อื่น
* ✅ platform เพิ่ม field ที่ repo ต้นทาง **ไม่มีความเห็นด้วย** (`tenant_id` `correlation_id` …) ได้เองโดยไม่ต้องต่อคิว review cycle ของเขา
* ⚠️ ต้องมีกลไกกัน drift ที่ตรวจได้ด้วยเครื่อง ไม่ใช่ความไว้ใจ → `derived_from` ด้านล่าง

## กติกา conformance (บังคับ)

ADR-0001 ระบุว่า contract-only มีความเสี่ยง drift — กติกานี้เป็นกลไกกัน drift และเป็น **ข้อบังคับของ consumer ทุกตัว** ไม่ใช่ข้อแนะนำ

```text
                  agent-platform
                        │
                        │ contract v1
                        ▼
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
 devfactory-core  navi-security-   enterprise-
                     agent          knowledge
        │               │               │
   conformance     conformance     conformance
      test            test            test
```

repo ที่อ้างว่า consume contract **ต้อง** มีทั้ง 3 ข้อ:

1. **manifest** ที่ root — `platform-contract.yaml` ประกาศว่า pin contract อะไรไว้และผล conformance ล่าสุด
2. **conformance test** ที่รันใน CI และ validate payload จริงกับ schema ที่ pin ไว้
3. **release gate** — test fail = ปล่อยไม่ได้ และต้องอัปเดต `last_verified` ทุกครั้งที่รันผ่าน

repo ที่ไม่มีครบ 3 ข้อถือว่า **ยังไม่ใช่ consumer** และ platform ไม่รับประกันความเข้ากันได้ให้

### `platform-contract.yaml`

```yaml
platform_contract_version: "0.1"      # รุ่นของ contract set ทั้งชุด

contracts:                            # pin ระดับ major ต่อ contract
  - agent/v1
  - execution/v1
  - policy/v1
  - event/v1

conformance:
  status: passing                     # passing | failing | unknown | waived
  last_verified: 2026-08-17           # วันที่ CI รันผ่านล่าสุด
```

| field | บังคับ | ความหมาย |
| --- | --- | --- |
| `platform_contract_version` | ✅ | รุ่นของ contract set ที่ยึด — ใช้ตอบว่า repo นี้ตามหลังกี่รุ่น |
| `contracts[]` | ✅ | รายการ `<name>/v<N>` ที่ pin · ประกาศเฉพาะที่ใช้จริง ไม่ใช่ทั้งหมด |
| `conformance.status` | ✅ | `passing` / `failing` / `unknown` (ยังไม่เคยรัน) / `waived` (ยกเว้นชั่วคราว ต้องมี ADR หรือ issue อ้าง) |
| `conformance.last_verified` | ✅ | ถ้าเก่ากว่า 90 วัน platform ถือเป็น `unknown` ไม่ว่าเขียนว่า passing |

`last_verified` เป็น field ที่ทำให้ตารางสถานะมีความหมาย — `status: passing` ที่ไม่มีวันที่บอกไม่ได้ว่าผ่านเมื่อไหร่และยังจริงอยู่หรือไม่

### ตารางสถานะ consumer

platform รวม manifest ของทุก repo ไว้ที่ [`architecture/consumers.md`](../architecture/consumers.md) เพื่อตอบ 2 คำถามที่ตอบไม่ได้ถ้าไม่มี registry:

```text
ใครยังไม่ conform            → ต้องตามใคร ก่อนปล่อย contract version ใหม่
vN ยังมีใคร pin อยู่ไหม       → ปิด vN ได้หรือยัง
```

ตัวอย่างสิ่งที่ตารางต้องบอกได้:

```text
devfactory-core        ✓ passing   agent/v1 execution/v1
navi-security-agent    ✓ passing   event/v1 policy/v1
enterprise-knowledge   ✓ passing   tool/v1
farm-agent             ? unknown   —
```

### นิยาม breaking change

เปลี่ยนอย่างใดอย่างหนึ่งต่อไปนี้ = breaking → ขึ้น major ใหม่:

```text
ลบ field · เปลี่ยนชื่อ field · เปลี่ยน type
เพิ่ม required field ใหม่ · เปลี่ยน field จาก optional → required
ลบค่าออกจาก enum · เปลี่ยนความหมายของค่าเดิม
เปลี่ยน default ที่ทำให้พฤติกรรมเดิมเปลี่ยน
เข้มขึ้นใน validation (เช่น ลด maxLength, เพิ่ม pattern)
```

ไม่ breaking (ทำได้ภายใน major เดิม):

```text
เพิ่ม optional field · เพิ่มค่าใน enum ที่ consumer ต้องเผื่อไว้แล้ว
ผ่อน validation · เพิ่มเอกสาร/ตัวอย่าง
```

### Compatibility

* consumer ต้องเผื่อ **unknown field** ได้ — ห้าม fail เมื่อเจอ field ที่ยังไม่รู้จัก
* consumer ต้องเผื่อ **unknown enum value** โดย fallback ที่ปลอดภัย (สำหรับ policy/risk ให้ fallback ไปทาง deny/escalate ไม่ใช่ allow)
* producer ห้ามพึ่งพาว่า consumer จะอ่าน field ใหม่ได้ทันที

### Deprecation

```text
ประกาศ deprecated ใน CHANGELOG + field flag
        ↓  ต่ำสุด 1 minor release และแจ้ง consumer ที่ pin ไว้ทุกตัว
ยังต้องรองรับต่อไปควบคู่ version ใหม่
        ↓  ต่ำสุด 90 วันหลัง vN+1 พร้อมใช้
ปิด vN ได้เมื่อ consumer ทุกตัวย้ายครบ (ตรวจจาก architecture/consumers.md)
```

vN ที่ยังมี consumer pin อยู่ **ห้ามปิด** ไม่ว่าครบกำหนดหรือไม่

## Decision

ADR นี้มี **2 การตัดสินใจ** ที่เคาะคนละวัน — ส่วนที่ 2 ค้างอยู่ 1 วันเพราะต้องรอ repo ต้นทางตอบ

### ส่วนที่ 1 — Versioning · `Accepted (2026-08-17)` ✅

**A** — directory per major (`contracts/<name>/vN/`) + additive-only ภายใน major · กติกา conformance, นิยาม breaking change และ deprecation window ตามหัวข้อด้านบนมีผลบังคับทันที

**Reason:** consumer pin version ได้ตรง ๆ และตรวจอัตโนมัติได้ว่าไม่มีการเผลอ breaking · รองรับ 2 version พร้อมกันช่วงย้าย · ปฏิเสธ C เพราะต้องมี service ซึ่งขัด ADR-0001

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### ส่วนที่ 2 — Ownership · `Accepted (2026-08-18)` ✅

**C2 — แยกตาม semantics / wire schema** · Accepted 2026-08-18

| ใคร | ถืออะไร |
| --- | --- |
| repo ต้นทางของ RFC | **semantics** — vocabulary และ guarantees |
| `agent-platform` | **canonical wire schema** — field name/type · JSON Schema · `$ref` · versioning · conformance suite · consumer registry |

**Reason:** เราถามเป็นคำถามสองทาง (A2 หรือ B2) และ Architecture Owner ของ `devfactory-core` ตอบว่าทั้งสองทางผิดแบบเดียวกัน — ปัญหา "schema เดียวกันคนละ field" ที่ ADR นี้ตั้งใจแก้เป็น *schema failure* การรวมศูนย์ schema แก้ได้แล้วโดยไม่ต้องรวมศูนย์ semantics ด้วย · ส่วน `no execution without APPROVE` เป็น direction lock ของ repo ต้นทาง ไม่ใช่รายละเอียดการ serialize

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform` · ฝั่ง semantics ตัดสินโดย Architecture Owner ของ `devfactory-core` ผ่าน [RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md)

### กฎ 5 ข้อที่ทำให้เส้นแบ่งอยู่ได้

1. **field ระดับ platform เพิ่มได้เอง** — `tenant_id` `workspace_id` `execution_id` `agent_id` `correlation_id` `policy_id` `expires_at` `action_risk` `escalation_target` cost attribution · ผ่าน ADR ฝั่งนี้อย่างเดียว ไม่ต้องมี RFC ที่ต้นทาง
2. **semantic change ต้องมี RFC ที่ต้นทางก่อน** — 5 ประเภท: เพิ่ม/ลบ/เปลี่ยนชื่อ decision หรือ event type · ลดหรือถอน guarantee · เปลี่ยน field ที่มีความหมายจาก required ↔ optional · เปลี่ยนความหมายของ decision/event/state ที่มีอยู่ · เปิดทางให้ execution เดินได้โดยไม่มี `APPROVE`
3. **ทุก derived contract ต้องมี `derived_from`** — ดูหัวข้อถัดไป
4. **ไม่มี schema ขนานที่ต้นทาง** — repo ต้นทาง consume schema ที่ publish แล้วตรง ๆ · RFC ของเขาเป็น intent spec ไม่ใช่ wire format
5. **escalation ชัด** — semantics ตัดสินสุดท้ายที่ Architecture Owner ของ repo ต้นทาง · schema shape กับ versioning ตัดสินสุดท้ายที่ `agent-platform` · ไม่มีใครตัดสินครึ่งของอีกฝ่ายได้เอง

### `derived_from` — pin `semantics_version` ไม่ใช่ commit SHA

RFC-0005 Rule 3 ฉบับแรกให้ pin commit SHA ของไฟล์ RFC · **แก้แล้วโดยต้นทางเอง** เพราะ RFC เป็น prose:

* แก้คำผิด → SHA เปลี่ยน แต่ไม่มีอะไร drift → false alarm
* แก้ enum ที่ frozen → SHA เปลี่ยนเท่ากันพอดี → แยกจากกรณีแรกไม่ออก

จึง pin `semantics_version` ของ [`contract-semantics.yaml`](https://github.com/monthop-gmail/devfactory-core/blob/main/contract-semantics.yaml) แทน ซึ่งขยับเฉพาะเมื่อ `frozen` ขยับ

```yaml
derived_from:
  repo: monthop-gmail/devfactory-core
  manifest: contract-semantics.yaml
  semantics_version: "1.0"
  rfcs: [rfcs/0002-governance-decision-contract.md]
  license: MIT
```

contract ที่ `derived_from` ชี้ไปยัง `semantics_version` ที่ไม่ตรงกับต้นทางแล้ว = **out of conformance** ไม่ว่า `CHANGELOG.md` จะเขียนว่าอะไร

### ตอบคำถามที่ต้นทางถามกลับ

**ถาม: check `derived_from` อัตโนมัติใน CI หรือตรวจตอน contract change ก็พอ?**

**ตอบ: ตรวจตอน contract change ก่อน · ยังไม่ทำ CI** — เหตุผลคือ ADR-0008 ห้ามมี implementation ใน repo นี้ และ workflow ที่ fetch manifest ของ repo อื่นมา hash เป็น code ที่ต้องดูแล ไม่ใช่ contract · ตอนนี้มี derived contract แค่ 2 ตัวและ `semantics_version` ยังเป็น `1.0` ทั้งคู่ ต้นทุนการตรวจด้วยคนยังต่ำกว่าต้นทุนการมี code ก้อนแรกใน repo

ทบทวนใหม่เมื่อเข้าเงื่อนไขข้อใดข้อหนึ่ง: derived contract เกิน 5 ตัว · มี repo ต้นทางมากกว่าหนึ่งแห่ง · หรือเคยพลาดจน `semantics_version` ค้างจริงหนึ่งครั้ง

ต้นทางเตรียม `hash_scope: frozen` ไว้ให้แล้วถ้าวันหนึ่งจะทำ

**ถาม: `subject_type: job` + `subject_id` ทำให้ `job_id` ซ้ำซ้อนไหม?**

**ตอบ: ไม่ซ้ำ เก็บทั้งคู่** — เป็นคนละคำถาม · `job_id` คือ *สายเหตุ* (งานแม่) ส่วน `subject_id` คือ *หัวเรื่อง* · event `EXECUTION_STARTED` มี subject เป็น execution แต่ `job_id` เป็น job ที่มันสังกัด ถ้ารวมเป็นค่าเดียวจะตอบคำถามใดคำถามหนึ่งไม่ได้

เพิ่มกฎระดับ schema: ถ้า `subject_type: job` และมี `job_id` ทั้งสองค่าต้องตรงกัน

## Consequences

* `contracts/*/vN/CHANGELOG.md` เป็นสิ่งบังคับ
* ทุก contract มี field `contract_version` ใน payload เพื่อให้ audit ย้อนได้ว่าใช้เวอร์ชันไหน
* repo ลูก **ต้อง** มี `platform-contract.yaml` + conformance test ใน CI ตามกติกาด้านบน — repo ที่ไม่มีไม่ถือเป็น consumer
* `contracts/approval/` และ `contracts/event/` เขียนได้แล้ว — ต้องมีบล็อก `derived_from` ทุกตัว
* contract ที่ derive มาต้องกำกับ 🔒 ที่ส่วนซึ่งเป็น semantics เพื่อไม่ให้ใครแก้โดยไม่รู้ว่าต้องผ่าน RFC ที่ต้นทาง
* platform ต้องเก็บ [`architecture/consumers.md`](../architecture/consumers.md) ให้เป็นปัจจุบัน — ตัดสินใจปิด vN ไม่ได้ถ้าไม่รู้ว่าใคร pin อยู่
* `waived` ต้องมีวันหมดอายุ — ยกเว้นถาวรไม่มี ถ้าจะยกเว้นนานกว่า 1 major ต้องเขียน ADR

## สถานะ ref เทียบกับ contract

| ที่เก็บ | ผลผูกพัน |
| --- | --- |
| `ref/` | ❌ บันทึกดิบตามเวลา ขัดกันเองได้ ไม่ผูกพัน |
| `decisions/` (Accepted) | ✅ ผูกพัน — เป็น authority ของศัพท์และขอบเขต |
| `contracts/` (Accepted version) | ✅ ผูกพัน — repo ลูกต้องทำตาม |
| `architecture/` | 📄 อธิบาย ไม่ผูกพัน แต่ต้องไม่ขัด ADR |

## Sources

`devfactory-core/GOVERNANCE.md` · `devfactory-core/docs/governance/CORE_BOUNDARY.md` · [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) §5, §6
