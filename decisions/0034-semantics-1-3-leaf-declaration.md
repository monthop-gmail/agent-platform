# ADR-0034: รับ `semantics_version` `1.3` — invariant ที่เราขอเอง กลับมาเป็นกฎที่ผูกเรา

**Status:** **Proposed** (2026-09-18)
**Date:** 2026-09-18
**Depends on:** [ADR-0006](0006-contract-versioning.md) · [ADR-0030](0030-the-field-nobody-named.md) · [ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md) · [ADR-0018](0018-policy-result-single-source.md)
**Blocking:** `contracts/event/v1` → `v1.8.0`

## Context

[RFC-0013](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0013-audit-fields-that-hold-human-text.md) ที่ `agent-platform` ยื่นที่ `devfactory-core` เมื่อ 12 ก.ย. **ถูก merge เมื่อ 17 ก.ย. 14:46** · `contract-semantics.yaml` ขึ้น `1.3` และเขียนไว้เองว่า *"contract ที่ derive ต้องอัปเดต `derived_from.semantics_version` เป็น `1.3`"*

**pointer ถูกขยับไปแล้วใน [#71](https://github.com/monthop-gmail/agent-platform/pull/71) เมื่อ 17 ก.ย. 15:03** — 17 นาทีหลังต้นทาง merge · `event/v1` `v1.7.1` · `approval/v1` `v1.2.2` · drift check เขียว

ใบ `v1.7.1` เขียนขอบเขตของตัวเองไว้ตรง ๆ และใบนี้คือส่วนที่มันกันไว้:

> **PR นี้แก้แค่ pointer** — `guarantees.rules` ยัง**ไม่ได้**เพิ่ม invariant ข้อใหม่ และ `transition.reason` ยังไม่ได้ถูกประกาศ · ทั้งสองอย่างเป็นการแก้ contract **ซึ่งต้องมี ADR ที่ repo นี้ ไม่ใช่สิ่งที่ consumer ยื่นมาให้**
>
> ที่ทำได้ทันทีคือ pointer เพราะปล่อยไว้ drift check จะแดงทุกวัน

**การแยกแบบนั้นถูก** — pointer เป็นของที่ต้นทางสั่งตรง ๆ และไม่มีดุลพินิจ ส่วนการเขียน invariant ลง `guarantees` กับการประกาศฟิลด์เป็นการตัดสินใจเรื่องรูปของสัญญา ซึ่งเป็นของที่นี่

### สิ่งที่ `v1.7.1` ยังไม่ปิด

| | สถานะหลัง `v1.7.1` |
| --- | --- |
| `derived_from.semantics_version` · รายการ `rfcs` | ✅ ปิดแล้ว |
| `guarantees.rules` — invariant ข้อใหม่ | ❌ ยังไม่มี · 8 ข้อเดิมไม่มีข้อไหนพูดถึง leaf |
| `transition.reason` | ❌ ยังเป็น `{ type: string }` เปล่า |
| กฎว่าการประกาศต้องเป็นสิ่งที่ตัวตรวจอ่าน · `metadata` อยู่ใต้กฎเดียวกัน | ❌ ยังไม่มี |

### invariant ที่ต้นทางรับไป — ถ้อยคำสุดท้ายไม่เท่ากับที่เรายื่น

ต้นทางเขียนลง `event.frozen.invariants` โดยเติมสองอย่างที่ร่างของเราไม่มี

| | ร่างที่เรายื่น | ที่ต้นทางรับไป |
| --- | --- | --- |
| ตัวอย่างของ "ตัวชี้" | *id, code, number, timestamp, boolean, enum* | เหมือนเดิม |
| ข้อจำกัด | อยู่ในหัวข้อแยกของ RFC | **ย้ายเข้ามาอยู่ในบรรทัดเดียวกับ invariant** — *"บังคับได้เฉพาะฝั่งผู้ผลิต: validator บอกได้ว่ามี key อะไร แต่บอกไม่ได้ว่าใครพิมพ์ค่านั้น"* |
| ที่มา | — | เขียนคอมเมนต์กำกับว่าเป็น *"ต้องประกาศ ไม่ใช่ห้ามมี"* พร้อมเหตุผลว่ากฎแบบห้ามจะทำให้ระบบที่บันทึกเหตุผลไว้ถูกต้องกลายเป็น non-conformant |

**การย้ายข้อจำกัดเข้ามาอยู่ในตัว invariant เป็นการแก้ที่ถูก** และตรงกับหลักที่เราใช้ใน [ADR-0030](0030-the-field-nobody-named.md) เอง คือเขียนข้อจำกัดของกฎไว้ในกฎ ไม่ใช่ในเอกสารข้าง ๆ

### และต้นทางทำสิ่งที่ RFC ขอ กับตัวเองด้วย

เขาประกาศ `text_fields` ของตัวเองไว้ในไฟล์เดียวกัน **นอก `frozen`** พร้อมเขียนกำกับว่า *"อยู่นอก frozen เพราะเป็นของฝั่งเรา ไม่ใช่ส่วนหนึ่งของสัญญา · `conformance/payload_check.py` อ่านบล็อกนี้ ไม่ได้ถือรายการของตัวเอง"*

และ `retention_layer` ของเขาเขียนตรง ๆ ว่า **ลบรายฟิลด์ไม่ได้ · `EventLog` อยู่ในหน่วยความจำล้วน · ยังไม่มีชั้น store หรือ tenant ที่ลบได้จริงในระบบนี้วันนี้** — คำแถลงที่ conform และเป็นจริง ซึ่งเป็นสิ่งที่ข้อ 3 ต้องการพอดี

## สิ่งที่เปลี่ยนในสัญญาของเรา

### `approval/v1` — ปิดไปแล้วใน `v1.2.2` ใบนี้ไม่แตะ

`approval.frozen` **ไม่ขยับแม้แต่ตัวอักษรเดียว** — invariant ใหม่อยู่ใต้ `event` ไม่ใช่ `approval` · และ `reason` มีกฎห้าม credential/PII/private reasoning อยู่แล้วตั้งแต่ `v1.0.0`

### `event/v1` — invariant + คำกำกับที่ `transition.reason` + กฎการประกาศ

`guarantees` ของเรามี 8 ข้อ ครอบของเขา 7 ข้อ · **ข้อใหม่เป็นข้อที่ 9 และไม่มีข้อไหนในนั้นครอบมาก่อน** ต่างจาก `v1.6.1` ที่ guarantee ใหม่ถูกครอบอยู่แล้วจึงไม่ต้องแก้ไฟล์

`transition.reason` เดิมเป็น `{ type: string }` ไม่มีคำอธิบายเลยสักบรรทัด — **รูปเดียวกับ `error/v1.details` ([ADR-0030](0030-the-field-nobody-named.md)) และ `identity/v1.display_name` ([ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md))** ซึ่งเป็นสองใบที่ทำให้ RFC นี้เกิดขึ้นตั้งแต่แรก · ตอนนี้มันคือ leaf แรกที่ถูกประกาศตามกฎที่เราขอมาเอง

## Options

### A. หยุดที่ `v1.7.1` — pointer พอแล้ว

* ✅ ไม่มี FAIL เหลือ · drift เขียวอยู่แล้ววันนี้
* ✅ มี precedent ตรง ๆ คือ `approval/v1` `v1.2.1` และ `event/v1` `v1.6.1` ที่ขยับ pointer อย่างเดียว
* ❌ **precedent นั้นใช้ได้เพราะ guarantee ใหม่ถูกครอบอยู่แล้ว (8 ≥ 3)** — รอบนี้ไม่ถูกครอบ · `guarantees` ของเราจะขาดข้อที่ต้นทางเพิ่ง freeze และไม่มีอะไรจับ เพราะ drift check เทียบแค่ตัวเลข
* ❌ `transition.reason` จะยังเป็น `{ type: string }` เปล่า ทั้งที่มันคือ leaf ที่ RFC ทั้งฉบับเขียนถึง — **ปิดกฎแล้วไม่ปิดฟิลด์ที่เป็นเหตุให้เขียนกฎ**
* ❌ ใบ `v1.7.1` เขียนเองว่ายังไม่จบและต้องมี ADR — เลือกข้อนี้คือปิดใบด้วยการไม่ทำสิ่งที่ตัวเองบอกว่าต้องทำ

### B. เขียน invariant ลง `guarantees` แต่ไม่แตะฟิลด์

* ✅ `guarantees` ครบตามต้นทาง
* ❌ ผู้อ่านที่เปิด `transition.reason` จะไม่เห็นอะไรบอกว่ามันเป็น leaf ที่ประกาศแล้ว — ต้องอ่าน `guarantees` ท้ายไฟล์แล้วอนุมานเอง
* ❌ ขัดกับเหตุผลของ [ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md) ที่เลือกเขียนคำกำกับ **ที่ตัวฟิลด์** เพื่อให้คำเตือนเดินทางไปกับฟิลด์ทุกที่ที่มันถูกอ่าน

### C. B + ประกาศ `transition.reason` ที่ตัวฟิลด์ + เขียนกฎการประกาศลง `platform_rules` ⭐

* ✅ **ปิดครบทั้งกฎและฟิลด์ที่เป็นเหตุของกฎ**
* ✅ คำกำกับอยู่ที่ตัวฟิลด์ตามหลักของ ADR-0031 — คนที่เปิดมาอ่านเห็นทันทีว่าทำไมมันเป็นตัวชี้ไม่ได้ และใครต้องประกาศ retention
* ✅ **เขียนชัดว่า `agent-platform` ประกาศ retention แทนใครไม่ได้** เพราะเราไม่ได้เป็นผู้เก็บ event ของใคร — ข้อ 3 ของ invariant จึงตกที่ผู้ผลิต ไม่ใช่ที่สัญญา
* ✅ ปิดช่อง `metadata` ไปพร้อมกัน — เป็น open object ที่คีย์ของผู้ผลิตอยู่ใต้กฎ leaf เดียวกัน และ **ข้อห้าม private reasoning ที่มีอยู่แล้วไม่ครอบข้อความของคนที่ไม่ใช่ของโมเดล** ซึ่งเป็นความต่างที่มองข้ามง่ายมาก
* ✅ ยก *"การประกาศต้องเป็นสิ่งที่ตัวตรวจอ่านจริง"* จาก RFC มาเป็น `platform_rules` — ข้อนี้อยู่ใน RFC ที่เรายื่นเอง ถ้าไม่ยกมา จะไม่มีที่ไหนใน contract ที่ consumer อ่านเจอ
* ❌ `guarantees` ยาวขึ้นหนึ่งข้อที่ยาวกว่าข้ออื่นมาก เพราะ invariant มีสามอนุข้อ
* ❌ **กฎทั้งชุด validator กลางบังคับไม่ได้** — ต้องเขียนข้อจำกัดนี้ไว้ในกฎเอง ซึ่งต้นทางทำแล้วและเราคัดมาทั้งท่อน

### D. C + สร้างบล็อก `text_fields` ในสัญญาให้ consumer กรอก

* ✅ ทำให้การประกาศมีรูปกลางที่เทียบกันได้ข้าม consumer
* ❌ **การประกาศเป็นของผู้ผลิต ไม่ใช่ของสัญญา** — ต้นทางเขียนกำกับไว้เองว่าบล็อกนั้น *"อยู่นอก frozen เพราะเป็นของฝั่งเรา"* · ถ้าเราสร้างช่องกลาง เราจะกลายเป็นที่เก็บรายการของคนอื่น ซึ่งเป็นรูปที่ RFC-0013 ปฏิเสธไปแล้วตอนไม่เอาทะเบียนคีย์กลาง
* ❌ เป็นการเดารูปให้ของที่ผู้ผลิตแต่ละรายมีอยู่แล้วคนละแบบ — `care-agent-platform` ประกาศใน `platform-contract.yaml` ของตัวเอง ส่วน `devfactory-core` ประกาศใน `contract-semantics.yaml` ของตัวเอง **และทั้งสองแบบถูกทั้งคู่**

## Recommendation — **C**

**เหตุผล:** A มี precedent จริงแต่ใช้ไม่ได้รอบนี้ เพราะ precedent นั้น (`event/v1` `v1.6.1`) ตั้งอยู่บนข้อเท็จจริงว่า guarantee ใหม่ถูกครอบอยู่แล้ว ซึ่งรอบนี้ไม่จริง · และใบ `v1.7.1` เองก็เขียนไว้ว่ายังไม่จบ · ส่วนการปิดแค่ `guarantees` โดยไม่แตะ `transition.reason` จะทำให้เราเขียนกฎที่ RFC ทั้งฉบับมีไว้เพื่อฟิลด์นั้น แล้วปล่อยฟิลด์นั้นเป็น `{ type: string }` เปล่าไว้เหมือนเดิม — ซึ่งเป็นรูปของ `error/v1.details` ที่เราเพิ่งปิดไปเมื่อ 10 ก.ย. · ปฏิเสธ D เพราะการประกาศเป็นของผู้ผลิต และการสร้างช่องกลางคือทะเบียนที่ RFC ฉบับนี้ปฏิเสธไปแล้วด้วยเหตุผลของมันเอง

**Authority:** รอเจ้าของสัญญาเคาะ — Monthop Champaruang, Platform Owner / Architecture Authority of `agent-platform`

## Consequences

* **`event/v1` `v1.7.1` → `v1.8.0`** — ไม่ breaking · ไม่มี field ใหม่ ไม่แตะ `required` ไม่แตะ `type` · payload ที่ valid วันนี้ยัง valid ทุกใบ · **`approval/v1` ไม่ต้องแก้เพิ่ม** — `v1.2.2` ปิด pointer ไปแล้ว และ `reason` มีกฎห้าม credential/PII/private reasoning อยู่แล้วตั้งแต่ `v1.0.0` (ตรวจแล้ว ไม่ได้เดา)
* **consumer ที่ pin `event/v1` ทั้งสี่รายได้ภาระใหม่ที่ validator ไม่ฟ้อง** — `care-agent-platform` · `devfactory-core` · `ecosystem-intelligence` · `botforge` · ต้องไล่ leaf ของ payload จริงแล้วประกาศว่าอันไหนถือข้อความของคน · **สองรายแรกทำแล้ว** (`care` มี `text_fields` + `cutover` ใน manifest และ `payload_check` อ่านจากใบโดยตรง · `devfactory-core` ประกาศใน `contract-semantics.yaml` ของตัวเอง) · **`ecosystem-intelligence` กับ `botforge` ยังไม่มีใครถาม** และทั้งคู่เป็นผู้ผลิต event
* **drift check จับได้เพราะเทียบ `semantics_version` กับต้นทางจริง** — ไม่ใช่เพราะมีคนสังเกต · แต่มันจับได้แค่ตัวเลข **ไม่ได้ตรวจว่าเนื้อหาของ invariant ถูกคัดมาครบ** · ช่องนี้เปิดอยู่และใบนี้ไม่ได้ปิด
* **ยังไม่ปิด: invariant ผูก `approval/v1` ด้วยหรือไม่** — `semantics_version` เป็นของทั้งไฟล์ แต่ invariant เขียนอยู่ใต้ `event` เท่านั้น ขณะที่ `approval/v1` `reason` เป็นข้อความของคนตามนิยามทุกประการ และต้นทางเองก็ประกาศ `metadata.approval.reason` ไว้ใน `text_fields` ของเขา · **อ่านได้สองทางและเราไม่ใช่เจ้าของ semantics** — ถามที่ต้นทางแล้ว ไม่เดาแทน

## Sources

[RFC-0013](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0013-audit-fields-that-hold-human-text.md) · [`devfactory-core#34`](https://github.com/monthop-gmail/devfactory-core/pull/34) merged 2026-09-17 · `contract-semantics.yaml` `semantics_version: "1.3"` — `event.frozen.invariants` และบล็อก `text_fields` ที่ต้นทางประกาศของตัวเอง · [ADR-0030](0030-the-field-nobody-named.md) · [ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md) — สองใบที่เป็นเหตุให้ RFC นี้เกิด · [#71](https://github.com/monthop-gmail/agent-platform/pull/71) ที่ขยับ pointer และเขียนขอบเขตของตัวเองไว้ · `dis-65134078` `seq 25`–`seq 32` ใน workspace ของ [`ai-collaboration-mcp`](https://github.com/monthop-gmail/ai-collaboration-mcp)
