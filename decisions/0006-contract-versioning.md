# ADR-0006: Contract Versioning & Ownership

**Status:** Proposed
**Date:** 2026-08-17
**Depends on:** ADR-0001
**Blocking:** `contracts/` ทั้งหมด

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

repo ที่อ้างว่า consume contract ต้องมี:

1. ไฟล์ประกาศ version ที่ใช้ — `contract.lock` (หรือเทียบเท่า) ระบุ `contracts/<name>/v<N>` ที่ pin ไว้
2. conformance test ที่รันใน CI และ validate payload จริงกับ schema ที่ pin
3. ผลลัพธ์ test เป็นเงื่อนไขของ release — fail = ปล่อยไม่ได้

repo ที่ไม่มี 3 ข้อนี้ถือว่า **ยังไม่ใช่ consumer** และ platform ไม่รับประกันความเข้ากันได้ให้

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
ปิด vN ได้เมื่อ consumer ทุกตัวย้ายครบ (ตรวจจาก contract.lock)
```

vN ที่ยังมี consumer pin อยู่ **ห้ามปิด** ไม่ว่าครบกำหนดหรือไม่

## Decision

> _(รอเคาะ — ต้องตอบ 2 ส่วน: รูปแบบ version และความเป็นเจ้าของ)_

## Consequences ถ้าเลือก A + A2

* `contracts/*/vN/CHANGELOG.md` เป็นสิ่งบังคับ
* ทุก contract มี field `contract_version` ใน payload เพื่อให้ audit ย้อนได้ว่าใช้เวอร์ชันไหน
* repo ลูก **ต้อง** มี `contract.lock` + conformance test ใน CI ตามกติกาด้านบน — repo ที่ไม่มีไม่ถือเป็น consumer
* ต้องนัดคุยกับ Architecture Owner ของ `devfactory-core` ก่อนเขียน `contracts/approval/` และ `contracts/event/`
* platform ต้องเก็บ **consumer registry** — รู้ว่า repo ไหน pin version ไหน ไม่งั้นตัดสินใจปิด vN ไม่ได้ (เก็บที่ `architecture/consumers.md`)

## สถานะ ref เทียบกับ contract

| ที่เก็บ | ผลผูกพัน |
| --- | --- |
| `ref/` | ❌ บันทึกดิบตามเวลา ขัดกันเองได้ ไม่ผูกพัน |
| `decisions/` (Accepted) | ✅ ผูกพัน — เป็น authority ของศัพท์และขอบเขต |
| `contracts/` (Accepted version) | ✅ ผูกพัน — repo ลูกต้องทำตาม |
| `architecture/` | 📄 อธิบาย ไม่ผูกพัน แต่ต้องไม่ขัด ADR |

## Sources

`devfactory-core/GOVERNANCE.md` · `devfactory-core/docs/governance/CORE_BOUNDARY.md` · [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) §5, §6
