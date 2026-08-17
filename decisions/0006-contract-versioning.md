# ADR-0006: Contract Versioning & Ownership

**Status:** **แยก 2 ส่วน** — Versioning: `Accepted (2026-08-17)` · Ownership: `Pending external confirmation`
**Date:** 2026-08-17
**Depends on:** ADR-0001
**Blocking:** `contracts/` ทั้งหมด (ส่วน versioning) · contract ที่อ้าง `devfactory-core` RFC (ส่วน ownership)

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

ADR นี้มี **2 การตัดสินใจที่ status ต่างกัน** — อย่ารายงานรวมกัน

### ส่วนที่ 1 — Versioning · `Accepted (2026-08-17)` ✅

**A** — directory per major (`contracts/<name>/vN/`) + additive-only ภายใน major · กติกา conformance, นิยาม breaking change และ deprecation window ตามหัวข้อด้านบนมีผลบังคับทันที

**Reason:** consumer pin version ได้ตรง ๆ และตรวจอัตโนมัติได้ว่าไม่มีการเผลอ breaking · รองรับ 2 version พร้อมกันช่วงย้าย · ปฏิเสธ C เพราะต้องมี service ซึ่งขัด ADR-0001

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### ส่วนที่ 2 — Ownership · `Pending external confirmation` ⏳

**A2 ยังไม่ Accepted** — `agent-platform` **ยังไม่ใช่** canonical owner ของ shared contract จนกว่าจะได้รับการยืนยันจาก Architecture Owner ของ `devfactory-core`

**เหตุผลที่ยังไม่เคาะ:** RFC-0001–0004 ของ `devfactory-core` เป็น `Status: Draft` และ `GOVERNANCE.md` ของ repo นั้นระบุว่า **Architecture Owner ของมันมีอำนาจตัดสินสุดท้าย** — การประกาศเองว่า authority ย้ายมาแล้วคือการยึดอำนาจของอีก repo โดยพลการ ซึ่งขัดกับ governance ที่ ADR ชุดนี้ตั้งขึ้นเอง

**รออะไร:** agreement อย่างเป็นทางการจาก Architecture Owner ของ `devfactory-core` ว่า authority ของ shared contract ย้ายมาที่ `agent-platform`

**ระหว่างรอ — ทำอะไรได้/ไม่ได้:**

| ทำได้ | ทำไม่ได้ |
| --- | --- |
| เขียน contract ที่ **ไม่** อ้าง RFC-0001–0004 ได้เต็มที่ | ประกาศว่า `agent-platform` เป็น canonical owner |
| อ้างอิง RFC ในฐานะ **reference** พร้อมติดสถานะ `external-authority-pending` | ย้าย/แก้ RFC ในนามของ platform |
| ใช้กติกา versioning + conformance ได้ทันที | ปิด ADR-0006 |

contract ที่ได้รับผลกระทบ: `contracts/approval/` (RFC-0002) · `contracts/event/` (RFC-0003) · state machine ที่อ้าง RFC-0001/0004 — ทั้งหมดติดสถานะ **`external-authority-pending`** จนกว่าจะยืนยัน

**การเดินต่อไม่ต้องรอส่วนที่ 2** — ADR อื่นและ contract ที่ไม่พึ่ง RFC เดินได้เลย

## Consequences ถ้าเลือก A + A2

* `contracts/*/vN/CHANGELOG.md` เป็นสิ่งบังคับ
* ทุก contract มี field `contract_version` ใน payload เพื่อให้ audit ย้อนได้ว่าใช้เวอร์ชันไหน
* repo ลูก **ต้อง** มี `platform-contract.yaml` + conformance test ใน CI ตามกติกาด้านบน — repo ที่ไม่มีไม่ถือเป็น consumer
* ต้องนัดคุยกับ Architecture Owner ของ `devfactory-core` ก่อนเขียน `contracts/approval/` และ `contracts/event/`
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
