# ADR-0019: `execution/v1` — ไม่มีที่บันทึกว่าใบอนุมัติไหนอนุญาตให้รัน

**Status:** Accepted (2026-08-21)
**Date:** 2026-08-21
**Depends on:** [ADR-0010](0010-risk-approval-taxonomy.md) · [ADR-0005](0005-agent-runtime-boundary.md) · [ADR-0006](0006-contract-versioning.md) · [ADR-0013](0013-approval-supersedes-chain.md)
**Blocking:** `contracts/execution/v1` · `contracts/approval/v1`

## Context

`approval/v1` `guarantees` ข้อ 3 (🔒 frozen — เป็นของ `devfactory-core` ตาม RFC-0002):

> **"execution ที่ไม่มี APPROVE เป็นสิ่งที่ห้าม"**

`execution/v1` มี `policy_decision` ที่ `$ref` ไป `policy/v1` `Decision` เต็มใบ — จึงบันทึกได้ว่า **ต้องขออนุมัติไหม** (`authority: approval_required` · `human_command_required`)

แต่ไล่ `properties` ครบทุกตัว — `execution_id` `context` `job_id` `execution_mode` `provider_id` `state` `capability_requirement` `policy_decision` `observability_depth` `attempt` `max_attempts` `parent_execution_id` `artifacts` `usage` `error` `created_at` `started_at` `ended_at` — **ไม่มีตัวไหนชี้ไปยังใบอนุมัติได้** · `grep -rn approval contracts/execution/` ได้ 0 ผลลัพธ์

```text
policy ตัดสิน authority: approval_required   →  บันทึกใน execution ✅
มีคนอนุมัติจริง                               →  ไม่มีที่บันทึก ❌
        ↓
execution record ตอบได้ว่า "ต้องขออนุมัติ"
แต่ตอบไม่ได้ว่า "ใครอนุมัติ ใบไหน เมื่อไหร่"
```

