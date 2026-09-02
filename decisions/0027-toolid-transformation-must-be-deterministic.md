# ADR-0027: `ToolId` คงข้อบังคับไว้ — แต่กฎการแปลงชื่อต้องอยู่ในสัญญา ไม่ใช่ให้แต่ละ consumer คิดเอง

**Status:** Accepted (2026-09-03)
**Date:** 2026-09-03
**Depends on:** [ADR-0026](0026-tool-identity-ceiling-is-namespace-bound.md) · [ADR-0022](0022-agent-may-narrow-its-own-scope.md) · [ADR-0006](0006-contract-versioning.md)
**Blocking:** [issue #59](https://github.com/monthop-gmail/agent-platform/issues/59) · `contracts/tool/v1`

## Context

[#59](https://github.com/monthop-gmail/agent-platform/issues/59) ถามว่า `ToolId` ที่บังคับให้มีจุดควรผ่อนไหม เพราะบล็อกการ pin ของ [`agent-builder-dsh-poc`](https://github.com/monthop-gmail/agent-builder-dsh-poc) และตั้งข้อสังเกตว่า MCP อาจได้รับผลกระทบ **แต่ยังไม่ได้ตรวจ**

**เขาตรวจให้แล้วด้วยการ probe จริง** — `listTools()` กับ server สองตัว ไม่ใช่อ่านจากเอกสาร:

| server | tools | ผ่านแบบชื่อเปล่า | ผ่านเมื่อเติม namespace |
| --- | --- | --- | --- |
| `@modelcontextprotocol/server-filesystem` | 14 | **0** | **14** |
| `ai-collaboration-mcp` | 15 | **0** | **15** |

29/29 เป็นชื่อเปล่า และ **29/29 ผ่านทันทีเมื่อเติม namespace** — สำหรับสองตัวนี้การ map ที่ขอบเขตก็พอ

## แต่ผลที่กว้างกว่านั้นเปลี่ยนคำถาม

connector ของบุคคลที่สาม:

| server | รูปแบบ | ตัวอย่าง | เติม namespace แล้ว |
| --- | --- | --- | --- |
| Canva | **kebab-case** | `comment-on-design` (33 ตัว) | ❌ **ยังไม่ผ่าน** |
| Composio | **SCREAMING_SNAKE** | `COMPOSIO_SEARCH_TOOLS` (7 ตัว) | ❌ **ยังไม่ผ่าน** |

`ToolId` ไม่ได้บังคับแค่ *"ต้องมีจุด"* — **แต่ละ segment ต้องเป็น `[a-z][a-z0-9_]*`** ด้วย

```
canva.comment-on-design         ← ❌ ขีดกลาง
composio.COMPOSIO_SEARCH_TOOLS  ← ❌ ตัวใหญ่
```

**การเติม namespace อย่างเดียวไม่พอ — ต้อง sanitize ด้วย** · และนี่คือจุดที่เปลี่ยนเรื่องทั้งหมด

## เมื่อการแปลงจำเป็น คำถามก็ไม่ใช่ "ผ่อนหรือไม่ผ่อน" อีกต่อไป

ถ้า consumer แต่ละรายแปลงเอง:

```text
Canva `comment-on-design`
  consumer A → canva.comment_on_design
  consumer B → canva.commentOnDesign  (ถ้าเลือก camel) หรือ canva_comment_on_design
        ↓
tool ตัวเดียวกันมี ToolId คนละชุด
        ↓
`deny: [canva.comment_on_design]` ที่ profile คุ้ม A แต่ไม่คุ้ม B — โดยไม่มีอะไรบอก
```

**นี่ทำลายสมมติฐานที่ [ADR-0026](0026-tool-identity-ceiling-is-namespace-bound.md) พึ่งอยู่โดยตรง** — และเกิดจากข้อบังคับของเราเอง ไม่ใช่ความผิดของ server

> ADR-0026 ข้อ 4 บอกว่า deny เชิงชื่อคุ้มเฉพาะ namespace ที่มันตั้งชื่อ · ถ้าชื่อในnamespace นั้นไม่แน่นอน ข้อ 4 ก็ไม่มีความหมาย

## Options

### A. ผ่อน `ToolId` ให้รับชื่อเปล่าและอักขระอื่น

* ✅ ไม่มีใครต้องแปลงอะไร
* ❌ **ต้องผ่อนสองที่พร้อมกัน** — `+`→`*` ไม่พอ ต้องเปิด character class ให้รับ `-` และตัวใหญ่ด้วย
* ❌ `search` จากสอง registry ชนกันทันที · ADR-0026 ทั้งใบพึ่ง namespace อยู่
* ❌ ทิ้งเจตนา *"อ่านแล้วต้องเดาผลกระทบได้"* ที่ `tool/v1` เขียนไว้เอง

### B. คงข้อบังคับ + **ตีพิมพ์กฎการแปลงให้เป็นบรรทัดฐาน** ⭐

* ✅ **การแปลงเป็น deterministic** — สอง consumer ที่ต่อ server เดียวกันได้ `ToolId` ชุดเดียวกัน ซึ่งเป็นเงื่อนไขที่ ADR-0026 ต้องการ
* ✅ ไม่มี field ใหม่ · ไม่แตะ pattern · ไม่ breaking
* ✅ พิสูจน์แล้วว่าทำได้จริง — `agent-builder-dsh-poc` เดินทางนี้แล้วและ **`agent/v1alpha2` ไม่ต้อง bump** เพราะไม่มีอะไรที่ผู้ใช้เขียนเปลี่ยน · ข้อสันนิษฐานเดิมที่ว่าต้อง bump **ผิด**
* ❌ ทุกคนที่ต่อ MCP ต้องมี mapping layer — แต่เป็นภาระที่ **ตัดสินใจอย่างรู้ตัว** แทนที่จะเป็นผลข้างเคียง

### C. คงข้อบังคับ แต่ปล่อยให้ consumer แปลงเอง (สถานะปัจจุบัน)

* ✅ ไม่ต้องเขียนอะไรเพิ่ม
* ❌ **`ToolId` ของ tool ตัวเดียวกันไม่ตรงกันข้าม consumer** — ทำลายฐานของ ADR-0026 เงียบ ๆ

## Decision

**B** — คง `ToolId` ไว้ · ตีพิมพ์กฎการแปลงให้เป็นบรรทัดฐานที่ deterministic

**Reason:** ข้อมูลที่ probe มาเปลี่ยนคำถาม — เดิมเป็น *"ผ่อน `ToolId` ไหม"* แต่พอพบว่า connector จำนวนไม่น้อยต้อง **sanitize ไม่ใช่แค่ prefix** คำถามจริงกลายเป็น *"ใครเป็นคนกำหนดการแปลง"* · ถ้าปล่อยให้แต่ละ consumer คิดเอง tool ตัวเดียวกันจะมี `ToolId` คนละชุด และ [ADR-0026](0026-tool-identity-ceiling-is-namespace-bound.md) ที่เพิ่งวางกฎเพดานเชิงชื่อไว้จะไม่มีความหมาย — **ความเสียหายนี้เกิดจากข้อบังคับของเราเอง เราจึงต้องเป็นคนกำหนดการแปลง** · ปฏิเสธ A เพราะต้องผ่อนสองที่และทิ้ง namespace ที่ ADR-0026 พึ่งอยู่ทั้งใบ

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### กฎการแปลง — ต้อง deterministic ไม่งั้นไม่มีประโยชน์

```text
1. lowercase
2. อักขระนอก [a-z0-9_] → `_`  ทีละตัว **ห้ามยุบซ้ำ**
   (`a--b` → `a__b` ไม่ใช่ `a_b` — การยุบสร้างการชนเพิ่มโดยไม่จำเป็น
    และ `a__b` ถูกต้องตาม pattern อยู่แล้ว)
3. เติม segment ของ namespace ไว้หน้า — สำหรับ MCP คือ `server_id`
4. ถ้าผลลัพธ์ยัง **ไม่ match `ToolId`** (เช่นชื่อขึ้นต้นด้วยตัวเลข `2fa_setup`)
   → **reject แล้วบังคับ mapping ที่เขียนมือ ห้ามเดา prefix ให้**
5. ถ้าแปลงแล้ว **ชนกัน** → **reject ไม่ใช่เลือกอันใดอันหนึ่ง**
```

**ข้อ 5 คือข้อที่สำคัญที่สุด** และเหตุผลของผู้รายงานตรงแล้ว:

> การชนเกิดจาก **การแปลงของเรา ไม่ใช่ความผิดของ server** — ปล่อยให้เงียบแปลว่า tool คนละตัวอยู่หลัง id เดียวกัน และ policy ที่เขียนถึงตัวหนึ่งจะไปคุมอีกตัวโดยไม่มีใครรู้

หลักเดียวกับ *"reject ไม่ใช่ coerce"* ที่ `consent/v1` ใช้กับ tenant ที่ไม่ตรง และ [ADR-0022](0022-agent-may-narrow-its-own-scope.md) ใช้กับ `required` ที่ตัดกับ `deny`

**ข้อ 4 เป็นของที่ผู้รายงานยังไม่ได้ครอบ** — `2fa_setup` เติม namespace แล้วเป็น `canva.2fa_setup` ซึ่ง segment ท้ายขึ้นต้นด้วยตัวเลข ยังตกอยู่ดี · การเดา prefix ให้ (`x_2fa_setup`) จะทำให้ผลไม่ deterministic ข้าม implementation ซึ่งย้อนแย้งกับเหตุผลทั้งหมดของ ADR ฉบับนี้

### `namespace` มาจากไหน — และข้อจำกัดที่ต้องบันทึก

สำหรับ MCP คือ `mcp/v1` `server_id` · **`server_id` เป็น `Id` ที่ unique ภายใน tenant/workspace ไม่ใช่ทั้งโลก** — สอง workspace ที่ตั้ง `server_id` เหมือนกันจะได้ `ToolId` ชุดเดียวกัน ซึ่งถูกต้องเพราะ `ToolId` ก็อยู่ใต้ tenant เหมือนกัน · บันทึกไว้ให้ชัดว่าขอบเขตของความ unique คือ tenant ไม่ใช่ global

### ⚠️ `mcp/v1.exposes` เก็บชื่ออะไร — ตอบเป็นกฎ ยังไม่สร้าง field

ผู้รายงานถามตรง ๆ และคำถามถูก: ถ้า `exposes` เก็บชื่อ**หลังแปลง** ชื่อที่ server รู้จักจะหายไป และ **ไม่มีที่ไหนบันทึก mapping** → audit ย้อนจาก `ToolId` กลับไปหา tool จริงไม่ได้

เป็นแผลตระกูลเดียวกับที่ปิดไปแล้วสี่ครั้ง — **record ที่อ่านคนเดียวแล้วได้ความจริงไม่ครบ**

**แต่ยังไม่มีใคร pin `mcp/v1` และไม่มีใครผลิต payload ของมัน** — การออกแบบรูปของ mapping record ตอนนี้คือเดารูปให้งานที่ยังไม่มีใครทำ ซึ่งเป็นเหตุผลเดียวกับที่ [ADR-0025](0025-provider-switch-and-what-identity-covers.md) ไม่สร้าง field ให้ cost attribution และ [#50](https://github.com/monthop-gmail/agent-platform/issues/50) ไม่เพิ่ม `embedding`

เขียนกฎไว้แทน:

> **การแปลงต้องย้อนกลับได้** — ผู้ที่ขึ้นทะเบียน tool จาก server ภายนอกต้องเก็บชื่อเดิมไว้ให้ audit ตามกลับไปได้ · รูปกลางของบันทึกนั้นรอ consumer รายแรกที่ pin `mcp/v1`

### ไม่ bump major — `tool/v1` `v1.0.0` → `v1.1.0`

ไม่มี field · ไม่แตะ `ToolId` pattern · `required` ไม่ขยับ — เพิ่ม `platform_rules` ที่เขียนกฎซึ่งไม่เคยเขียน

## Consequences

* **`ToolId` ของ tool ตัวเดียวกันตรงกันข้าม consumer เป็นครั้งแรก** — เงื่อนไขที่ ADR-0026 ต้องการแต่ไม่เคยมีอะไรรับประกัน
* `agent-builder-dsh-poc` pin `agent/v1` และ `tool/v1` ได้แล้ว (ทำไปแล้วก่อน ADR นี้จะเคาะ) และ **`agent/v1alpha2` ไม่ต้อง bump** — ข้อสันนิษฐานเดิมผิด
* ทุกคนที่ต่อ MCP ต้องมี mapping layer — **ภาระที่ตัดสินใจอย่างรู้ตัว** ไม่ใช่ผลข้างเคียงของ pattern
* **drift check ตรวจข้อนี้ไม่ได้** — การแปลงเกิดที่ runtime ของ consumer · พิสูจน์ได้จากเทสของ consumer ที่ probe server จริงเท่านั้น แบบที่ผู้รายงานทำ
* ยังไม่ปิด: **รูปของบันทึก mapping ใน `mcp/v1`** — รอ consumer รายแรกที่ pin

## Sources

[issue #59](https://github.com/monthop-gmail/agent-platform/issues/59) และคอมเมนต์ที่ probe MCP จริง · [`agent-builder-dsh-poc`](https://github.com/monthop-gmail/agent-builder-dsh-poc) commit `f723a67` · [ADR-0026](0026-tool-identity-ceiling-is-namespace-bound.md) ข้อ 4 · [ADR-0025](0025-provider-switch-and-what-identity-covers.md) เหตุผลที่เขียนกฎก่อนสร้าง field · `tool/v1` `$defs.ToolId` · `mcp/v1` `exposes`
