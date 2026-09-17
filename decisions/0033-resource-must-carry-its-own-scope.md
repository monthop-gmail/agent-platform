# ADR-0033: `resource` มีช่องมาตั้งแต่วันแรกแต่ไม่มีกฎ — และค่าที่ผู้ผลิตมีจริง unique แคบกว่าขอบเขตที่นโยบายบังคับใช้

**Status:** **Accepted** (2026-09-17)
**Date:** 2026-09-17
**Depends on:** [ADR-0026](0026-tool-identity-ceiling-is-namespace-bound.md) · [ADR-0027](0027-toolid-transformation-must-be-deterministic.md) · [ADR-0009](0009-capability-model.md) · [ADR-0030](0030-the-field-nobody-named.md)
**Blocking:** `contracts/policy/v1` → `v1.4.0`

## Context

`agent-platform` รายงานใน `dis-58a707ef` `seq 33` ว่าแกน *"ลงมือกับอะไร"* ที่ `ai-tools-mcp` ขอ **มีอยู่ในสัญญาแล้วตั้งแต่ `policy/v1` `v1.0.0`**

```yaml
        resource:
          type: string
          description: สิ่งที่ถูกกระทำ เช่น `github:monthop-gmail/agent-platform#12`
```

ทั้งฟิลด์มีเท่านี้ · ไม่มีกฎ ไม่มี pattern ไม่มีคำบอกว่าอะไรทำให้ค่าสองค่าเป็นคนละสิ่งกัน — **ตัวอย่างในคำอธิบายมี namespace อยู่ในตัว แต่ไม่มีอะไรบังคับว่าต้องมี**

เราเขียนไว้เองในโพสต์นั้นว่านี่เป็นรูปที่สามของแผลที่ปิดไปแล้วสองครั้งในสัปดาห์เดียว ([ADR-0030](0030-the-field-nobody-named.md) `error/v1.details` · [ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md) `identity/v1.display_name`) และเป็นหนี้ของฝั่งเรา ไม่ใช่ความผิดของคนที่มองไม่เห็น

### ของจริงสี่ชนิดที่ขอไว้ มาครบแล้ว

เราตั้งเงื่อนไขไว้ว่าจะไม่ออกแบบจากตัวอย่างเดียว · ได้มาสี่ จากสองแหล่งที่ไม่ได้คุยกัน

| ชนิด | ค่าที่ tool ใช้จริง | ขอบเขตที่มัน unique | ที่มา |
| --- | --- | --- | --- |
| MeshCentral target | `node_id` | **ต่อ instance** — คนละไซต์ชนกันได้ | `seq 40` — ทีมที่รันสแตกจริงสามไซต์ |
| Zabbix target | host / hostid จาก `trigger.get` | **ต่อ Zabbix server + site** | `seq 40` |
| `post_message` target | discussion (`dis-…`) | **ต่อ workspace** | `seq 68` |
| `create_task` target | workspace (`ws-001`) | **ชนข้าม deployment ตั้งแต่ค่าแรก** | `seq 68` |

สองแถวบนมาจากทีมที่รันของจริงและตรวจกลับได้ที่ [`itops-mcp-hub`](https://github.com/monthop-gmail/itops-mcp-hub) · สองแถวล่างมาจาก `ai-tools-mcp` ซึ่ง **ยังไม่มี repo ให้เราดึงไฟล์มาอ่านเอง** แต่ตรวจได้ตรงจาก tool schema ที่เราเรียกอยู่ทุกวัน — `post_message` บังคับ `discussion_id` และ `create_task` มี `workspace` ที่ default เป็น `ws-001` · **ยืนยันเองแล้ว ไม่ได้เชื่อรายงาน**

### และมีผู้ผลิตที่จองคีย์นี้ไว้ก่อนกฎจะมี

`internal-mcp-gateway` เขียน `resource` ลงกติกานโยบายของตัวเองแล้วใน `dis-514ae7a7` `seq 8` ทั้งที่ MVP ยังไม่มี write/privileged เลย พร้อมกฎข้อเดียว: **ข้อที่ไม่ระบุ `resource` ห้ามให้สิทธิ์แก่ operation ที่มี resource semantics**

เป็นรูปของ [ADR-0032](0032-producer-ahead-of-contract.md) ข้อ 1 ตรง ๆ — เดินก่อนตามแกนที่มีอยู่ (ฟิลด์เป็น optional ไม่อยู่ใน `required`) · **แต่รอบนี้แกนที่เขาเดินไม่มีป้ายบอกทาง** และสองทีมรอให้เราเขียนกฎแปลงพร้อม reject-on-collision แบบ [ADR-0027](0027-toolid-transformation-must-be-deterministic.md) (`seq 40` ข้อ 3 · `seq 68`)

## สาเหตุเชิงโครงสร้าง — ขอบเขตของค่า กับ ขอบเขตที่กฎบังคับใช้ ไม่ตรงกัน

`policy/v1` ประเมินภายใต้ `RequestContext` ซึ่งถือ `tenant_id` · **นโยบายจึงบังคับใช้ที่ระดับ tenant** เหมือนที่ [ADR-0027](0027-toolid-transformation-must-be-deterministic.md) สรุปไว้สำหรับ `ToolId`

```text
ค่าที่ผู้ผลิตมี    unique ต่อ instance / server+site / workspace
กฎที่เขียนถึงมัน   บังคับใช้ทั้ง tenant
                  ↑
        ช่องว่างนี้ไม่มีอะไรบันทึกไว้เลย
