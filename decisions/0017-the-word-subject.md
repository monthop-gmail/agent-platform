# ADR-0017: คำว่า `subject` — หนึ่งคำ สามความหมาย ข้าม 5 contract

**Status:** Accepted (2026-08-21)
**Date:** 2026-08-21
**Depends on:** [ADR-0006](0006-contract-versioning.md) · [ADR-0012](0012-consent-contract.md) · [ADR-0016](0016-recording-which-consent-allowed-access.md)
**Blocking:** ตารางศัพท์ที่ lock ใน [`README.md`](README.md) · `contracts/policy/v1`

## Context

เจอตอนเขียน [ADR-0016](0016-recording-which-consent-allowed-access.md) ว่า `policy/v1` เรียกผู้กระทำว่า `subject` ขณะที่ `consent/v1` เขียนกำกับ field ชื่อเดียวกันไว้เองว่า 🔒 *"ไม่ใช่ actor"*

ADR-0016 บันทึกไว้ว่าเป็นปัญหาข้าม **3 contract** — **นับขาด** · ไล่ทั้ง `contracts/` แล้วมี **5 ตัว** และแยกได้เป็น **3 ความหมาย**:

| contract | field | ความหมาย | รูป |
| --- | --- | --- | --- |
| `policy/v1` | `Request.subject` | **ผู้กระทำ** — *"ใครจะทำ"* | object `{principal, agent_id}` |
| `capability/v1` | `declaration.subject` | **ผู้ประกาศ** — *"ใครเป็นคนประกาศ"* | object `{kind, id}` |
| `event/v1` 🔗 | `subject_type` / `subject_id` | **หัวเรื่องของบันทึก** | enum 9 ค่า + `Id` |
| `approval/v1` 🔗 | `subject` | **สิ่งที่ถูกอนุมัติ** — *"อนุมัติให้อะไร"* | object `{type, id}` |
| `consent/v1` | `subject_id` | **เจ้าของข้อมูล** — 🔒 *"ไม่ใช่ actor และไม่ใช่ resource"* | `Id` เดี่ยว |

สองกลุ่มแรกคือ *ผู้กระทำ/ผู้ถือ* · สองกลุ่มกลางคือ *สิ่งที่บันทึกเกี่ยวกับ* · ตัวสุดท้ายคือ *เจ้าของข้อมูลส่วนบุคคล* ซึ่งเป็นคนละเรื่องกับทั้งสองกลุ่ม

และคำนี้ **ไม่อยู่ในตารางศัพท์ที่ lock ไว้** ทั้งที่ [`decisions/README.md`](README.md) มีตารางนั้นอยู่เพื่อกันเรื่องแบบนี้โดยเฉพาะ

## ประเมินความเสี่ยงตามจริง — อย่าตีขลุม

คู่ที่อันตรายจริงมีคู่เดียว: **`policy/v1.Request.subject` (ผู้กระทำ) ↔ `consent/v1.subject_id` (เจ้าของข้อมูล)** เพราะทั้งคู่คือ "id ของคน" ที่ความหมายตรงข้ามกัน และเป็นสองด่านที่ต้องเรียกคู่กันตาม `consent_rules` ข้อ 6

ส่วน `event/v1` กับ `approval/v1` มี `type`/`subject_type` ติดมาด้วยเสมอ (job · execution · artifact …) จึงไม่ถูกสับสนกับ principal ได้ง่าย · `capability/v1` ก็มี `kind` กำกับ

**แต่ต้องพูดให้ตรง:** บน wire วันนี้ **schema จับความผิดพลาดนี้ได้อยู่แล้ว** — `policy` เป็น object `{principal, …}` ส่วน `consent` เป็น scalar `Id` · ส่งสลับกันจะ validate ไม่ผ่าน

```text
ความเสี่ยงจริงจึงไม่ได้อยู่บน wire แต่อยู่ใน:
  · หัวคนที่อ่าน contract สองตัวเรียงกัน
  · โมเดลภายในของ consumer ที่เขียนเอง ซึ่งไม่มี schema มาจับให้
```

