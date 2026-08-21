# event/v1

## v1.6.1 — 2026-08-21

`derived_from.semantics_version` `1.1` → `1.2` ตามต้นทาง

[RFC-0012](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0012-terminal-closing-record.md) เพิ่ม guarantee ข้อที่สามให้ `event` — **ทุกการจบแบบ terminal ต้องออกใบปิดท้าย ไม่ใช่แค่ทางที่จบสำเร็จ** — ปิดช่องที่ [#23](https://github.com/monthop-gmail/agent-platform/issues/23) ยกมาเอง

* **ไม่มีอะไรใน schema เปลี่ยน** — guarantee เป็นของ `devfactory-core` และ `guarantees` block ในไฟล์นี้เป็นของเรา ซึ่งครอบ 3 ข้อของเขาอยู่แล้ว (8 ≥ 3)
* **ไม่มี field ใหม่** — ใบปิดท้ายเป็น event type ไม่ใช่ field · `event_type` อ้าง `EventTypeName` ชุดเปิด `JOB_SETTLED` จึง validate ผ่านตั้งแต่วันนี้
* ADR-0015 บอกไว้เองว่าครึ่งความครบถ้วนปิดด้วยใบปิดท้าย และเป็น semantics ของเขา — นี่คือครึ่งนั้นกลับมาแล้ว

## v1.6.0 — 2026-08-21

`consent/v1` `consent_rules` ข้อ 2 บังคับให้การให้ · การใช้ · การเพิกถอน ออก audit event ทุกครั้ง แต่ 7 ค่าที่ platform รับรองไม่มีตัวไหนเกี่ยวกับ consent — [ADR-0020](../../../decisions/0020-consent-event-vocabulary.md) option B

* `EventType` +2 — **`CONSENT_GRANTED`** · **`CONSENT_REVOKED`**
* `SubjectType` +1 — **`consent`**

### ⚠️ ไม่มี `CONSENT_USED` โดยเจตนา

การใช้บันทึกด้วย field `consent` (`consent/v1` `$defs.Evaluation`) บน event ที่เกิดการเข้าถึงจริง ซึ่ง [ADR-0016](../../../decisions/0016-recording-which-consent-allowed-access.md) เพิ่มไว้แล้ว

ถ้ามี event type แยกจะเกิด **สองบันทึกของเหตุการณ์เดียวกัน** และที่แย่กว่านั้น — query ด้วย `event_type` จะ **ตกหล่นการใช้ที่บันทึกบน event ของโดเมน ซึ่งเป็นส่วนใหญ่** · query ที่ถูกต้องคือหาจาก `consent.grant_id` ซึ่งครอบทั้งสองแบบอยู่แล้ว

### ทำไม `consent` มีค่าใน `SubjectType` ของตัวเอง

เป็น contract ระดับ platform เหมือน `approval` ที่มีค่าของตัวเองอยู่แล้ว — ไม่ใช่ record ของโดเมนที่ควรไปรวมใน `record` (ซึ่งสงวนไว้ให้บันทึกที่ platform ไม่รู้จักชนิด)

### ทำได้เองไม่ต้องรอ RFC

`contract-semantics.yaml` ของ `devfactory-core` ระบุใน `contracts.event.platform_may_add_freely` ตรง ๆ ว่า **"event type ใหม่"** และ **"subject_type / subject_id"** · `event_types.closed: false`

**`guarantees` ไม่ขยับ** (ยัง 8 ข้อ) · `derived_from.semantics_version` ยัง `"1.1"`

### ไม่ breaking — ผ่อนอย่างเดียว

7 ค่าเดิมของ `EventType` ไม่ขยับ · `SubjectType` รับค่าเพิ่มหนึ่งค่า · field `event_type` ยังผูกกับ `EventTypeName` (ชุดเปิด) เหมือนเดิม

## v1.5.0 — 2026-08-21

`event/v1.policy_result` เคยประกาศรูปของตัวเอง ไม่ได้ `$ref` ไป `policy/v1` — มีสองที่ที่บอกว่า *"ผลของ policy หน้าตาอย่างไร"* และไม่มีอะไรคอยจับว่ายังตรงกัน · `consent` ที่ [ADR-0016](../../../decisions/0016-recording-which-consent-allowed-access.md) เพิ่มเข้า `Decision` ไม่ไหลไปที่นั่นเอง — พิสูจน์แล้วว่าเพี้ยนจริง ไม่ใช่ความเสี่ยงทางทฤษฎี

[ADR-0018](../../../decisions/0018-policy-result-single-source.md) เคาะ option B — **ปัญหาคือประกาศซ้ำ ไม่ใช่ย่อ**

* `policy_result` เปลี่ยนจาก**ประกาศรูปเอง** เป็น `$ref` ไป `policy/v1#/$defs/DecisionSummary`

### ไม่ breaking — และไม่เข้มขึ้นแม้แต่นิดเดียว

`DecisionSummary` ไม่มี `required` เหมือนที่ `policy_result` เดิมไม่มี · **รูปที่ยอมรับเหมือนเดิมเป๊ะ** — ใส่ครบ 4 field · ใส่บางส่วน · หรือ `{}` ก็ยัง valid เหมือนก่อน

ที่เลือกทางนี้แทนการ `$ref` ทั้ง `Decision` เพราะ `Decision.required` มี 4 ตัว ซึ่งจะทำให้ `policy_result` ที่ใส่ไม่ครบกลายเป็น invalid = เข้มขึ้น = breaking ตามตัวอักษรของ [ADR-0006](../../../decisions/0006-contract-versioning.md)

### `consent` จงใจไม่อยู่ใน `policy_result`

event มี `consent` ของตัวเองที่ระดับบนสุดแล้ว (`v1.4.0`) — ใส่ซ้ำสองที่ในบันทึกเดียวคือ drift ที่รอเกิด

**`guarantees` ไม่ขยับ** (ยัง 8 ข้อ) · `derived_from.semantics_version` ยัง `"1.1"`

## v1.4.0 — 2026-08-21

เพิ่ม **ผลการประเมินความยินยอม** ตาม [ADR-0016](../../../decisions/0016-recording-which-consent-allowed-access.md) (option C)

`consent_rules` ข้อ 6 บังคับว่าการเข้าถึงต้องผ่านทั้ง `policy/v1` และ consent แต่ไม่มี record ไหนบอกได้ว่า **อนุญาตด้วยความยินยอมใบไหน** — และหลัง [ADR-0014](../../../decisions/0014-consent-access-time-conditions.md) การเก็บแค่ `grant_id` ก็ยังไม่พอ เพราะใบที่มี `conditions` ตอบตัวเองไม่ได้ ประเมินใหม่ทีหลังจะได้คำตอบของ *วันที่ประเมิน* ไม่ใช่ของ *วันที่เข้าถึง*

* `consent` — optional · `$ref` ไป `consent/v1#/$defs/Evaluation`
* **`guarantees` ไม่ขยับ** (ยัง 8 ข้อ) · `derived_from.semantics_version` ยัง `"1.1"` — เป็น field ระดับ platform ที่ [ADR-0006 กฎข้อ 1](../../../decisions/0006-contract-versioning.md) ให้เพิ่มได้เองโดยไม่ต้องมี RFC ที่ต้นทาง

### บ้านของ audit อยู่ที่นี่

`consent_rules` ข้อ 2 บังคับให้การให้ · การใช้ · และการเพิกถอน ออก event ทุกครั้งอยู่แล้ว แต่ไม่ได้ระบุว่าต้องมีอะไรในนั้น · field นี้ทำให้ event ตอบได้ว่า **ใบไหน** และ **ตอนนั้นเงื่อนไขผ่านจริงไหม** ซึ่งประเมินย้อนหลังไม่ได้

ปิดของค้างที่ [ADR-0014](../../../decisions/0014-consent-access-time-conditions.md) ฝากไว้ — *"`event/v1` บันทึกว่าเงื่อนไขถูกประเมินแล้วและผ่าน"*

### ไม่ breaking

optional · `required` ยัง 7 ตัว · payload ที่ valid กับ `v1.3.0` ยัง valid ทุกใบ

## v1.3.0 — 2026-08-21

เพิ่ม optional `sequence` ตาม [ADR-0015](../../../decisions/0015-event-sequence-and-trail-closure.md) (option C) จาก [issue #23](https://github.com/monthop-gmail/agent-platform/issues/23)

* `sequence` — integer, `minimum: 1` · **สำหรับเรียงเท่านั้น** · ผู้อ่านเรียงด้วย `(occurred_at, sequence)`
* `platform_rules` +2 — ช่องว่างไม่มีความหมาย ห้ามตีความว่ามีใบหาย · event ที่ไม่มี `sequence` เรียงด้วย `occurred_at` อย่างเดียว ห้ามถือว่าอยู่ก่อนหรือหลังใบที่มีโดยอัตโนมัติ
* **`guarantees` ไม่ขยับ** (ยัง 8 ข้อ) · `derived_from.semantics_version` ยัง `"1.1"`

### ปิดอะไร ไม่ปิดอะไร

| ต้องการ | ปิดแล้วไหม |
| --- | --- |
| เรียง event ที่ `occurred_at` เท่ากันเป๊ะ (`care-agent-platform` บน Postgres) | ✅ ปิดด้วย field นี้ |
| จับใบหายกลางทาง | ✅ `devfactory-core` มีอยู่แล้วผ่าน from→to ของ `STATE_TRANSITION` |
| จับ trail ที่ถูกตัดท้าย | ❌ **field นี้ปิดไม่ได้** — ต้องมีใบปิดท้ายหรือ checkpoint |

**เลขลำดับบน event บอกไม่ได้ว่าใบสุดท้ายควรเป็นเลขอะไร** เพราะคำตอบไม่ได้อยู่ในใบไหนเลย · `sequence` เป็นตัวจับช่องว่าง*กลางทาง* ไม่ใช่ตัวจับ*ปลายที่ขาด* · จึงไม่รับข้อเสนอ contiguous-ต่อ-subject ที่จะบังคับให้ทุก consumer serialize การเขียนโดยไม่ได้ปิดช่องที่ผู้ขอยกมา

สอดคล้องกับ guarantee ข้อ 8 ที่มีอยู่แล้ว — *"trace ที่ไม่มี step ย่อยถือว่าถูกต้อง"* — สัญญาบอกอยู่แล้วว่าการไม่มี event ไม่ใช่หลักฐานว่าไม่มีเหตุการณ์

### ไม่ breaking

`required` ยัง 7 ตัวเท่าเดิม · ไม่มี `sequence` = เรียงด้วย `occurred_at` เหมือนเดิม → payload ที่ valid กับ `v1.2.0` ยัง valid ทุกใบ

### ยังไม่ทำในรอบนี้

* **ใบปิดท้ายสำหรับทุกการจบแบบ terminal** (`FAILED` · `CANCELLED` · `TIMED_OUT`) — เป็น semantics ของ `devfactory-core` ต้องมี RFC ที่ต้นทางตาม [ADR-0006](../../../decisions/0006-contract-versioning.md)
* **ตัวตนของผู้ผลิต** — `source` มีแค่ `kind` กับ `system` · การรับประกันระดับ producer จึงยังเขียนลงสัญญาไม่ได้
* **event ที่บันทึกว่าเงื่อนไข consent ถูกประเมินแล้ว** — ฝากมาจาก [ADR-0014](../../../decisions/0014-consent-access-time-conditions.md) เป็นเรื่องเนื้อหาของ event ไม่ใช่ลำดับ

### หมายเหตุการนับเลข — แก้เลขซ้ำที่ค้างอยู่

ไฟล์นี้เคยมี **`v1.1.0` สองอัน** — 2026-08-18 (RFC-0009 ประกาศว่า `EventType` เป็นชุดเปิด) กับ 2026-08-19 ([#17](https://github.com/monthop-gmail/agent-platform/issues/17) แก้ให้ schema ทำตามที่ประกาศ + เพิ่ม `record` ใน `SubjectType`) และ `v1.0.0` ถูกแทรกอยู่ระหว่างกลาง

ตัวหลังเปลี่ยนเป็น **`v1.2.0`** และเรียงใหม่ตามเวลา · รอบนี้จึงเป็น `v1.3.0` ไม่ใช่ `v1.2.0`
ไม่มี consumer รายไหน pin ด้วยเลข semver ของ contract (pin ด้วยชื่อ contract + commit SHA ตาม [ADR-0006](../../../decisions/0006-contract-versioning.md)) การแก้เลขจึงไม่กระทบใคร


## v1.2.0 — 2026-08-19

ไม่ breaking — ผ่อน validation และเพิ่มค่าใน enum เท่านั้น ([ADR-0006](../../../decisions/0006-contract-versioning.md))

- **`event_type` รับค่านอก 7 ตัวได้แล้ว** ([#17](https://github.com/monthop-gmail/agent-platform/issues/17)) — เพิ่ม `$defs.EventTypeName`
  (`type: string` + `pattern`) และให้ field อ้างตัวนั้นแทน `$defs.EventType`
  · `EventType` ยังอยู่เป็นชุดค่าที่ platform รับรองความหมาย ให้ consumer generate constant ได้
  · เดิม description เขียนว่าชุดเปิดแต่ `enum` ยังปิด ทำให้ขัดกับ `platform_rules` ในไฟล์เดียวกัน
    และขัดกับ ADR-0006 Rule 2 ฉบับแก้ (RFC-0009) · `devfactory-core` `payload_check` เจอตอนรันจริง
    (`SIGHTING_RECORDED` · `GEOFENCE_CROSSED` validate ไม่ผ่าน)
- **เพิ่ม `record` ใน `SubjectType`** ([#14](https://github.com/monthop-gmail/agent-platform/issues/14)) — บันทึกของโดเมนที่ต้องตามรอยได้แต่ไม่ได้เกิดจาก job
  · ชนิดจริงอยู่ใน `metadata.record_type` · แยกจาก `artifact` ที่เป็นผลผลิตของ execution
- semantics ไม่เปลี่ยน — vocabulary 7 ตัวและ guarantees ทั้ง 8 ข้อคงเดิม ไม่ต้องมี RFC ที่ต้นทาง
  (`semantics_version` ยัง `1.1`)

## v1.1.0 — 2026-08-18
- **`EventType` เปลี่ยนจากชุดปิดเป็นชุดเปิด** — 7 ค่าเดิมเป็น *ขั้นต่ำที่ต้องมี* ไม่ใช่ชุดทั้งหมด
- **เพิ่ม event type ใหม่เป็น additive** ทำได้ผ่าน ADR ที่ repo นี้ ไม่ต้องมี RFC ที่ `devfactory-core`
  ตาม [RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md) ซึ่งแก้ Rule 2 ของ ADR-0006
- ลบ · เปลี่ยนชื่อ · เปลี่ยนความหมาย ของ 7 ค่าเดิม ยังเป็น semantic change เหมือนเดิม
- guarantee ทั้ง 8 ข้อไม่เปลี่ยน · ไม่มี field ใดเพิ่ม ลบ หรือเปลี่ยน type
- `derived_from.semantics_version` `1.0` → `1.1`
- **ไม่ breaking** — payload ที่ถูกต้องกับ v1.0.0 ยังถูกต้องกับ v1.1.0 ทุกตัว ชุดค่าที่ยอมรับกว้างขึ้นเท่านั้น

## v1.0.0 — 2026-08-18
- เขียนได้หลัง [`devfactory-core` RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) แยก authority เป็น semantics / wire schema
- semantics มาจาก `devfactory-core` `contract-semantics.yaml` `semantics_version: "1.0"` (RFC-0003 + RFC-0008)
- `job_id` optional · `subject_type` + `subject_id` required ตาม RFC-0008
- เพิ่ม field ระดับ platform: `tenant_id` `workspace_id` `correlation_id` `policy_result` `usage` `source` ตาม RFC-0005 Rule 1
- ตัดสินฝั่ง schema: **เก็บทั้ง `job_id` และ `subject_id`** เพราะเป็นคนละคำถาม (สายเหตุ vs หัวเรื่อง) พร้อมกฎว่าถ้า `subject_type: job` ต้องตรงกัน
