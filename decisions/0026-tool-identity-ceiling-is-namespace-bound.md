# ADR-0026: เพดานที่เขียนด้วยชื่อ tool ผูกกับ namespace ที่มันตั้งชื่อ — ใช้ข้าม registry ไม่ได้เงียบ ๆ

**Status:** Accepted (2026-09-02)
**Date:** 2026-09-02
**Depends on:** [ADR-0022](0022-agent-may-narrow-its-own-scope.md) · [ADR-0010](0010-risk-approval-taxonomy.md) · [ADR-0012](0012-consent-contract.md)
**Blocking:** [issue #53](https://github.com/monthop-gmail/agent-platform/issues/53) · `contracts/profile/v1`

## Context

[#53](https://github.com/monthop-gmail/agent-platform/issues/53) รายงานว่า `profile.tools.allow` เป็น allowlist ค่าตายตัว — consumer ที่มี tool ของตัวเองใช้ profile กลางเป็นเพดานแล้ว **intersect ได้ศูนย์**

```text
{dsh.web.fetch, dsh.fs.read} ∩ {github.issue.read, git.commit.create, …} = ∅
และ schema เขียนว่า ว่าง = ไม่อนุญาต tool ใดเลย
```

## ตรวจแล้วเจอด้านที่อันตรายกว่า — profile เดียวกัน **จำกัดเกินและปกป้องไม่พอพร้อมกัน**

`profiles/coding-agent` มีทั้งสองฝั่ง:

```yaml
tools:
  allow: [github.issue.read, git.commit.create, fs.file.read, shell.execute, …]
  deny:  [github.pr.merge, deploy.production.run, secret.read]
```

เอาไปใช้กับ agent ที่มี tool ใน namespace `dsh.*`:

| | ผลลัพธ์ | ทิศทางของความล้มเหลว |
| --- | --- | --- |
| `allow` | ไม่ตรงสักตัว → **ไม่มี tool เหลือเลย** | ❌ fail **closed** — ใช้งานไม่ได้ แต่เห็นทันที |
| `deny` | ไม่ตรงสักตัว → **ไม่ปิดอะไรเลย** | ☠️ fail **open** — *"profile นี้ห้าม merge"* กลายเป็นความเชื่อที่ไม่จริง **โดยไม่มีอะไรบอก** |

**นี่คือสิ่งที่ #53 ยังไม่ได้ชี้** — ฝั่ง `deny` อันตรายกว่าฝั่ง `allow` มาก เพราะฝั่งแรกพังให้เห็น ส่วนฝั่งหลังเงียบ

profile ที่เขียนด้วยชื่อจาก namespace หนึ่ง **ไม่ได้แปลว่าไม่มีผลกับอีก namespace — มันแปลว่าไม่มีใครรู้ว่ามันมีผลหรือเปล่า**

## เพดานเชิงคุณสมบัติมีอยู่แล้วครึ่งหนึ่ง แต่ไม่มีใครต่อสาย

`profiles/coding-agent` ประกาศเจตนาเดียวกัน **สองครั้ง** — ครั้งหนึ่งแบบพกพาได้ อีกครั้งแบบผูกกับชื่อ:

```yaml
capability_requirement:
  required: [code_execution, filesystem, git]
policy:
  deny_capabilities: [autonomous_execution]
tools:
  allow: [github.issue.read, …]        # ← ผูกกับชื่อ
```

และ `tool/v1` ประกาศคุณสมบัติของ tool ไว้แล้วเช่นกัน:

```yaml
action_risk:           # ADR-0010
required_capabilities: # capability ที่ subject ต้องมีจึงจะเรียกได้
```

**แต่ไม่มีที่ไหนเขียนว่าสองอย่างนี้ประกอบกันยังไง** — `grep -rn required_capabilities contracts/` ได้ผลลัพธ์เดียวคือที่นิยามตัวเอง

```text
tool ประกาศ:      required_capabilities: [shell]
profile ประกาศ:   deny_capabilities: [shell]
        ↓
tool นั้นใช้ไม่ได้ — ชัดเจนสำหรับคน แต่ไม่มีกฎไหนเขียนไว้
```

ต่อสายนี้แล้ว **เพดานเชิงคุณสมบัติจะทำงานกับ tool registry ที่ platform ไม่เคยเห็น** ซึ่งเป็นสิ่งเดียวที่ platform เขียนได้จริง — เพราะ platform ไม่รู้จักชื่อ tool ของใคร และ[ไม่ควรรู้](0012-consent-contract.md)

## `allow` ที่หายไป กับ `allow: []` แปลว่าคนละอย่าง — และตอนนี้ไม่มีใครบอก

schema เขียนแค่ *"ว่าง = ไม่อนุญาต tool ใดเลย"* · **ไม่ได้เขียนว่าไม่มี field เลยแปลว่าอะไร**

repo นี้ห้ามความกำกวมแบบนี้ทุกที่ — `expires_at: null` · `conditions: []` · `provider_switches: []` ล้วนมีนิยามชัด · ที่นี่กลับปล่อยไว้ ทั้งที่เป็นตัวตัดสินว่า profile มีเพดานเชิงชื่อหรือไม่

## Options

### A. ให้ `tools.allow` รับ pattern (`dsh.*`)

* ✅ profile กลางเขียนเพดานที่ครอบ namespace อื่นได้
* ❌ **`deny` ต้องรับ pattern ด้วย** ไม่งั้น allow กว้างกว่าที่ deny ตามทัน = ละเมิด *"ค่าที่กว้างที่สุดชนะไม่ได้"*
* ❌ ไม่แก้ปัญหาที่แท้จริง — platform ยังต้องเดา namespace ของ consumer อยู่ดี · `dsh.*` มาจากไหน ถ้า platform ไม่รู้จัก `dsh`
* ❌ pattern ใน allowlist ทำให้ *"ตกลงตรงกันทั้งสามฝ่าย"* ตรวจยากขึ้นมาก

### B. นิยามให้ครบ + ต่อสายเพดานเชิงคุณสมบัติ + **ไม่ตรงเลย = reject ไม่ใช่ deny-all** ⭐

1. **`tools.allow` ที่หายไป = ไม่มีเพดานเชิงชื่อ** (เพดานมาจาก capability/authority) · **`[]` = ไม่อนุญาตเลย** — สองอย่างต่างกันและเขียนไว้ให้ชัด
2. **ต่อสาย**: tool ที่ `required_capabilities` ตัดกับ `deny_capabilities` ของฝ่ายใดก็ตาม → **ใช้ไม่ได้**
3. **`allow` ที่ไม่ตรงกับ tool ของ agent เลยสักตัว = profile ถูกใช้ผิด namespace → reject** ไม่ใช่ปล่อยให้กลายเป็น deny-all เงียบ ๆ

* ✅ ปิดทั้งด้าน fail-closed และ fail-open — ข้อ 3 ทำให้การใช้ผิด namespace **ดังขึ้น** แทนที่จะเงียบ
* ✅ ข้อ 2 ทำให้ profile ที่ platform เขียน **ใช้ได้กับ registry ที่ไม่เคยเห็น** โดยไม่ต้องรู้จักชื่อ tool
* ✅ **ไม่ต้องแก้ profile ทั้ง 6 ตัว** — มันยังเป็นเพดานที่ถูกต้องสำหรับ tenant ที่ใช้ namespace กลาง
* ✅ ใช้ของที่มีอยู่หมด — `required_capabilities` · `deny_capabilities` · `authority_map` ไม่มี field ใหม่สักตัว
* ❌ ข้อ 3 บังคับด้วย JSON Schema ไม่ได้ — ต้องพึ่ง implementation เหมือน guarantee อื่นเกือบทั้งหมด

### C. บอกว่า profile ที่ platform ตีพิมพ์เป็น **แม่แบบ** ต้อง specialize ก่อนใช้

* ✅ ไม่แตะ schema เลย
* ❌ ไม่แก้ด้าน fail-open — tenant ที่ specialize แล้วลืมแปลง `deny` ยังได้ profile ที่ไม่ปกป้องอะไร
* ❌ ย้ายภาระไปหา tenant ทั้งที่ปัญหาอยู่ที่สัญญาไม่ได้บอกว่าเพดานเชิงชื่อผูกกับ namespace

### D. บังคับให้ทุก consumer ขึ้นทะเบียน tool ด้วยชื่อกลาง

* ❌ **ยังไม่มีทะเบียน tool กลางอยู่จริง** (เหมือน capability catalog ที่ [#50](https://github.com/monthop-gmail/agent-platform/issues/50) พบ)
* ❌ ขัดกับที่ปฏิเสธ `channel-event/v1` ของ `botforge` ด้วยเหตุผลว่า *"platform ไม่ควรรู้รายละเอียดของ LINE"*

## Decision

**B** — นิยาม absent/empty ให้ครบ · ต่อสายเพดานเชิงคุณสมบัติ · และ `allow` ที่ไม่ตรงเลย = reject ไม่ใช่ deny-all

**Reason:** ปัญหาที่ #53 รายงาน (allow ได้ศูนย์) เห็นได้ทันทีเพราะมัน fail closed — **ด้านที่อันตรายกว่าคือ `deny` ที่ไม่ตรงแล้วเงียบ** ทำให้ *"profile นี้ห้าม merge"* กลายเป็นความเชื่อที่ไม่จริงโดยไม่มีอะไรบอก · ทางแก้จึงต้องทำให้การใช้ผิด namespace **ดังขึ้น** ไม่ใช่แค่ทำให้ allow กว้างขึ้น (ปฏิเสธ A ที่แก้เฉพาะด้านที่เห็นอยู่แล้ว) · และเพดานที่ platform เขียนได้จริงคือเพดานเชิงคุณสมบัติ ซึ่ง **มีอยู่แล้วทั้งสองข้าง แค่ไม่มีใครต่อสาย** — ไม่ต้องเพิ่ม field สักตัว · หลัก *"reject ไม่ใช่ coerce"* เป็นหลักเดียวกับที่ `consent/v1` ใช้กับ tenant ที่ไม่ตรง และที่ [ADR-0022](0022-agent-may-narrow-its-own-scope.md) ใช้กับ `required` ที่ตัดกับ `deny`

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### กฎที่เขียนลงสัญญา

```text
1. ไม่มี tools.allow      = ไม่มีเพดานเชิงชื่อ · เพดานมาจาก capability และ authority
   tools.allow: []        = ไม่อนุญาต tool ใดเลย
   — สองอย่างนี้ต่างกัน และไม่มีทางเขียนสิ่งเดียวกันได้สองแบบ

2. tool ที่ required_capabilities ตัดกับ deny_capabilities ของฝ่ายใดก็ตาม → ใช้ไม่ได้
   — เพดานเชิงคุณสมบัติที่ทำงานกับ registry ที่ platform ไม่เคยเห็น

3. tools.allow ที่ไม่ตรงกับ tool ของ agent เลยสักตัว = profile ถูกใช้ผิด namespace
   → reject การผูก ไม่ใช่ปล่อยให้กลายเป็น deny-all เงียบ ๆ

4. tools.deny และ require_human_for ที่เขียนด้วยชื่อ **ปกป้องเฉพาะ namespace ที่มันตั้งชื่อ**
   — การปกป้องที่พกพาได้ต้องเขียนด้วย capability หรือ action_risk
```

ข้อ 4 คือข้อที่ตอบด้าน fail-open โดยตรง · ไม่ได้ทำให้ deny เชิงชื่อทำงานข้าม namespace (ทำไม่ได้) แต่ทำให้**ไม่มีใครเข้าใจผิดว่ามันทำ**

### ไม่ bump major — `profile/v1` `v1.0.0` → `v1.1.0`

ไม่มี field ใหม่ · ไม่มี field เปลี่ยน type · `required` ไม่ขยับ · เป็นการเขียนความหมายที่ยังไม่เคยเขียนและต่อสายที่มีอยู่แล้ว

**ไม่ต้องแก้ profile ทั้ง 6 ตัว** — ยังเป็นเพดานที่ถูกต้องสำหรับ tenant ที่ใช้ namespace กลาง · สิ่งที่เปลี่ยนคือการเอาไปใช้กับ namespace อื่นจะถูกปฏิเสธแทนที่จะเงียบ

## Consequences

* `agent-builder-dsh-poc` **ไม่ต้องเปลี่ยนชื่อ tool ของตัวเอง** — ใช้ profile กลางโดยไม่มี `allow` หรือเขียน profile ของตัวเองก็ได้ · และถ้าเผลอใช้ profile ที่ไม่ตรง namespace จะได้ error ไม่ใช่ agent ที่ไม่มี tool
* **เพดานเชิงคุณสมบัติใช้ได้จริงเป็นครั้งแรก** — `required_capabilities` เคยถูกอ้างที่เดียวคือที่นิยามตัวเอง
* **drift check ตรวจข้อ 2–4 ไม่ได้** — เป็นกฎการประกอบข้ามไฟล์และข้าม runtime พิสูจน์ได้จากเทสของ consumer เท่านั้น ([ADR-0011](0011-conformance-automation.md))
* ยังไม่ปิด: **`ToolId` บังคับให้มีจุดอย่างน้อยหนึ่งจุด** — consumer ที่ตั้งชื่อคำเดียวจะ validate ไม่ผ่านตั้งแต่แรก · เป็นคำถามเรื่องรูปของชื่อ คนละเรื่องกับเพดาน จึงไม่ตัดสินในใบนี้
* ยังไม่ปิด: **ไม่มีทะเบียน tool กลางอยู่จริง** เหมือนที่ [#50](https://github.com/monthop-gmail/agent-platform/issues/50) พบว่าไม่มี capability catalog — ADR นี้ทำให้ไม่จำเป็นต้องมีเพื่อให้ profile ใช้งานได้ แต่ไม่ได้แปลว่าไม่ควรมี

## Sources

[issue #53](https://github.com/monthop-gmail/agent-platform/issues/53) · [`profiles/coding-agent/profile.yaml`](../profiles/coding-agent/profile.yaml) · `tool/v1` `action_risk` / `required_capabilities` · [ADR-0022](0022-agent-may-narrow-its-own-scope.md) กฎการรวมสามฝ่าย · [ADR-0012](0012-consent-contract.md) เหตุผลที่ platform ไม่ควรรู้รายละเอียดของโดเมน · `consent/v1` หลัก *reject ไม่ใช่ coerce*