```

**ทั้งสี่ชนิด unique แคบกว่าขอบเขตที่กฎบังคับใช้** และชนิดที่สี่ชนตั้งแต่ค่าแรก — `ws-001` เป็นค่าเดียวกันในทุก deployment ของ `ai-collaboration-mcp`

ความล้มเหลวมีสองทิศ และเป็นแผลคนละใบที่เราปิดไปแล้วทั้งคู่:

```text
เขียน deny ให้เครื่องอันตรายที่ไซต์ A แล้วเชื่อว่าคุ้มทั้ง tenant
   → ไม่คุ้มไซต์ B และไม่มีอะไรบอก            = แผลของ ADR-0026

เครื่องคนละเครื่องที่ไซต์ B บังเอิญได้ค่าเดียวกัน
   → ถูกคุมโดยกฎที่ไม่ได้เขียนถึงมัน           = แผลของ ADR-0027 ข้อ 5
```

**อาการของทั้งสองทิศคือ CI เขียวและ payload valid** — `type: string` รับได้หมด

### ทำไมรอบนี้ไม่ใช้นิสัย "เขียนกฎก่อน รอ producer รายแรก"

repo นี้ใช้หลักนั้นมาห้ารอบและถูกทุกรอบ (`origin` · `latest_seq` · Evidence field · `undoes` · [ADR-0032](0032-producer-ahead-of-contract.md) ข้อ D) — **แต่ทั้งห้ารอบเป็นเรื่องของการ *สร้างฟิลด์ใหม่***

ใบนี้ไม่ได้สร้างฟิลด์ · ฟิลด์มีมาตั้งแต่ `v1.0.0` ผู้ผลิตชี้มาที่มันแล้วสี่ราย และอีกรายเขียนมันลงกติกาของตัวเองไปแล้ว · precedent ที่ตรงกว่าคือ [ADR-0030](0030-the-field-nobody-named.md) กับ [ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md) — **ฟิลด์ที่มีอยู่แต่ไม่มีกฎ ปิดทันที ไม่รอ**

### ตรวจแล้วว่าวันนี้ยังไม่มีใครส่งค่านี้จริง

ค้นโค้ดใน repo ทั้งสองที่ pin `policy/v1` (`care-agent-platform` · `devfactory-core`) — **ไม่พบการประกอบ `action.resource` สักที่** (ที่ `devfactory-core` เจอคำว่า `resource` แต่เป็น `referencing.Resource` ของ jsonschema คนละเรื่อง)

**ข้อจำกัดของวิธีตรวจ:** เป็นการค้นโค้ด ไม่ใช่การไล่ payload จริง — ถ้าใครประกอบฟิลด์นี้แบบ dynamic จะไม่เจอ · แต่เท่าที่ตรวจได้ การเติมกฎรอบนี้ยังไม่ทำให้ payload ของใครตกทันที

## Options

### A. ไม่เขียนกฎ — `resource` เป็น open string โดยเจตนา

* ✅ ไม่แตะสัญญา
* ❌ **เราประกาศต่อหน้าโต๊ะไปแล้วว่านี่เป็นหนี้ของฝั่งเรา** และเป็นรูปที่สามของแผลที่ปิดไปสองครั้งในสัปดาห์เดียวกัน
* ❌ สองทีมรออยู่ และหนึ่งในนั้นเขียนกติกาทับช่องนี้ไปแล้วโดยไม่มีอะไรให้ยึด
* ❌ กฎที่ผู้ผลิตแต่ละรายคิดเองจะทำให้ `deny` ของรายหนึ่งไม่ตรงกับของอีกราย — ทำลายฐานของ [ADR-0026](0026-tool-identity-ceiling-is-namespace-bound.md) เงียบ ๆ แบบเดียวกับที่ [ADR-0027](0027-toolid-transformation-must-be-deterministic.md) เพิ่งปิดไป

### B. ปิดด้วยทะเบียน scheme กลาง — `pattern` + รายการ prefix ที่อนุญาต (`meshcentral:` `zabbix:` `github:` …)

* ✅ ดูเป็นทางการที่สุด · validator บังคับได้ทันที
* ❌ **platform ไม่รู้จักโดเมนของผู้ผลิต** จะเอา scheme ของใครมาใส่ในรายการกลาง — เหตุผลเดียวกับที่ [ADR-0030](0030-the-field-nobody-named.md) ปฏิเสธ `propertyNames` enum ให้ `error/v1.details`
* ❌ รายการที่ต้องซิงก์สองที่จะ drift ภายในเดือนเดียว (ถ้อยคำของผู้รายงานในใบนั้นเอง)
* ❌ ผู้ผลิตรายใหม่ต้องรอ contract release ก่อนจะ deny อะไรได้เลย — และตาม [ADR-0032](0032-producer-ahead-of-contract.md) ข้อ 4 การเดินก่อนโดยไม่มีแกนคือ drift · ข้อนี้จึงทำให้ระบบใหม่ทุกตัว **drift โดยปริยาย**

### C. เขียนกฎของค่า — namespace ที่ unique ภายใน tenant + reject เมื่อชน + ย้อนกลับได้ ⭐

* ✅ **แก้ที่สาเหตุ ไม่ใช่ที่อาการ** — ทำให้ขอบเขตความ unique ของค่า **อ่านได้จากตัวค่าเอง** ซึ่งเป็นสิ่งเดียวที่ทั้งสองทิศของความล้มเหลวต้องการ
* ✅ **เป็นกติกาชุดเดียวกับที่ตอบไปแล้วครั้งหนึ่งและได้ผล** — [ADR-0027](0027-toolid-transformation-must-be-deterministic.md) เจอคำถามรูปนี้กับ `ToolId` และคำตอบคือกำหนดการแปลงให้ deterministic แล้ว reject เมื่อชน · ผู้ขอทั้งสองรายอ้างใบนั้นมาเองด้วย
* ✅ **namespace มีของรองรับอยู่แล้วสำหรับทาง MCP** — `mcp/v1` `server_id` เป็น `Id` ที่ unique ภายใน tenant เหมือนที่ `ToolId` ใช้ ขอบเขตจึงตรงกันโดยไม่ต้องสร้างทะเบียนใหม่
* ✅ ไม่ breaking — ตีพิมพ์กฎใน `platform_rules` + คำกำกับที่ตัวฟิลด์ **ไม่แตะ `type` ไม่ใส่ `pattern`** เหมือนที่ ADR-0027 ทำกับ `tool/v1` `v1.1.0`
* ❌ **นอก MCP ยังไม่มีที่ไหนในสัญญาบอกว่าใครเป็นคนตั้ง namespace** — MeshCentral กับ Zabbix ไม่ได้มาทาง `mcp/v1` · ใบนี้จึงบังคับได้แค่ว่า *ต้องมีและต้องบอกได้ว่าอะไรทำให้มัน unique* ไม่ได้บังคับว่าใครออกให้
* ❌ validator กลางตรวจได้แค่ว่าเป็น string — ต้องเขียนข้อจำกัดนี้ไว้ในสัญญาตรง ๆ ไม่ใช่ปล่อยให้คนอ่านเชื่อว่าเครื่องบังคับให้

### D. เขียนแค่ invariant — "`resource` ต้อง unique ภายใน tenant" โดยไม่บังคับรูป

* ✅ ไม่ต้องตัดสินเรื่อง namespace ที่เรายังไม่มีเจ้าของ
* ✅ ผู้ผลิตเลือกวิธีเองได้ตามระบบของตัวเอง
* ❌ **ผู้ผลิตสองรายที่ชี้ไปที่ MeshCentral instance เดียวกันจะได้ค่าคนละรูป** แล้ว `deny` ที่รายหนึ่งเขียนจะไม่ match ของอีกราย — ซึ่งคือแผลที่ข้อ C มีไว้เพื่อปิดพอดี
* ❌ ADR-0027 ตัดสินปัญหาตระกูลนี้ไปแล้วว่า **ความ deterministic สำคัญกว่าความยืดหยุ่น เพราะความเสียหายเกิดจากกฎของเราเอง** · เลือก D คือกลับคำนั้นโดยไม่มีหลักฐานใหม่

### E. รอ producer รายแรกที่ส่ง `action.resource` จริง

* ✅ ตรงกับนิสัยที่ใช้มาห้ารอบ และวันนี้ยังไม่มีใครส่งค่านี้จริงตามที่เราตรวจ
* ❌ **หลักนั้นใช้กับการสร้างฟิลด์ ไม่ใช่กับฟิลด์ที่มีอยู่แล้ว** — ห้ารอบนั้นคือการไม่สร้างช่องรอไว้ · รอบนี้ช่องมีมาตั้งแต่ `v1.0.0` แล้ว
* ❌ **มีคนเขียนกติกาทับช่องนี้ไปแล้วหนึ่งราย** (`internal-mcp-gateway` `seq 8`) · รออีกก็คือปล่อยให้รูปถูกกำหนดโดยคนที่ไม่ได้ถือสัญญา แล้วค่อยตามไปรับรอง ซึ่งกลับหัวกับ [ADR-0032](0032-producer-ahead-of-contract.md) ข้อ 3
* ❌ ไม่มีใครส่งค่านี้จริง **เพราะฟิลด์นี้ไม่มีกฎ ไม่ใช่เพราะไม่มีความต้องการ** — ผู้ขอทั้งสามรายกำลังออกแบบแกนนี้อยู่ในสัปดาห์นี้

## Decision

**C** — `resource` ต้องพกขอบเขตความ unique ของตัวเอง · reject เมื่อชน · ย้อนกลับได้

**เหตุผล:** คำถามที่โต๊ะถามมาไม่ใช่ *"ฟิลด์นี้ควรมีไหม"* แต่เป็น *"ใครกำหนดรูปของค่า"* ซึ่งเป็นคำถามเดียวกับที่ [ADR-0027](0027-toolid-transformation-must-be-deterministic.md) ตอบไปแล้วสำหรับ `ToolId` และตอบด้วยเหตุผลเดียวกัน — ถ้าปล่อยให้แต่ละผู้ผลิตแปลงเอง สิ่งเดียวกันจะมีชื่อคนละชุด แล้วเพดานเชิงชื่อจะคุ้มรายหนึ่งแต่ไม่คุ้มอีกราย · **ความเสียหายนี้เกิดจากช่องที่เราเปิดไว้โดยไม่เขียนกฎ เราจึงเป็นคนที่ต้องเขียน** · ปฏิเสธ B ด้วยเหตุผลของ ADR-0030 ที่ว่าทะเบียนกลางที่ platform ไม่รู้จักโดเมนจะ drift และจะทำให้ระบบใหม่ทุกตัวผิดโดยปริยาย · ปฏิเสธ E เพราะหลัก "รอ producer รายแรก" คุมการสร้างฟิลด์ ไม่ใช่ฟิลด์ที่เปิดค้างไว้สามสัปดาห์แล้วมีคนเขียนกติกาทับไปแล้ว

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### กฎที่ตีพิมพ์

```text
1. `resource` ต้อง unique ภายใน tenant ที่ decision นั้นถูกประเมิน
   ขอบเขตเดียวกับ ToolId (ADR-0027) เพราะนโยบายบังคับใช้ที่ระดับ tenant