`enterprise-knowledge` กำลัง map `Principal` / `TenantScope` / `PolicyContext` ของตัวเองเข้ากับ contract ชุดนี้ ([#17 ของเขา](https://github.com/monthop-gmail/enterprise-knowledge/issues/17)) และ `contracts.py` ของเขาเป็น Python ล้วน — **ไม่มี JSON Schema มาจับตรงนั้น** · ในโดเมนที่เขาทำ (ACL-aware retrieval) การสลับสองคำนี้แปลว่า *เอาสิทธิ์ของคนหนึ่งไปเปิดข้อมูลของอีกคน*

นี่คือเหตุผลที่เรื่องนี้ควรทำตอนนี้ ไม่ใช่ตอนมี consumer รายที่สี่

## ข้อจำกัดที่กำหนดทางเลือก

* [ADR-0006](0006-contract-versioning.md) ระบุ **"เปลี่ยนชื่อ field"** เป็น breaking ตรง ๆ → rename = major ใหม่
* `event/v1` และ `approval/v1` เป็น **derived contract** — `subject_type`/`subject_id` มาจาก [RFC-0008](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0008-external-event-intake.md) ซึ่งเป็น 🔒 semantics ของ `devfactory-core` · **เราเปลี่ยนเองไม่ได้** และไม่ควรอยากเปลี่ยน
* `consent/v1` `subject_id` ใช้อยู่ใน production ของ `care-agent-platform` และคำว่า **data subject เป็นศัพท์กฎหมาย** (PDPA/GDPR) ที่ถูกต้องอยู่แล้วในบริบทนั้น
* `policy/v1` มีคน pin สองราย (`care-agent-platform` · `devfactory-core`) และกำลังจะมีรายที่สาม

## คำวินิจฉัยที่เสนอให้ lock

> **`subject` = สิ่งที่บันทึกหรือข้อความนั้นเกี่ยวกับ**
> ห้ามใช้เรียก **ผู้กระทำ** — ผู้กระทำคือ `actor`
> ความหมาย *"เจ้าของข้อมูลส่วนบุคคล"* ใช้ได้เฉพาะใน `consent/v1` เพราะเป็นศัพท์กฎหมาย (*data subject*) และต้องมีหมายเหตุกำกับเสมอ

กฎนี้ทำให้ 4 ใน 5 contract ถูกอยู่แล้ว และชี้ตัวที่ต้องแก้ได้ตัวเดียวคือ `policy/v1`

## Options

### A. เอกสารอย่างเดียว — lock คำ + ใส่หมายเหตุอ้างอิงไขว้ในทั้ง 5 contract

* ✅ ไม่แตะ wire เลย · ไม่มี consumer ต้อง migrate
* ✅ ปิดความเสี่ยงที่เป็นความเสี่ยงจริง (การอ่านผิด) ตรงจุด
* ❌ `policy/v1` ยังเรียกผู้กระทำว่า `subject` ต่อไป — กฎที่เพิ่ง lock ถูกละเมิดโดย contract ของตัวเองตั้งแต่วันแรก
* ❌ consumer รายที่สี่ยังอ่านชื่อผิดได้เหมือนเดิม เพราะชื่อยังผิดอยู่

### B. A + `policy/v1` เพิ่ม `actor` · เลิกใช้ `subject` แบบมีช่วงเปลี่ยนผ่าน ⭐

```yaml
Request:
  required: [context, action]        # ถอด subject ออกจาก required (ผ่อน ไม่ใช่บังคับ)
  oneOf:
    - required: [actor]              # ทางใหม่
    - required: [subject]            # ทางเดิม — deprecated
  properties:
    actor:    { ... }                # รูปเดียวกับ subject เดิมทุกอย่าง
    subject:  { deprecated: true }
```

* ✅ **ไม่ breaking** — payload เดิมที่ส่ง `subject` ยัง valid ทุกใบ · ถอดออกจาก `required` เป็นการผ่อน
* ✅ `oneOf` บังคับให้มี **อย่างใดอย่างหนึ่ง ไม่ใช่ทั้งคู่** — ไม่มีช่วงที่สองชื่อพูดคนละเรื่องพร้อมกัน ตรงกับกฎ *"สิ่งเดียวกันต้องเขียนได้แบบเดียว"* ที่ใช้กับ `expires_at: null` และ `conditions: []`
* ✅ ลบ `subject` ทิ้งเมื่อ `policy/v2` เกิดขึ้นด้วยเหตุอื่น — ไม่ต้องบังคับให้ใครขึ้น major เพราะชื่อ
* ❌ มีสองชื่ออยู่ร่วมกันชั่วคราว ซึ่ง repo นี้ไม่ชอบ — แลกกับการไม่บังคับ consumer สองรายให้ migrate ทันที
* ❌ ต้องมีคนจำว่าให้ลบตอน v2 · แก้ด้วยการเขียนไว้ใน `CHANGELOG` และ `platform_rules`

### C. A + rename `consent/v1.subject_id` → `data_subject_id` (`consent/v2`)

* ✅ ตรงศัพท์กฎหมายที่สุด และทำให้ `subject` เหลือความหมายเดียว
* ❌ **breaking กับ contract ที่ใช้ใน production อยู่** และ `care-agent-platform` เพิ่ง migrate `conditions` ไปหมาด ๆ
* ❌ แก้ตัวที่ *ถูกอยู่แล้ว* แทนที่จะแก้ตัวที่ผิด — `consent/v1` เขียนกำกับไว้ชัดตั้งแต่แรกว่าไม่ใช่ actor

### D. rename ให้เป็นคำเฉพาะทุกที่ (`actor` · `data_subject_id` · `record_subject`)

* ✅ ไม่เหลือความกำกวมเลย
* ❌ major bump 4–5 contract พร้อมกัน · และ **แตะ `event/v1` กับ `approval/v1` ซึ่งเป็น semantics ของ `devfactory-core` ที่เราเปลี่ยนเองไม่ได้**
* ❌ ราคาสูงกว่าความเสี่ยงจริงมาก ในเมื่อ schema จับกรณีสลับบน wire ได้อยู่แล้ว

### E. ไม่ทำอะไร

* ✅ ศูนย์บาท
* ❌ ตารางศัพท์ที่ lock มีไว้กันเรื่องนี้โดยเฉพาะ แล้วปล่อยเคสที่ชัดที่สุดไว้นอกตาราง
* ❌ consumer รายที่สามกำลังอ่านอยู่ตอนนี้

## Decision

**B** — lock คำ + `policy/v1` เพิ่ม `actor` และ deprecate `subject` ด้วย `oneOf` ที่บังคับให้เลือกอย่างใดอย่างหนึ่ง

**Reason:** ความเสี่ยงจริงอยู่ที่คนอ่านและที่โมเดลภายในของ consumer ไม่ใช่บน wire (schema จับการสลับได้อยู่แล้วเพราะรูปต่างกัน) — จึงไม่คุ้มที่จะบังคับ major bump ให้ใคร (ปฏิเสธ C และ D) · แต่การ lock กฎแล้วปล่อยให้ contract ของตัวเองละเมิดตั้งแต่วันแรกก็ไม่ใช่การ lock (ปฏิเสธ A เดี่ยว ๆ) · `oneOf` + ถอดออกจาก `required` ปิดช่องได้โดยไม่ทำให้ payload เดิมใบไหน invalid และไม่เปิดช่วงที่สองชื่อพูดคนละเรื่องพร้อมกัน · `event/v1` และ `approval/v1` ไม่ต้องแตะเพราะกฎที่ lock ทำให้มันถูกอยู่แล้ว และมันเป็น semantics ของ repo อื่นที่เราเปลี่ยนเองไม่ได้อยู่ดี

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### ไม่ bump major — `policy/v1` `v1.1.0` → `v1.2.0`

| เกณฑ์ breaking ของ [ADR-0006](0006-contract-versioning.md) | การเปลี่ยนนี้ |
| --- | --- |
| ลบ field · เปลี่ยนชื่อ field · เปลี่ยน type | ❌ `subject` ยังอยู่ ยังรูปเดิม แค่ติด `deprecated` |
| เพิ่ม required field ใหม่ · optional → required | ❌ ตรงข้าม — **ถอด `subject` ออกจาก `required`** คือการผ่อน |
| ลบค่าออกจาก enum · เปลี่ยนความหมายของค่าเดิม | ❌ ไม่มี enum ถูกแตะ |
| เปลี่ยน default | ❌ ไม่มี default |
| เข้มขึ้นใน validation | ⚠️ `oneOf` ห้ามส่งทั้งสองชื่อพร้อมกัน — แต่ `actor` เพิ่งเกิด **ไม่มี payload เดิมใบไหนส่งทั้งคู่ได้** จึงไม่มีใบไหนกลายเป็น invalid |

## Consequences

* ตารางศัพท์ที่ lock ใน [`decisions/README.md`](README.md) เพิ่มแถว `subject` — ที่มา ADR นี้
* `policy/v1` `v1.2.0` · `contracts/README.md` บันทึกว่ามี field ที่ deprecated รอลบใน `v2`
* ใส่หมายเหตุอ้างอิงไขว้ใน `consent/v1` · `event/v1` · `approval/v1` · `capability/v1` ว่า `subject` ที่นั่นหมายถึงอะไร และชี้มาที่กฎเดียวกัน — **นี่คือส่วนที่ปิดความเสี่ยงจริง** ไม่ใช่การ rename
* `care-agent-platform` และ `devfactory-core` **ไม่ต้องทำอะไรทันที** — payload เดิมยัง valid · ย้ายไป `actor` เมื่อสะดวก
* ตอบ [enterprise-knowledge#17](https://github.com/monthop-gmail/enterprise-knowledge/issues/17) ได้ด้วยชื่อที่ไม่กำกวมตั้งแต่วันแรกที่เขา map
* **`event/v1` และ `approval/v1` ไม่ถูกแตะ** — ถ้าวันหนึ่งอยากให้ตรงกันหมดจริง ๆ ต้องเปิด RFC ที่ `devfactory-core` ไม่ใช่ ADR ที่นี่
* **drift check ตรวจข้อนี้ไม่ได้** — เป็นเรื่องความหมายของชื่อ ไม่ใช่โครงสร้าง · สิ่งเดียวที่ตรวจได้คือ `oneOf` ทำงานจริงไหม ซึ่งพิสูจน์ด้วย negative test
* ค้างต่อจาก ADR-0016: `event/v1.policy_result` ที่เป็นสำเนามือของ `Decision` — ยังไม่แตะ

## Sources

[ADR-0016](0016-recording-which-consent-allowed-access.md) ข้อค้นพบ 4 (ซึ่งนับ contract ขาดไป 2 ตัว) · [ADR-0012](0012-consent-contract.md) · [RFC-0008](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0008-external-event-intake.md) `subject_type`/`subject_id` · [enterprise-knowledge#17](https://github.com/monthop-gmail/enterprise-knowledge/issues/17) · ตารางศัพท์ที่ lock ใน [`decisions/README.md`](README.md)
