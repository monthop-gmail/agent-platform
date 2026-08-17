# ADR-0002: Core Repository Naming

**Status:** Accepted (2026-08-17)
**Date:** 2026-08-17
**Depends on:** ADR-0001
**Blocking:** ADR-0003, `architecture/module-mapping.md`

## Context

ชื่อของ core repo ปรากฏใน `ref/` **4 เวอร์ชัน** จาก 4 เอกสารที่เขียนต่างเวลากัน:

| ชื่อ | ที่มา | สถานะจริง |
| --- | --- | --- |
| **`agent-platform`** | [`ref/repo-naming-agent-platform.md`](../ref/repo-naming-agent-platform.md) | ✅ **สร้างแล้ว** — repo นี้ |
| `agent-backend-os` | [`ref/naming-convention-ecosystem.md`](../ref/naming-convention-ecosystem.md) — ลิสต์ "7 core repos" ไม่มี `agent-platform` เลย | ยังไม่มี |
| `enterprise-agent-backend` | [`ref/enterprise-agent-backend-os-blueprint.md`](../ref/enterprise-agent-backend-os-blueprint.md) §3 | ยังไม่มี |
| `enterprise-agent-knowledge-platform` | [`ref/enterprise-agent-knowledge-platform-blueprint.md`](../ref/enterprise-agent-knowledge-platform-blueprint.md) §13 | ยังไม่มี |

ปัญหาไม่ใช่แค่ "ชื่อไหนสวย" แต่คือ **สองอันหลังไม่ใช่ core repo ตัวเดียวกัน** — `enterprise-agent-backend` เป็น Cloudflare backend, `enterprise-agent-knowledge-platform` เป็น Python knowledge platform ทั้งสองอันเป็น *implementation* คนละก้อน ไม่ใช่ตัวเลือกของชื่อเดียวกัน

ส่วน `agent-backend-os` อยู่ในลิสต์ 7 core repos **และ** เป็น 1 ใน 10 module ของ repo นี้ (`backend-os/`) พร้อมกัน — ซ้อนกันเอง

## Options

### A. `agent-platform` = contract owner, `agent-backend-os` = implementation repo แยก (แนะนำ)

```text
agent-platform          contract / architecture / decisions   ← repo นี้
agent-backend-os        implementation ของ backend plane      ← repo ใหม่
enterprise-knowledge    implementation ของ knowledge plane
```

* ✅ ไม่ต้องเปลี่ยนชื่อ repo ที่สร้างแล้ว (ไม่มี link เสีย)
* ✅ `agent-platform` กว้างกว่า จึงครอบ contract ที่ใช้ทั้ง ecosystem ได้ ส่วน `agent-backend-os` แคบกว่าและตรงกับหน้าที่ implementation
* ✅ แก้การซ้อนกันของ `backend-os/` — มันกลายเป็น "เอกสารขอบเขตของ repo `agent-backend-os`"
* ❌ ลิสต์ "7 core repos" ในไฟล์ naming convention ต้องแก้เป็น 8 (เพิ่ม `agent-platform`)

### B. rename repo นี้เป็น `agent-backend-os`

* ✅ ตรงกับลิสต์ 7 core repos ที่ทีมอาจจำไปแล้ว
* ❌ ขัดกับเหตุผลใน `ref/repo-naming-agent-platform.md` ที่เลือก `agent-platform` เพราะ "กว้างกว่า ไม่ล็อกไว้แค่ backend"
* ❌ contract ไม่ใช่ backend — เอา contract ระดับ ecosystem ไปอยู่ใต้ชื่อ `backend-os` ทำให้ทีมเข้าใจผิดว่าเป็นเรื่อง backend
* ❌ link ที่ส่งทีมไปแล้วเสียหมด

### C. ใช้ `enterprise-agent-platform`

* ✅ ชัดเจนว่าเป็น enterprise scope
* ❌ ยาว และ `ref/repo-naming-agent-platform.md` พิจารณาแล้วให้ ⭐⭐⭐⭐ (แพ้ `agent-platform`)
* ❌ ต้อง rename เหมือน B

## Decision

**A** — `agent-platform` = contract owner · `agent-backend-os` = implementation repo แยก

**Reason:** ไม่ต้อง rename repo ที่สร้างแล้ว (link ที่ส่งทีมไปแล้วไม่เสีย) และแยก domain ของสอง repo ไม่ให้ชนกัน — contract ระดับ ecosystem ไม่ใช่เรื่อง backend จึงไม่ควรอยู่ใต้ชื่อ `backend-os` · แก้การซ้อนกันของ `backend-os/` ที่เป็นทั้ง core repo candidate และ module ในตัวเอง

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

ลิสต์ "7 core repos" ในไฟล์ naming convention ให้อ่านว่าเป็น **implementation repos** — `agent-platform` อยู่คนละชั้น ไม่นับรวม

## Consequences ถ้าเลือก A

* ต้องแก้ลิสต์ core repos ให้มี `agent-platform` เป็นตัวที่ 8 (หรือประกาศว่า 7 ตัวนั้นคือ "implementation repos" ซึ่งอ่านสมเหตุสมผลกว่า)
* `enterprise-agent-backend` และ `enterprise-agent-knowledge-platform` ถือเป็น **ชื่อที่เลิกใช้** — map เป็น `agent-backend-os` และ `enterprise-knowledge` ตามลำดับ
* `backend-os/` ใน repo นี้ต้องเขียนใน README ว่าเป็นเอกสารขอบเขตของ repo ไหน

## ตารางชื่อที่เลิกใช้ (ถ้าเลือก A)

| ชื่อในเอกสารเก่า | ใช้ชื่อนี้แทน |
| --- | --- |
| `enterprise-agent-backend` | `agent-backend-os` |
| `enterprise-agent-knowledge-platform` | `enterprise-knowledge` |
| `enterprise-rag` (repo แยก) | module ใน `enterprise-knowledge` — ตาม knowledge blueprint §"แต่ถ้าต้องการลดจำนวน repo" |
| `ai-agent-harness` / `agent-harness` | รอ ADR-0005 |
| `ai-agent-gateway` / `multi-agent-gateway` | รอ ADR-0003 |

## Sources

[`../ref/repo-naming-agent-platform.md`](../ref/repo-naming-agent-platform.md) · [`../ref/naming-convention-ecosystem.md`](../ref/naming-convention-ecosystem.md) · [`../ref/existing-repos.md`](../ref/existing-repos.md)
