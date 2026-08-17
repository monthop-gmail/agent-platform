# ADR-0007: Multi-Tenancy Model

**Status:** Accepted (2026-08-17)
**Date:** 2026-08-17
**Blocking:** `contracts/identity/`, `contracts/policy/`, `contracts/event/`

## Context

มี tenant model **3 แบบที่ไม่ตรงกัน** ใน 3 เอกสาร และทุกอันบอกว่า "ต้องรองรับ multi-tenant ตั้งแต่วันแรก"

**[`backend-os §5`](../ref/enterprise-agent-backend-os-blueprint.md)** — 3 ชั้น มี Workspace:

```text
Organization → Users / Roles / Workspaces → Agents → {Tools, Knowledge, Memory, Files, Policies, Workflows}
```

**[`knowledge-platform §11`](../ref/enterprise-agent-knowledge-platform-blueprint.md)** — 2 ชั้น ไม่มี Workspace:

```text
Platform → Tenant → {Knowledge, Agents, Tools, Workflows, Policies}
```

**[`contract-review`](../ref/agent-platform-contract-review.md)** — 5 ชั้น มี Project:

```text
Organization → Project → Agent → User → Resource
```

และ [`knowledge-platform §7`](../ref/enterprise-agent-knowledge-platform-blueprint.md) ยังเพิ่ม **Department** เข้ามาอีกชั้นในสาย governance:

```text
User → Identity → Organization → Department → Role → Permission → Knowledge Access → Tool Access → Agent Policy
```

ส่วน [`backend-os §17`](../ref/enterprise-agent-backend-os-blueprint.md) ระบุว่าทุก request ต้องมี 4 id: `tenant_id` · `workspace_id` · `actor_id` · `agent_id` และ **ห้าม cross-tenant access โดย default**

ของจริงที่มีอยู่: `navi-ims` เป็น Odoo ซึ่งมี company/multi-company model ของตัวเองอยู่แล้ว — ต้องดูว่า map กับชั้นไหน

## Options

### A. Tenant → Workspace → Resource (แนะนำ)

```text
tenant_id       ขอบเขต isolation แข็ง — ห้ามข้ามเด็ดขาด (DB/index/storage แยกได้)
workspace_id    ขอบเขตงาน — agent, knowledge, tool, policy อยู่ใน workspace
actor_id        คนหรือระบบที่เป็นต้นเหตุ (principal)
agent_id        agent ที่ลงมือ
```

* `Organization` = คำเรียกทางธุรกิจของ `tenant` (alias ไม่ใช่ชั้นแยก)
* `Project` / `Department` = **attribute หรือ label ของ workspace** ไม่ใช่ชั้นใหม่ใน id chain
* ✅ ตรงกับ 4 required ids ที่ backend-os §17 บังคับอยู่แล้ว — ไม่ต้องแก้ blueprint
* ✅ 2 ชั้นพอสำหรับ isolation จริง (tenant = boundary, workspace = grouping) ชั้นที่ 3+ ทำเป็น metadata ได้
* ✅ Odoo company map เป็น `tenant` ตรง ๆ
* ❌ องค์กรที่มีลำดับชั้นลึก (กองทัพ/มหาวิทยาลัย) ต้อง represent ด้วย label ไม่ใช่ tree จริง — ยอมรับได้ในเฟสแรก

### B. Organization → Project → Workspace → Resource (4 ชั้น)

* ✅ ตรงกับ contract-review และรองรับองค์กรลำดับชั้นลึก
* ❌ ทุก query ต้องพก 4 id — ต้นทาง `backend-os §17` มี 4 field อยู่แล้วแต่คนละชุด → ต้องแก้ทุก blueprint
* ❌ ยิ่งชั้นเยอะ policy evaluation ยิ่งซับซ้อน ตอนที่ยังไม่มี requirement จริงมายืนยัน

### C. Tenant → Resource (แบน ไม่มี workspace)

ตาม knowledge-platform §11

* ✅ ง่ายสุด
* ❌ ไม่มีที่ให้แบ่งงาน/ทีมภายใน tenant เดียวกัน → ทีมหนึ่งเห็น knowledge อีกทีมทั้งหมด
* ❌ ขัด backend-os §5 และ §17 ที่ workspace เป็นแกนกลาง

## Decision

**A** — `Tenant → Workspace → Resource` · required ids ทุก request คือ `tenant_id` `workspace_id` `actor_id` `agent_id` · **deny cross-tenant by default**

**Reason:** ตรงกับ 4 required ids ที่ `backend-os §17` บังคับอยู่แล้วจึงไม่ต้องแก้ blueprint · 2 ชั้นพอสำหรับ isolation จริง (tenant = boundary แข็ง, workspace = grouping) ส่วน `Organization` เป็น alias ของ tenant และ `Project`/`Department` เป็น label ไม่ใช่ชั้น id · Odoo company map เป็น tenant ได้ตรง ๆ · ปฏิเสธ B เพราะเพิ่มชั้นโดยยังไม่มี requirement จริงมายืนยัน และทำให้ policy evaluation ซับซ้อนขึ้น ปฏิเสธ C เพราะไม่มีที่แบ่งงานภายใน tenant เดียวกัน

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

`tenant_id` เป็น **required ทุก contract ไม่มีข้อยกเว้น** และ isolation ต้องลงลึกถึง DB / index / storage layer

## Consequences ถ้าเลือก A

* ทุก contract ต้องมี `tenant_id` เป็น **required** ไม่มีข้อยกเว้น
* `workspace_id` required สำหรับ execution/knowledge/tool · optional สำหรับ event ระดับ tenant
* `contracts/event/` ต้องเพิ่ม `tenant_id` เข้าไป — `devfactory-core` RFC-0003 มีแค่ `event_id` `job_id` `event_type` `timestamp` `source` ยังไม่มี tenant ([extraction §3](../architecture/devfactory-core-rfc-extraction.md))
* ต้องประกาศกฎ **deny cross-tenant by default** ใน `contracts/policy/` และให้ isolation ลงลึกถึง DB/index/storage ตาม knowledge-platform §11
* `Department` / `Project` ที่ blueprint พูดถึงกลายเป็น label — ต้องเขียนไว้ในตารางศัพท์ที่เลิกใช้เพื่อไม่ให้ใครสร้างเป็นชั้น id ใหม่
* Zero-Trust Knowledge Access chain ของ knowledge-platform §10 ต้อง rewrite ให้อยู่บน 4 id นี้

## Sources

[`../ref/enterprise-agent-backend-os-blueprint.md`](../ref/enterprise-agent-backend-os-blueprint.md) §5, §17 · [`../ref/enterprise-agent-knowledge-platform-blueprint.md`](../ref/enterprise-agent-knowledge-platform-blueprint.md) §7, §10, §11 · [`../ref/agent-platform-contract-review.md`](../ref/agent-platform-contract-review.md) · [`../ref/existing-repos.md`](../ref/existing-repos.md)