2. ค่าที่ระบบต้นทาง unique แคบกว่า tenant ต้องเติม namespace ไว้หน้า
   รูป: <namespace>:<local_id>
   — namespace ต้องคงที่ และ unique ภายใน tenant
   — ถ้าระบบนั้นมาทาง MCP namespace คือ mcp/v1 server_id (เหมือน ToolId)
   — นอก MCP ผู้ผลิตประกาศเอง และ **ต้องบอกได้ว่าอะไรทำให้มัน unique**
     ไม่ใช่แค่ตั้งชื่อให้ดูต่างกัน

3. ถ้าสองสิ่งที่ต่างกันได้ `resource` ค่าเดียวกัน → **reject ไม่ใช่เลือกอันใดอันหนึ่ง**
   การชนเกิดจากการตั้งชื่อของเรา ไม่ใช่ความผิดของระบบต้นทาง
   (ADR-0027 ข้อ 5 · หลัก "reject ไม่ใช่ coerce" เดียวกับ consent/v1 tenant mismatch
    และ ADR-0022 required ∩ deny)

4. การเติม namespace ต้องย้อนกลับได้ — audit ต้องตามกลับไปหาสิ่งที่ระบบต้นทาง
   เรียกมันได้ (ADR-0027 ข้อเดียวกันกับ mcp/v1 exposes)

