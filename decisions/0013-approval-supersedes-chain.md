# ADR-0013: `approval/v1` — field สำหรับห่วงโซ่การเปลี่ยนใจ

**Status:** Accepted (2026-08-19)
**Date:** 2026-08-19
**Depends on:** [ADR-0006](0006-contract-versioning.md) · [ADR-0010](0010-risk-approval-taxonomy.md)
**Blocking:** [issue #22](https://github.com/monthop-gmail/agent-platform/issues/22) · `contracts/approval/v1/approval.schema.yaml`

## Context

[`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) พบระหว่าง implement Governance Decision Interface ([devfactory-core#5](https://github.com/monthop-gmail/devfactory-core/issues/5)) ว่า `approval/v1` มี **guarantee ที่ schema ไม่มี field ให้ทำตาม** ([#22](https://github.com/monthop-gmail/agent-platform/issues/22))

guarantee ข้อแรกในบล็อก 🔒 frozen ของ `approval.schema.yaml`:

> "decision เป็น immutable — แก้ไม่ได้หลังบันทึก · **การเปลี่ยนใจคือ approval ใบใหม่ที่อ้างใบเดิม**"

แต่ไล่ `properties` ครบทุกตัวแล้ว — `approval_id` `tenant_id` `workspace_id` `subject` `execution_id` `agent_id` `decision` `reason` `authority` `decided_at` `policy_id` `action_risk` `expires_at` `escalation_target` — **ไม่มีตัวไหนอ้างใบเดิมได้** · `grep -rn supersede contracts/` ได้ 0 ผลลัพธ์

```text
guarantee บังคับ:  ใบใหม่ต้องอ้างใบเดิม
schema ให้:        ไม่มีที่ให้อ้าง
        ↓
consumer ที่ทำตาม guarantee เขียนใบใหม่ที่บอกไม่ได้ว่าแทนใบไหน
        ↓
audit ตอบได้ว่า "มี approval สองใบกับเรื่องเดียวกัน" แต่ตอบไม่ได้ว่าใบไหนแทนใบไหน
```

นี่เป็นความล้มเหลวชนิดเดียวกับ [#17](https://github.com/monthop-gmail/agent-platform/issues/17) (`event_type` ที่ description บอกว่าชุดเปิดแต่ `enum` ยังปิด) — **schema ขัดกับสิ่งที่ตัวเองเขียนไว้ในไฟล์เดียวกัน** และเจอเพราะมีคน implement จริง ไม่ใช่เพราะอ่านทวน

`devfactory-core` ใส่ `supersedes_decision_id` ในฝั่งตัวเองไปก่อนแล้ว (schema ไม่ได้ปิด `additionalProperties`) พร้อมคอมเมนต์กำกับว่าเป็นการเติมช่องที่สัญญายังไม่มี และขอชื่อจริงจากฝั่งนี้เพื่อไม่ต้อง migrate สองรอบ — **ยิ่งช้ายิ่งแพง** เพราะ field ที่อยู่นอกสัญญาจะกลายเป็นสิ่งที่ consumer รายที่สองลอกไปโดยไม่รู้ว่าไม่ใช่ของกลาง

### ทำไมไม่ต้องรอ RFC ที่ต้นทาง

[ADR-0006 กฎข้อ 1](0006-contract-versioning.md) (จาก [RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) Rule 1):

> **field ระดับ platform เพิ่มได้เอง** — `tenant_id` `workspace_id` `execution_id` `agent_id` `correlation_id` `policy_id` `expires_at` `action_risk` `escalation_target` cost attribution · **ผ่าน ADR ฝั่งนี้อย่างเดียว ไม่ต้องมี RFC ที่ต้นทาง**

และ semantic change 6 ประเภทใน Rule 2 — ลบ/เปลี่ยนชื่อ/เปลี่ยนความหมาย decision หรือ event type · เพิ่ม decision type · ลดหรือถอน guarantee · เปลี่ยน field required ↔ optional · เปลี่ยนความหมายของ decision/event/state ที่มีอยู่ · เปิดทางให้ execution เดินโดยไม่มี `APPROVE` — **ไม่มีข้อไหนตรงกับการเพิ่ม optional field**

การเพิ่ม field นี้จึงเป็น *wire schema* ล้วน ๆ ซึ่งเป็นของ `agent-platform` ตาม ADR-0006 C2 · guarantee ไม่ขยับแม้แต่ตัวอักษรเดียว — ตรงกันข้าม field นี้มีอยู่**เพื่อให้ guarantee ที่ frozen ทำตามได้**

## Options

### A. เพิ่ม optional `supersedes_approval_id` ⭐

* ✅ ปิดช่องว่างระหว่าง guarantee กับ schema โดยไม่แตะ guarantee
* ✅ additive ล้วน — payload เดิมที่ไม่มี field นี้ยัง valid ทุกใบ
* ✅ ชื่อสอดคล้องกับ `approval_id` ที่มันชี้ไป และกับ `supersedes_job_id` ที่ `devfactory-core` ใช้ใน RFC-0007 อยู่แล้ว
* ❌ JSON Schema ตรวจไม่ได้ว่าใบที่อ้างมีอยู่จริง / ไม่เป็นวง — ต้องพึ่งผู้ผลิต

### B. ใช้ชื่อ `supersedes_decision_id` ตามที่ `devfactory-core` ใส่ไปก่อนแล้ว

* ✅ ฝั่งเขาไม่ต้อง rename
* ❌ **ผิดกับสิ่งที่มันชี้ไป** — ค่าที่ใส่คือ `approval_id` ไม่ใช่ id ของ `decision` (ซึ่งเป็น enum ไม่มี id) · ADR-0006 ให้ field naming เป็นของที่นี่ก็เพื่อกันชื่อแบบนี้
* ❌ `decision` เป็นคำที่ `policy/v1` ใช้กับผลประเมินของเครื่องด้วย — ชื่อนี้จะอ่านได้สองแบบข้าม contract

### C. ทำเป็น object `supersedes: {approval_id, reason}`

* ✅ บันทึกได้ว่าทำไมถึงเปลี่ยนใจ แยกจาก `reason` ของคำตัดสินใหม่
* ❌ `reason` ที่มีอยู่เป็น required และ 🔒 required meaning อยู่แล้ว — *"เหตุผลที่ตัดสินอย่างนั้น"* ครอบเหตุผลที่เปลี่ยนใจอยู่แล้ว · เพิ่ม reason ที่สองคือเปิดทางให้เขียนคนละเรื่องในสองที่
* ❌ โครงสร้างซ้อนโดยไม่จำเป็น ต่างจาก field อื่นทั้งหมดในไฟล์นี้ที่เป็น scalar `$ref`

### D. ไม่เพิ่ม field — ให้ผูกห่วงโซ่ผ่าน `event/v1` `GOVERNANCE_DECISION` แทน

* ✅ ไม่แตะ `approval/v1`
* ❌ ทำให้ approval record อ่านคนเดียวไม่รู้เรื่อง — ต้องมี event store อยู่ด้วยเสมอถึงจะตอบได้ว่าใบนี้แทนใบไหน
* ❌ guarantee เขียนว่า *"approval ใบใหม่ที่อ้างใบเดิม"* — ผู้ที่อ้างคือ approval ไม่ใช่ event

### E. บังคับเป็น required เมื่อ `decision` ต่างจากใบก่อนหน้า

* ❌ **schema ไม่รู้ว่ามีใบก่อนหน้าหรือไม่** — เป็นข้อเท็จจริงของ store ไม่ใช่ของ payload
* ❌ ทำให้ payload เดิมทั้งหมด invalid ทันที = breaking ตาม ADR-0006 · และ "เปลี่ยน field จาก optional → required" เป็น semantic change ตาม Rule 2 ข้อ 4 ต้องมี RFC ที่ต้นทาง

## ทำไม optional — และทำไมมันยังพอ

approval **ใบแรก**ของเรื่องหนึ่งไม่มีใบให้อ้าง ถ้าบังคับ required ทุกใบต้องมีค่าปลอม ซึ่งแย่กว่าไม่มี field

การบังคับที่แท้จริงอยู่ที่ **description ไม่ใช่ `required`**: *ต้องมีเมื่อเป็นการเปลี่ยนใจ* · ไม่มี field นี้ = **อ้างว่าเป็นใบแรก** ไม่ใช่ *ไม่ระบุ* — ความหมายนี้เขียนไว้ในตัว schema เพื่อไม่ให้เป็นค่ากำกวมแบบที่ ADR-0012 ตั้งข้อสังเกตกับ `expires_at: null`

invariant ที่เหลือ JSON Schema ตรวจให้ไม่ได้ ผู้ผลิตต้องบังคับเอง และเขียนกำกับไว้ในตัว field:

```text
ใบที่อ้างถึงต้องมีอยู่จริง · tenant เดียวกัน · subject เดียวกัน
ห้ามชี้ตัวเอง · ห้ามเป็นวง
ใบเดิมยังคงอยู่และห้ามแก้ — การมีใบใหม่ไม่ได้ลบใบเก่า
```

ข้อสุดท้ายคือหัวใจ · ถ้า implementation ตีความว่า "แทน" = "เขียนทับ" guarantee ข้อแรกจะพังทั้งที่ field ครบ

## Decision

**A** — เพิ่ม optional property `supersedes_approval_id` ใน `contracts/approval/v1/approval.schema.yaml` โดย `$ref` ไปที่ `identity/v1#/$defs/Id` เหมือน `approval_id` ที่มันชี้ไป · **ไม่เข้า `required`** · **บล็อก `guarantees` ไม่ขยับ**

**Reason:** guarantee ที่ frozen บังคับให้ใบใหม่อ้างใบเดิมอยู่แล้ว — สัญญาที่บังคับสิ่งที่ตัวเองไม่มีที่ให้ทำ คือสัญญาที่ consumer ทำตามไม่ได้ไม่ว่าตั้งใจแค่ไหน · การเพิ่ม optional field เป็น wire schema ล้วน ซึ่ง [ADR-0006 กฎข้อ 1](0006-contract-versioning.md) ให้ทำผ่าน ADR ที่นี่ได้เอง และไม่ตรงกับ semantic change ข้อใดใน 6 ข้อของ Rule 2 · ปฏิเสธ B เพราะค่าที่ใส่คือ `approval_id` ไม่ใช่ id ของ `decision` และ `decision` ชนกับคำเดียวกันใน `policy/v1` · ปฏิเสธ E เพราะ schema ไม่มีทางรู้ว่ามีใบก่อนหน้า และ optional → required เป็น semantic change ที่ต้องมี RFC ที่ต้นทาง

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### ไม่ bump major — อยู่ใน `v1` เดิม

[ADR-0006 นิยาม breaking change](0006-contract-versioning.md) ระบุ **"เพิ่ม optional field"** ไว้ในลิสต์ *ไม่ breaking* ตรง ๆ และการเปลี่ยนนี้ไม่ตรงกับข้อใดในลิสต์ breaking เลย:

| เกณฑ์ breaking ของ ADR-0006 | การเปลี่ยนนี้ |
| --- | --- |
| ลบ field · เปลี่ยนชื่อ field · เปลี่ยน type | ❌ ไม่มี field เดิมถูกแตะ |
| เพิ่ม required field ใหม่ · optional → required | ❌ `required` ไม่ขยับ (7 ตัวเท่าเดิม) |
| ลบค่าออกจาก enum · เปลี่ยนความหมายของค่าเดิม | ❌ `$defs.Decision` ยัง 3 ค่าเท่าเดิม |
| เปลี่ยน default ที่ทำให้พฤติกรรมเดิมเปลี่ยน | ❌ ไม่มี default |
| เข้มขึ้นใน validation | ❌ ผ่อนอย่างเดียว — field ใหม่ที่ไม่บังคับ |

payload ที่ valid กับ `v1.0.1` **ยัง valid ทุกใบ** · consumer ที่ยังไม่อ่าน field นี้ไม่พัง เพราะ ADR-0006 Compatibility บังคับให้ consumer เผื่อ unknown field ไว้แล้ว · จึงเป็น `v1.1.0` ใน `CHANGELOG.md` โดยไม่สร้าง `v2/`

`derived_from.semantics_version` **ยัง `"1.1"`** — ต้นทางไม่ขยับเพราะ `frozen` ไม่ขยับ

## Consequences

* `contracts/approval/v1/approval.schema.yaml` เพิ่ม `supersedes_approval_id` · `CHANGELOG.md` → `v1.1.0`
* `devfactory-core` rename `supersedes_decision_id` → `supersedes_approval_id` ได้ตามที่แจ้งไว้ใน [#22](https://github.com/monthop-gmail/agent-platform/issues/22) — ตอบกลับที่ issue นั้นว่าชื่อจริงคืออะไร ก่อนที่ payload ที่ใช้ชื่อเก่าจะสะสม
* `planes/policy.md` บันทึกว่าการเปลี่ยนใจ = ใบใหม่ที่อ้างใบเดิม ไม่ใช่การแก้ใบเดิม
* **drift check ไม่ครอบคลุมข้อนี้** — `check_frozen` เทียบ vocabulary กับจำนวน guarantee เท่านั้น ตรวจไม่ได้ว่า guarantee แต่ละข้อมี field รองรับหรือไม่ · ช่องว่างนี้เจอด้วยคนที่ implement จริง และจะเจอแบบเดิมอีกถ้ามี guarantee ใหม่ที่ต้องการ field · ขอบเขตของ `conformance/` ถูกจำกัดโดย [ADR-0011](0011-conformance-automation.md) — การขยายให้ตรวจข้อนี้ต้องประเมินแยก ไม่ทำใน ADR นี้
* ครึ่งหลังของ [#22](https://github.com/monthop-gmail/agent-platform/issues/22) (`REQUIRE_CHANGES` ไม่มีปลายทางใน state machine) **ปิดที่ฝั่ง `devfactory-core`** ด้วย RFC-0011 ที่เลือกทาง `GOVERNANCE_ANALYSIS → DRAFT` — ไม่เพิ่ม vocabulary ใหม่ จึงไม่มีอะไรต้องแก้ที่ contract นี้

## Sources

[issue #22](https://github.com/monthop-gmail/agent-platform/issues/22) · [devfactory-core#5](https://github.com/monthop-gmail/devfactory-core/issues/5) · [ADR-0006 กฎข้อ 1 + นิยาม breaking change](0006-contract-versioning.md) · [RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) Rule 1 · [`contract-semantics.yaml`](https://github.com/monthop-gmail/devfactory-core/blob/main/contract-semantics.yaml) `platform_may_add_freely`