**นี่เป็นแผลชนิดเดียวกับ [#22](https://github.com/monthop-gmail/agent-platform/issues/22) และ [ADR-0016](0016-recording-which-consent-allowed-access.md) — ครั้งที่สาม** และเป็นครั้งที่กระทบมากที่สุด เพราะมันคือ **ด่านอำนาจของมนุษย์** ซึ่งเป็นเหตุผลทั้งหมดที่ [ADR-0010](0010-risk-approval-taxonomy.md) แยก `authority` ออกจาก `effect`

สองครั้งก่อนเจอเพราะมีคน implement · ครั้งนี้เจอจากการไล่ `guarantees` ทุกข้อของทุก contract เทียบกับ `properties` อย่างเป็นระบบ — **การไล่แบบนั้นควรทำตั้งแต่ตอนเขียน contract ไม่ใช่ตอนนี้**

## อ่าน guarantee ให้ตรง — ไม่ใช่ทุก execution ต้องมี APPROVE

ถ้าอ่านตามตัวอักษรว่า *execution ทุกใบ* ต้องมี APPROVE จะขัดกับ `authority: auto` ของ [ADR-0010](0010-risk-approval-taxonomy.md) ทันที ซึ่งแปลว่า *ทำได้เลย*

ความหมายที่ถูกคือ: **execution ที่ผ่านด่านซึ่งต้องการอนุมัติ ต้องมี APPROVE จริง ๆ ห้ามข้าม** · การบันทึกจึงจำเป็นเฉพาะเมื่อ `policy_decision.authority` เป็น `approval_required` หรือ `human_command_required`

## ทำไมที่นี่ "เก็บ id ก็พอ" ทั้งที่ ADR-0016 บอกว่าไม่พอ

[ADR-0016](0016-recording-which-consent-allowed-access.md) ปฏิเสธการเก็บแค่ `grant_id` เพราะใบยินยอมที่มี `conditions` **ตอบตัวเองไม่ได้** — ประเมินใหม่ทีหลังได้คำตอบของวันที่ประเมิน ไม่ใช่ของวันที่เข้าถึง

เคสนี้ตรงกันข้าม และเหตุผลอยู่ในสัญญาเอง — `approval/v1` `guarantees` ข้อ 1:

> "decision เป็น immutable — แก้ไม่ได้หลังบันทึก · การเปลี่ยนใจคือ approval ใบใหม่ที่อ้างใบเดิม"

**ใบอนุมัติที่อ่านปีหน้าให้คำตอบเดียวกับที่อ่านวันนี้เสมอ** เพราะมันห้ามเปลี่ยน · ตัวชี้จึงเพียงพอจริง ๆ ที่นี่

บันทึกความต่างนี้ไว้ให้ชัด เพื่อไม่ให้ ADR-0016 ถูกอ่านเป็นกฎเหมารวมว่า *"ห้ามเก็บ id ต้องเก็บผลเสมอ"* — เกณฑ์ที่แท้จริงคือ **สิ่งที่ชี้ไปนั้นเปลี่ยนได้หรือไม่**

## ทำไมบังคับด้วย schema ไม่ได้ — และการพยายามจะทำให้ผิด

น่าจะเขียน `if/then` ว่า *ถ้า `authority: approval_required` แล้วต้องมี `approval_id`* ได้ · **ทำแล้วจะแดงในกรณีที่ถูกต้อง**

`ExecutionState` มี `rejected` · `cancelled` · `timed_out` — execution ที่เข้า `awaiting_approval` แล้ว**ถูกปฏิเสธ ถูกยกเลิก หรือหมดเวลาก่อนมีใครอนุมัติ** เป็นเส้นทางที่ถูกต้องสมบูรณ์ และ **ไม่มี APPROVE ให้ชี้** ตามนิยาม

```text
authority: approval_required + state: rejected   → ไม่มี approval_id ถูกต้อง
authority: approval_required + state: succeeded  → ไม่มี approval_id คือการละเมิด
```

ความต่างอยู่ที่ *เดินผ่านด่านไปแล้วหรือยัง* ซึ่งขึ้นกับ state ที่เปลี่ยนตามเวลา · schema ตรวจ payload ณ ขณะหนึ่ง จึงตรวจข้อนี้ไม่ได้โดยไม่ผลิตสัญญาณลวง — และ **สัญญาณลวงอันตรายพอ ๆ กับการตรวจไม่เจอ** ([ADR-0015](0015-event-sequence-and-trail-closure.md) เจอเหตุผลเดียวกันกับ `sequence` ที่ต่อเนื่อง)

## Options

### A. เพิ่ม optional `approval_id` + เขียนกฎว่าต้องมีเมื่อไหร่ ⭐

* ✅ ปิดช่องว่างระหว่าง guarantee กับ schema โดยไม่แตะ guarantee
* ✅ additive ล้วน — payload เดิมยัง valid ทุกใบ
* ✅ ไม่ผลิตสัญญาณลวงกับ `rejected` / `cancelled` / `timed_out`
* ❌ JSON Schema บังคับไม่ได้ว่าต้องมีตอนไหน — ต้องพึ่งผู้ผลิต เหมือน guarantee อื่นเกือบทั้งหมดของ repo นี้

### B. A + `if/then` บังคับเมื่อ `authority: approval_required`

* ✅ ตรวจได้ด้วย schema
* ❌ **แดงกับ `rejected` · `cancelled` · `timed_out` ซึ่งถูกต้อง** — สัญญาณลวงที่จะทำให้คนเลิกเชื่อ check
* ❌ เข้มขึ้น = breaking ตาม [ADR-0006](0006-contract-versioning.md)

### C. เก็บเป็น object `approval: {approval_id, decided_at, decision}` แบบ `consent/v1` `Evaluation`

* ✅ อ่าน execution ใบเดียวจบ ไม่ต้องเปิดใบอนุมัติ
* ❌ **ซ้ำข้อมูลที่ immutable อยู่แล้ว** — และสำเนาที่ซ้ำได้คือสำเนาที่ drift ได้ ซึ่งเป็นเหตุผลเดียวกับที่ [ADR-0018](0018-policy-result-single-source.md) เพิ่งเลิกทำ
* ❌ `Evaluation` มีเหตุผลเพราะ consent เปลี่ยนได้ · approval เปลี่ยนไม่ได้ เหตุผลนั้นจึงไม่ย้ายมาที่นี่

### D. ไม่แตะ `execution/v1` — ผูกผ่าน event (`subject_type: approval` + `correlation_id`)

* ✅ ไม่แก้ contract
* ❌ ทำให้ execution record อ่านคนเดียวไม่รู้เรื่อง ต้องมี event store อยู่ด้วยเสมอ — เหตุผลเดียวกับที่ [ADR-0013](0013-approval-supersedes-chain.md) ปฏิเสธทางนี้ไปแล้วครั้งหนึ่ง
* ❌ **`approval/v1` ยังไม่มี `correlation_id` ด้วยซ้ำ** (ดูข้างล่าง) การ join จึงยังไม่แน่นอย่างที่คิด

### E. ไม่ทำอะไร

* ❌ guarantee ที่ frozen บังคับสิ่งที่ไม่มีที่ให้ทำตาม — ปล่อยไว้ครั้งที่สามหลังจากแก้มาแล้วสองครั้ง

## พ่วง: `approval/v1` ไม่มี `correlation_id`

contract อื่นเกือบทั้งหมดมี (`event/v1` · `identity/v1` `RequestContext` ที่ `execution/v1` ใช้ผ่าน `context`) แต่ `approval/v1` ไม่มี — จึงผูกใบอนุมัติเข้ากับสายงานข้าม service ได้ยากกว่าที่ควร

[ADR-0006 กฎข้อ 1](0006-contract-versioning.md) ระบุ `correlation_id` เป็น **field ระดับ platform ที่เพิ่มได้เองผ่าน ADR ฝั่งนี้ ไม่ต้องมี RFC ที่ต้นทาง** · แก้รอบเดียวไปพร้อมกันจะได้ไม่ต้องรบกวน consumer สองรอบ

## Decision

**A** — optional `approval_id` ใน `execution/v1` + กฎว่าต้องมีเมื่อไหร่ · พ่วง `correlation_id` ใน `approval/v1`

**Reason:** guarantee ที่ frozen บังคับให้ execution ผ่านด่านด้วย APPROVE จริง แต่ไม่มีที่บันทึกว่าใบไหน — สัญญาที่บังคับสิ่งที่ตัวเองไม่มีที่ให้ทำ คือสัญญาที่ทำตามไม่ได้ไม่ว่าตั้งใจแค่ไหน · เก็บ **id ก็พอที่นี่** เพราะใบอนุมัติเป็น immutable ตาม guarantee ข้อ 1 ของมันเอง ต่างจาก consent ที่ ADR-0016 ต้องแช่แข็งผล · ปฏิเสธ B เพราะจะแดงกับ `rejected`/`cancelled`/`timed_out` ที่ถูกต้อง และสัญญาณลวงอันตรายพอ ๆ กับการตรวจไม่เจอ · ปฏิเสธ C เพราะเป็นสำเนาที่ drift ได้ของข้อมูลที่เปลี่ยนไม่ได้ ซึ่ง ADR-0018 เพิ่งเลิกทำไปหมาด ๆ

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### invariant ที่ผู้ผลิตต้องบังคับเอง

JSON Schema ตรวจให้ไม่ได้ · เขียนกำกับไว้ในตัว field แบบเดียวกับ [ADR-0013](0013-approval-supersedes-chain.md):

```text
ใบที่อ้างต้องมีอยู่จริง · tenant เดียวกัน · subject ตรงกับ execution นี้
decision ของใบนั้นต้องเป็น APPROVE — ใบที่ REJECT หรือ REQUIRE_CHANGES อ้างไม่ได้
ต้องมีก่อนออกจาก awaiting_approval ไปสู่ running
ไม่มีเมื่อจบที่ rejected · cancelled · timed_out = ถูกต้อง ไม่ใช่ข้อมูลขาด
```

ข้อสุดท้ายสำคัญที่สุด — ถ้า implementation ตีความว่า *ไม่มี `approval_id` = ผิดเสมอ* จะเกิดสัญญาณลวงแบบเดียวกับที่ option B จะสร้าง

### ไม่ bump major

| contract | จาก | เป็น | เปลี่ยนอะไร |
| --- | --- | --- | --- |
| `execution/v1` | `v1.0.0` | `v1.1.0` | เพิ่ม optional `approval_id` |
| `approval/v1` 🔗 | `v1.1.0` | `v1.2.0` | เพิ่ม optional `correlation_id` |

optional ทั้งคู่ · `required` ไม่ขยับ · ไม่มีการเข้มขึ้น · `approval/v1` `guarantees` ไม่ขยับ และ `derived_from.semantics_version` ยัง `"1.1"`

## Consequences

* `execution/v1` ตอบได้เองว่าผ่านด่านมาด้วยใบไหน โดยไม่ต้องมี event store อยู่ด้วย
* บันทึกไว้ว่า **เกณฑ์ว่าจะเก็บ id หรือเก็บผลที่แช่แข็ง คือ "สิ่งที่ชี้ไปเปลี่ยนได้ไหม"** ไม่ใช่กฎเหมารวมจาก ADR-0016
* `devfactory-core` pin `execution/v1` อยู่แต่ยังไม่ผลิต payload ของมัน (job state machine อยู่คนละชั้น) — **ไม่มีใครต้อง migrate**
* **drift check ตรวจข้อนี้ไม่ได้** — `check_frozen` เทียบ vocabulary กับจำนวน guarantee เท่านั้น ตรวจไม่ได้ว่าแต่ละ guarantee มี field รองรับหรือไม่ · เป็นช่องเดิมที่ [ADR-0013](0013-approval-supersedes-chain.md) บันทึกไว้แล้วและยังเปิดอยู่ · **ครั้งนี้เป็นครั้งที่สาม จึงควรพิจารณาว่าการไล่ guarantee เทียบ properties ควรเป็นงานประจำหรือไม่ — แยกเป็นเรื่องของตัวเอง ไม่ตัดสินใน ADR นี้**
* ยังไม่ปิด: 16 จาก 20 ไฟล์ schema ไม่มี `guarantees`/`platform_rules` เลย — ตัวที่มี consumer จริงงอกกฎออกมา ตัวที่ยังไม่มีใครใช้ยังเป็น schema เปล่า

## Sources

`approval/v1` `guarantees` ข้อ 1 และ 3 (🔒 `devfactory-core` RFC-0002) · [ADR-0010](0010-risk-approval-taxonomy.md) `authority` · [ADR-0013](0013-approval-supersedes-chain.md) รูปแบบ optional field + invariant ที่ผู้ผลิตบังคับ · [ADR-0016](0016-recording-which-consent-allowed-access.md) เหตุผลที่ *บางที่* เก็บ id ไม่พอ · [ADR-0018](0018-policy-result-single-source.md) สำเนาที่ซ้ำได้คือสำเนาที่ drift ได้ · `ExecutionState` ใน `contracts/execution/v1`