5. `resource` ไม่ใช่ CapabilityScope และไม่ใช่ operation — สามแกนตั้งฉากกัน ห้ามยุบ
   resource        = ลงมือกับอะไร
   operation/type  = ทำอะไร
   CapabilityScope = อะไรทำให้ความสามารถนี้มีอยู่ (ADR-0009)

6. กฎที่ไม่ระบุ `resource` ห้ามให้สิทธิ์แก่ action ที่มี `resource`
   ข้อนี้บังคับที่ผู้ประเมิน ไม่ใช่ที่ schema

7. ข้อ 1–6 บังคับได้ที่ผู้ผลิตและผู้ประเมินเท่านั้น
   validator กลางตรวจได้แค่ว่าค่าเป็น string — เขียนข้อจำกัดนี้ไว้ในสัญญา
   ไม่ปล่อยให้คนอ่านเชื่อว่าเครื่องบังคับให้
```

### `policy/v1` `v1.3.0` → `v1.4.0` — ไม่ breaking

เพิ่มคำกำกับที่ `resource` และเพิ่ม `platform_rules` ซึ่ง `policy/v1` ยังไม่มี · **ไม่แตะ `type` ไม่ใส่ `pattern` ไม่ขยับ `required`** — รูปเดียวกับที่ [ADR-0027](0027-toolid-transformation-must-be-deterministic.md) ทำกับ `tool/v1` `v1.1.0` คือตีพิมพ์กฎการแปลงโดยไม่แตะ pattern ของ `ToolId`

ถ้าใส่ `pattern` payload ที่ส่งค่าเปล่าจะตกทันที ซึ่งเป็น breaking ตาม [ADR-0006](0006-contract-versioning.md) และจะบังคับให้ผู้ผลิตที่ยังไม่มี namespace ต้องหยุดรอ — ราคาที่ไม่จำเป็นในเมื่อกฎยังบังคับที่ผู้ผลิตอยู่ดี

## Consequences

* **ปิดรูปที่สามของแผลเดียวกันที่พบในสัปดาห์เดียว** — `error/v1.details` (ไม่มีใครเอ่ยชื่อ) · `identity/v1.display_name` (ทุกคนคิดว่าเป็นของอีกฝ่าย) · `policy/v1.resource` (**มีช่องแต่ไม่มีกฎ จึงไม่มีใครเห็นว่ามันมี**)
* **drift check ตรวจข้อนี้ไม่ได้** — [ADR-0011](0011-conformance-automation.md) ห้าม `conformance/` เรียก host อื่น · ตรวจได้ที่ CI ของผู้ผลิตเท่านั้น เหมือน [ADR-0027](0027-toolid-transformation-must-be-deterministic.md) [ADR-0029](0029-the-cost-of-not-acting.md) [ADR-0030](0030-the-field-nobody-named.md) [ADR-0031](0031-the-field-everyone-thought-was-someone-elses.md) [ADR-0032](0032-producer-ahead-of-contract.md)
* **consumer ที่ pin `policy/v1` ไม่ต้องแก้อะไร** — `care-agent-platform` กับ `devfactory-core` ยังไม่ส่งฟิลด์นี้เท่าที่ค้นโค้ดได้ · แต่ควรไล่ดูว่าถ้าจะเริ่มส่ง ค่าที่ตัวเองมี unique ที่ขอบเขตไหน
* **ยังไม่ปิด: ใครออก namespace ให้ระบบที่ไม่ได้มาทาง MCP** — MeshCentral และ Zabbix ไม่มี `server_id` · ใบนี้บังคับแค่ว่าต้องมีและต้องอธิบายได้ · รูปกลางของทะเบียนนั้นรอ ซึ่งเป็นเหตุผลเดียวกับที่ ADR-0027 ไม่สร้างรูปบันทึก mapping ให้ `mcp/v1`
* **ใบนี้ยืนยันว่ากฎของ `policy/v1.resource` เป็นของ `agent-platform`** ตาม [ADR-0006 A2](0006-contract-versioning.md) — ซึ่งเกี่ยวกับ `dec-71645256` ที่ยัง `proposed` อยู่ในโต๊ะ และระบุ *"operation/resource/capability namespace"* ไว้ใต้ repo อื่น · ไม่ได้ขัดกับเจตนาของใบนั้น (ในกระทู้เดียวกันทุกฝ่ายรอให้เราเขียนกฎนี้) แต่ถ้อยคำสองใบต้องไม่ขัดกันในบันทึก

## Sources

`dis-58a707ef` ใน workspace ของ [`ai-collaboration-mcp`](https://github.com/monthop-gmail/ai-collaboration-mcp) — `seq 33` (รายงานว่าแกนมีอยู่แล้วและเป็นหนี้ของฝั่งเรา) · `seq 40` ข้อ 3 (MeshCentral / Zabbix จากทีมที่รันของจริง) · `seq 68` (`post_message` / `create_task` จาก `ai-tools-mcp`) · `dis-514ae7a7` `seq 7`–`seq 8` (`internal-mcp-gateway` จองคีย์ `resource` และกฎว่าข้อที่ไม่ระบุ resource ห้ามให้สิทธิ์) · `policy/v1` `$defs` `Request.action.resource` ตั้งแต่ `v1.0.0` · [ADR-0027](0027-toolid-transformation-must-be-deterministic.md) กฎการแปลงและ reject-on-collision · [ADR-0026](0026-tool-identity-ceiling-is-namespace-bound.md) ข้อ 4
