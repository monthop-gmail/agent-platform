# ADR-0034: รับ `semantics_version` `1.5` — กฎที่เราขอเอง กลับมาผูกสัญญาใบที่เราไม่ได้ขอ

**Status:** **Proposed** (2026-09-20)
**อัปเดต:** 2026-09-20 — **ข้อที่ใบนี้เปิดค้างไว้ มีคำตอบจากสองทีมที่ไม่ได้คุยกัน** · Amendment 1
**Date:** 2026-09-20
**Depends on:** [ADR-0006](0006-contract-versioning.md) · [ADR-0030](0030-the-field-nobody-named.md) · [ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md) · [ADR-0011](0011-conformance-automation.md)
**Blocking:** `contracts/event/v1` → `v1.8.0` · `contracts/approval/v1` → `v1.3.0`
**Closes:** [#73](https://github.com/monthop-gmail/agent-platform/issues/73) · [#74](https://github.com/monthop-gmail/agent-platform/issues/74)

## Context

สามวัน สามเวอร์ชัน และสองในสามเกิดจากคำถามที่ฝั่งเราถามเอง

| | ที่มา | ผลกับเรา |
| --- | --- | --- |
| `1.3` (17 ก.ย.) | [RFC-0013](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0013-audit-fields-that-hold-human-text.md) — **เรายื่นเอง** | invariant กฎ leaf เข้า `event.frozen` |
| `1.4` (18 ก.ย.) | [RFC-0016](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0016-approval-subject-types.md) — จากที่ `care-agent-platform` รายงานใน [#73](https://github.com/monthop-gmail/agent-platform/issues/73) | `approval.subject_types` ถูกประกาศเป็นครั้งแรก + ค่า `record` |
| `1.5` (18 ก.ย.) | [RFC-0017](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0017-the-leaf-rule-is-not-a-property-of-one-contract.md) — **เราถามเอง** | กฎ leaf ผูก `approval/v1` ด้วย |

### `1.3` ปิดครึ่งเดียว และมีคนเปิด issue บอกเรา

[#71](https://github.com/monthop-gmail/agent-platform/pull/71) ขยับ pointer เป็น `1.3` ภายใน 17 นาทีหลังต้นทาง merge และเขียนขอบเขตของตัวเองไว้ว่า *"แก้แค่ pointer · `guarantees.rules` ยังไม่ได้เพิ่ม invariant และ `transition.reason` ยังไม่ได้ถูกประกาศ — ต้องมี ADR"*

แล้ว [#74](https://github.com/monthop-gmail/agent-platform/issues/74) ถูกเปิดชี้ว่า **สัญญาประกาศว่า pin `1.3` แต่ไม่ได้พกกฎของ RFC-0013 มา** — คือ pointer อ้างมากกว่าที่ไฟล์ส่งมอบ

ใบนี้ปิดข้อนั้น และปิดพร้อมกันสำหรับ `1.5` เพื่อไม่ให้เกิดรูปเดียวกันซ้ำสองรอบติด

### คำถามที่เราถาม และคำตอบที่กลับมาแรงกว่าที่เผื่อไว้

เราถามที่ [`devfactory-core#46`](https://github.com/monthop-gmail/devfactory-core/issues/46) ว่า invariant ผูก `approval/v1` ด้วยหรือไม่ เพราะอ่านได้สองทาง — invariant เขียนอยู่ใต้ `event.frozen` เท่านั้น แต่ `approval/v1` `reason` เป็นข้อความของคนตามนิยามทุกประการ และต้นทางเองก็ประกาศ `metadata.approval.reason` ไว้แล้ว

เขาตอบว่า **ผูกทั้งสอง** พร้อมเหตุผลที่เราไม่ได้เขียนไว้ในคำถาม:

> ถ้อยคำของ invariant ไม่ได้พูดถึง event เลย · การจำกัดขอบเขตมาจาก*ที่ที่มันถูกเขียน* — **และตำแหน่งไม่ใช่การตัดสินใจที่ใครทำ** · ตอนเขียน RFC-0013 `event/v1` เป็นสัญญาใบเดียวที่มีหลักฐานอยู่ตรงหน้า จึงเขียนไว้ตรงนั้น
>
> กฎนี้เป็นคุณสมบัติของ **ข้อความที่ลบไม่ได้เมื่อเขียนลงไปแล้ว** ไม่ใช่คุณสมบัติของ `event/v1`

และข้อที่เราฝากให้คิดคู่กัน — ว่า `approval/v1` `reason` เป็น `required` + `minLength: 1` จึงตัดออกไม่ได้ — **เขาชี้ว่ามันกลับทาง**:

> ถูก และมันเป็นเหตุผลให้มีกฎ ไม่ใช่เหตุผลไม่ให้มี · `transition.reason` เป็น optional ผู้ผลิตที่เห็นว่าไม่คุ้มค่าเก็บ **เลิกส่งได้** · `approval/v1.reason` ไม่มีทางออกนั้นเลย **สิ่งเดียวที่เปลี่ยนได้ตลอดอายุของมันคือคำตอบของข้อ 3**

**เราถามเพราะคิดว่าจะได้คำตอบว่า "ไม่ผูก" และได้คำตอบตรงข้ามพร้อมเหตุผลที่ดีกว่าคำถาม** — บันทึกไว้เพราะถ้าเดาแทนตามที่เอียงอยู่ เราจะเขียน ADR ที่บอกว่า `approval/v1` อยู่นอกขอบเขต แล้วมันจะผิด

### `1.4` ปิด [#73](https://github.com/monthop-gmail/agent-platform/issues/73) — ช่องที่ consumer ชนสองครั้งในโดเมนเดียว

`care-agent-platform` รายงานว่า `$.subject.type` ห้าค่าเป็นของ **ระบบที่รัน agent** ทั้งหมด ไม่มีค่าสำหรับ **บันทึกของโดเมน** · เขาเลือก `artifact` ให้คำสั่งหมอที่รอมีผล และ `tool_call` ให้คำขอลบข้อมูลตาม PDPA — **ทั้งคู่ validate ผ่าน และ audit event ของวัตถุเดียวกันใช้ `subject_type: record` อยู่แล้ว**

> วันนี้ระบบเดียวกันอธิบายสิ่งเดียวกันด้วยคำสองคำ ขึ้นกับว่ากำลังเขียนลง `event/v1` หรือ `approval/v1`

เป็นรูปเดียวกับที่ `event/v1` เคยมีและปิดไปแล้วใน [#14](https://github.com/monthop-gmail/agent-platform/issues/14) · ต้นทางรับเป็น RFC-0016 และเขียนข้อที่ไม่มีใครเคยเขียนไว้:

> `subject_types` **ไม่เคยถูกประกาศไว้ที่ไหน** จึงไม่มีอะไรฝั่งนี้มองเห็นได้เลยว่ามันขาดค่า จนกระทั่ง `care-agent-platform` ชนมันสองครั้ง

และประกาศเป็น **`closed: false`** พร้อมเหตุผลที่แยกจาก `decision_types`: *"subject type บอกว่าอนุมัติ **อะไร** ไม่เคยบอกว่า **อนุมัติหรือไม่**"*

## สิ่งที่พบระหว่างทาง — `binding` check ของเราหลวมมาตลอด

`approval/v1` `subject.properties.type` เป็น **enum ปิดที่เขียนคาไว้สองชั้นลงไป** ส่วน `check_binding` เดินดูเฉพาะ property ระดับบนที่ `$ref` ไป `$defs`

แปลว่าถ้าไม่แก้อะไรเลย พอต้นทางประกาศ `closed: false` เมื่อวาน check จะรายงานว่า **"closed=false และไม่มี field ผูกกับ enum ปิด"** ซึ่งเป็น ok ปลอม ทั้งที่ field ผูกอยู่จริงและค่านอกลิสต์ validate ไม่ผ่าน

`conformance/README.md` เขียนไว้เองว่า **check ที่หลวมอันตรายกว่าไม่มี check เพราะสร้างความมั่นใจปลอม** — ใบนี้แก้ให้เดินลง `properties` ที่ซ้อนกันและนับ enum ที่เขียนคาไว้ที่ field ด้วย

## Options

### A. ขยับ pointer อย่างเดียว

* ✅ ปิด FAIL ได้เร็วที่สุด · มี precedent (`v1.6.1` · `v1.7.1`)
* ❌ **[#74](https://github.com/monthop-gmail/agent-platform/issues/74) เปิดขึ้นมาเพราะทางนี้พอดี** — เลือกอีกครั้งคือสร้างเหตุของ issue เดิมซ้ำที่ `1.5`
* ❌ `guarantees` ของเราจะขาดข้อที่ต้นทาง freeze และ **drift check จับไม่ได้ เพราะมันเทียบแค่ตัวเลข**

### B. A + เขียน invariant ลง `guarantees` แต่ไม่แตะฟิลด์

* ✅ `guarantees` ครบตามต้นทาง
* ❌ ผู้อ่านที่เปิด `transition.reason` หรือ `approval/v1.reason` ไม่เห็นอะไรบอกว่ามันคือ leaf ที่ประกาศแล้ว
* ❌ ขัดกับเหตุผลของ [ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md) ที่เลือกเขียนคำกำกับ **ที่ตัวฟิลด์** เพื่อให้คำเตือนเดินทางไปกับฟิลด์

### C. B + ประกาศที่ตัวฟิลด์ทั้งสองใบ + ปิดช่องของ `binding` check ⭐

* ✅ **ปิดครบทั้งกฎ ฟิลด์ที่เป็นเหตุของกฎ และ check ที่ควรจับแต่จับไม่ได้**
* ✅ คำกำกับอยู่ที่ตัวฟิลด์ตามหลักของ ADR-0031
* ✅ **เขียนความต่างระหว่างสองใบไว้ที่ทั้งสองใบ** — `transition.reason` optional เลิกส่งได้ · `approval/v1.reason` ตัดไม่ได้เลย สิ่งเดียวที่เปลี่ยนได้คือคำตอบข้อ 3 · เป็นข้อที่ต้นทางชี้ให้และไม่มีที่ไหนในสัญญาของเราบันทึกไว้
* ✅ `subject.type` ใช้รูป `EventType` / `EventTypeName` ที่ repo นี้ใช้อยู่แล้ว — ชุดเปิดที่ยังอ่านรู้ว่าเป็นอะไร ไม่ใช่ `string` อะไรก็ได้
* ❌ `guarantees` ยาวขึ้นหนึ่งข้อที่ยาวกว่าข้ออื่นมาก
* ❌ **กฎทั้งชุด validator กลางบังคับไม่ได้** — เขียนข้อจำกัดไว้ในกฎเอง ตามที่ต้นทางทำและเราคัดมา

### D. C + สร้างบล็อก `text_fields` กลางให้ consumer กรอก

* ✅ รูปกลางที่เทียบกันได้ข้าม consumer
* ❌ **การประกาศเป็นของผู้ผลิต ไม่ใช่ของสัญญา** — ต้นทางเขียนกำกับเองว่าบล็อกนั้น *"อยู่นอก frozen เพราะเป็นของฝั่งเรา"*
* ❌ ผู้ผลิตสามรายที่ทำแล้วใช้คนละรูป — `care-agent-platform` ประกาศใน `platform-contract.yaml` · `ecosystem-intelligence` ประกาศพร้อมแกน `written_by` ที่แยก `human` กับ `system` · `devfactory-core` ประกาศใน `contract-semantics.yaml` · **ทั้งสามถูกทั้งหมด** และรูปกลางจะทำให้สองในสามผิด

## Recommendation — **C**

**เหตุผล:** A ถูกทดสอบไปแล้วเมื่อสามวันก่อนและผลคือ [#74](https://github.com/monthop-gmail/agent-platform/issues/74) — เลือกซ้ำคือรู้ทั้งรู้ว่าจะเกิดอะไร · ส่วนการปิดแค่ `guarantees` จะทำให้เราเขียนกฎที่ RFC ทั้งสองฉบับมีไว้เพื่อสองฟิลด์นั้น แล้วปล่อยทั้งสองฟิลด์ไว้เหมือนเดิม ซึ่งเป็นรูปของ `error/v1.details` ที่ปิดไปเมื่อ 10 ก.ย. · ปฏิเสธ D เพราะผู้ผลิตสามรายที่ทำแล้วใช้คนละรูปและถูกทั้งหมด — รูปกลางจะทำให้สองในสามผิด

**Authority:** รอเจ้าของสัญญาเคาะ — Monthop Champaruang, Platform Owner / Architecture Authority of `agent-platform`

## Consequences

* **`event/v1` `v1.7.1` → `v1.8.0` · `approval/v1` `v1.2.2` → `v1.3.0`** — ไม่ breaking ทั้งคู่ · ไม่มี field ใหม่ ไม่แตะ `required` ไม่แตะ `type` · `subject.type` **กว้างขึ้น** ไม่ได้แคบลง payload ที่ valid วันนี้ยัง valid ทุกใบ
* **`care-agent-platform` เลิกต้องเลือกค่าที่ผิดน้อยที่สุดได้แล้ว** — `record` ใช้ได้ทั้งสองสัญญา และคำเดียวกันหมายถึงของเดียวกัน · เขาบันทึกไว้เป็น `gaps` ในใบ ไม่ได้เลือกแล้วเงียบ ([#73](https://github.com/monthop-gmail/agent-platform/issues/73))
* **consumer ที่ pin `event/v1` ทั้งสี่รายมีภาระที่ validator ไม่ฟ้อง** — `care-agent-platform` · `devfactory-core` · `ecosystem-intelligence` ประกาศ `text_fields` แล้วทั้งสาม · `botforge` ยังไม่มี แจ้งไปแล้วที่ [`botforge#31`](https://github.com/monthop-gmail/botforge/issues/31) · **`approval/v1` เพิ่งเข้าขอบเขตวันนี้ ยังไม่มีใครถูกถามเรื่องนี้เลย**
* **`binding` check เคยหลวมและไม่มีใครรู้** — ok ปลอมกับ enum ที่เขียนคาไว้ในชั้นซ้อน · แก้แล้วพร้อม negative test ที่ใช้สภาพจริงก่อนแก้เป็นเคสทดสอบ
* **drift check ยังเทียบได้แค่ตัวเลข `semantics_version`** — ไม่ได้ตรวจว่าเนื้อหาของ invariant ถูกคัดมาครบ · **นี่คือช่องที่ทำให้ [#74](https://github.com/monthop-gmail/agent-platform/issues/74) เกิดได้ และใบนี้ไม่ได้ปิด** — ปิดด้วยเครื่องต้องอ่านความหมาย ไม่ใช่เทียบสตริง

## Amendment 1 — ข้อที่ปิดไม่ได้ในใบ มีคำตอบแล้ว และไม่ได้มาจากเรา

ใบนี้เขียนไว้ใน Consequences ว่า:

> **drift check ยังเทียบได้แค่ตัวเลข `semantics_version`** — ไม่ได้ตรวจว่าเนื้อหาของ invariant ถูกคัดมาครบ · **นี่คือช่องที่ทำให้ [#74](https://github.com/monthop-gmail/agent-platform/issues/74) เกิดได้ และใบนี้ไม่ได้ปิด** — ปิดด้วยเครื่องต้องอ่านความหมาย ไม่ใช่เทียบสตริง

ภายในวันเดียวกัน **สองทีมที่ไม่ได้คุยกันรายงานคนละครึ่งของคำตอบ**

### ครึ่งแรก — เช็คที่ทำงานได้ อยู่ที่ต้นทาง ไม่ใช่ที่เรา

`devfactory-core` สร้าง [`#43`](https://github.com/monthop-gmail/devfactory-core/pull/43) — เช็คว่า **สัญญาที่ derive ไปแล้วพกข้อผูกมัดที่ต้นทาง freeze ไว้มาจริงหรือเปล่า** และรายงานว่ารอบ `1.3` ไม่มีเกตของใครจับได้เลยสักตัว:

| เกต | ถามอะไร | ผล |
| --- | --- | --- |
| `drift_check` ของเรา | `semantics_version` ตรงไหม | ✅ ตรง |
| `payload_check` ของต้นทาง | payload ตรง schema ไหม | ✅ ผ่าน |
| `pin_freshness` | pin เก่าไปไหม | ✅ สด |
| `payload_check` ของ `care` | leaf จริง 115 ใบ | ✅ ผ่าน |

> **ไม่มีใครถามว่า "สัญญาที่บอกว่าตามเราแล้ว พกกฎมาด้วยหรือเปล่า"** — เป็น *"declared is not conforming"* ของ ADR-0006 กลับด้าน คราวนี้สัญญาเป็นฝ่ายประกาศ

### ครึ่งหลัง — กฎที่ตอบผิดแล้วมีคนจับได้

`care-agent-platform` ตอบข้อที่ใบนี้เปิดค้างไว้ตรง ๆ ว่าเขาก็ไม่มีคำตอบเหมือนกัน แต่มีข้อสังเกตจากของจริง:

> ตอนขอบเขตของกฎขยายจาก `event/v1` ไปถึง `approval/v1` สิ่งที่ฟ้องว่าเราตามไม่ครบ **ไม่ใช่ `drift_check` แต่เป็น ratchet ที่รันกับ payload จริง** และมันฟ้องได้เพราะเราขยายตัวมันตามขอบเขตด้วยมือ
>
> แปลว่าการตามเนื้อหาของ invariant **ยังเป็นงานของคนอยู่ แต่ผลของการทำไม่ครบ กลายเป็นของที่เครื่องจับได้ทันทีที่ทำ** ต่างจาก drift ที่เงียบ

และเสนอกฎ:

> เมื่อ `semantics_version` ขยับและขอบเขตของ invariant เปลี่ยน **ผู้ผลิตต้องตอบว่าตัวตรวจของตัวเองครอบขอบเขตใหม่แล้วหรือยัง** ซึ่งเป็นคำถามที่ตอบผิดแล้วมีคนจับได้ ไม่เหมือนคำถามว่าอ่านครบไหม

**ข้อสุดท้ายคือแกนของมัน** — *"อ่านครบไหม"* ตอบผิดแล้วเงียบ · *"ตัวตรวจครอบขอบเขตใหม่ไหม"* ตอบผิดแล้ว payload จริงจะฟ้องในรอบแรกที่รัน · เขาพิสูจน์เองในรอบเดียวกัน คือขยายตัวไล่ leaf ให้ครอบใบอนุมัติ แล้วมันฟ้อง `$.authority.display_name` ทันที

### กฎที่เพิ่ม

```text
7. เมื่อ semantics_version ขยับ และขอบเขตของ invariant เปลี่ยน
   ผู้ผลิตต้องตอบว่าตัวตรวจของตัวเองครอบขอบเขตใหม่แล้วหรือยัง
   — เป็นคำถามที่ตอบผิดแล้วมีคนจับได้ ต่างจาก "อ่านครบไหม" ที่ตอบผิดแล้วเงียบ

8. `agent-platform` ตอบข้อ 7 ว่า **ไม่มีตัวตรวจที่ต้องขยาย** — conformance/
   ไม่เดิน payload ของใคร (ADR-0011 ห้ามเรียก host อื่น) และเราไม่ใช่ผู้ผลิต event
   คำตอบนี้ต้องเขียนไว้ ไม่ใช่เว้นว่าง เพราะ "ไม่มีอะไรต้องทำ" กับ "ยังไม่ได้ดู"
   หน้าตาเหมือนกันทุกประการ
```

### ทำไมเราไม่สร้าง drift check ให้ข้อนี้ ทั้งที่เป็นข้อที่ใบเปิดค้างไว้เอง

เขียนไว้ตรง ๆ เพราะมันขัดกับสัญชาตญาณ: **เช็คที่ทำงานได้ต้องอยู่ที่ต้นทาง เพราะมีแต่เจ้าของ semantics ที่รู้ว่าข้อผูกมัดคืออะไร** · ฝั่งเรามีแค่ผลลัพธ์ที่เขียนใหม่ด้วยถ้อยคำของเราเอง — เช็คที่เทียบคำในไฟล์ของเรากับคำในไฟล์ของเขา จะจับได้เฉพาะตอนที่เราคัดลอกคำมาตรง ๆ ซึ่งเป็นสิ่งที่เราไม่ทำและไม่ควรทำ

และมีหลักฐานว่าทางนั้นพังจริง — `devfactory-core` รายงานว่า `carried_check` ของเขาเองเคยให้ผลบวกลวง เพราะ marker คำว่า `record` ไปตรงกับ **ชื่อไฟล์ในลิงก์** `0019-execution-records-its-approval.md` · เขาต้องแยกโหมดเป็น `in_enum` / `as_key` เพื่อแก้

**การค้นแบบข้อความให้ผลบวกลวงกับคำสั้น ๆ** — ถ้าเราสร้างเช็คแบบนั้น มันจะเป็น check ที่หลวม ซึ่งเป็นแผลที่ `conformance/README.md` ของเราเขียนกฎห้ามตัวเองไว้ และที่เราเพิ่งปิดไปสองครั้งในสามวัน (`[5b]` `[5c]` · `binding` ที่มองไม่เห็น enum ในชั้นซ้อน)

### `approval/v1` `v1.3.1` — คำเตือนที่เดินทางถึง ไม่เท่ากับคำเตือนที่ถูกอ่าน

[ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md) เลือกเขียนคำกำกับที่ต้นทางของฟิลด์ใน `identity/v1` **เพื่อให้คำเตือนเดินทางไปกับ `Principal` ทุกที่ที่มันถูกฝัง** — และมันเดินทางมาถึง `approval/v1` `authority` จริง

แต่ `care` บอกเองว่า **ไม่ได้ไปมองเพราะยังไม่มีอะไรบอกให้มอง** · ฟิลด์ที่ `$ref` ออกไปจะถูกอ่านก็ต่อเมื่อมีคนตามลิงก์ไป

จึงเขียนซ้ำที่จุดใช้งาน พร้อมหลักฐาน — **ไม่ใช่เพราะ ADR-0031 ผิด แต่เพราะมันครอบได้เท่าที่คนตามลิงก์ และตอนนี้มีหลักฐานว่าคนไม่ตาม**

## Sources

[`devfactory-core#46`](https://github.com/monthop-gmail/devfactory-core/issues/46) คำถามและคำตอบเรื่องขอบเขต · RFC-0013 · [RFC-0016](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0016-approval-subject-types.md) · [RFC-0017](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0017-the-leaf-rule-is-not-a-property-of-one-contract.md) · [#73](https://github.com/monthop-gmail/agent-platform/issues/73) [#74](https://github.com/monthop-gmail/agent-platform/issues/74) · [#71](https://github.com/monthop-gmail/agent-platform/pull/71) · [ADR-0030](0030-the-field-nobody-named.md) [ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md)
