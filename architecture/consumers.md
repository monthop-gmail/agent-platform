# Consumer Registry

ทะเบียน repo ที่ consume contract ของ `agent-platform` — รวมจาก `platform-contract.yaml` ของแต่ละ repo ตาม [ADR-0006](../decisions/0006-contract-versioning.md)

ตารางนี้ตอบ 2 คำถามที่ตอบไม่ได้ถ้าไม่มีทะเบียน:

```text
ใครยังไม่ conform       → ต้องตามใครก่อนปล่อย contract version ใหม่
vN ยังมีใคร pin อยู่ไหม  → ปิด vN ได้หรือยัง
```

## สถานะปัจจุบัน — 2026-08-17

> ⚠️ **ยังไม่มี repo ไหนเป็น consumer** — [`contracts/` v1 เขียนแล้ว](../contracts) แต่ยังไม่มี repo ไหนประกาศ `platform-contract.yaml` และรัน conformance test ตาม [ADR-0006](../decisions/0006-contract-versioning.md)
> ตารางนี้จึงเป็นโครงที่รอเติม ไม่ใช่รายงานสถานะจริง — `—` หมายถึงยังไม่ได้ pin อะไร

| Repo | Manifest | Status | Contracts ที่ pin | last_verified | หมายเหตุ |
| --- | --- | --- | --- | --- | --- |
| [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) | 📝 ร่างแล้ว ยังไม่ push | `unknown` | *(ร่าง)* `identity/v1` `execution/v1` `policy/v1` `error/v1` | — | **consumer นำร่อง** — ยัง conform ไม่ได้เพราะ repo ยังไม่มี code จึงไม่มี payload ให้ validate · ผลวิเคราะห์: [`consumer-devfactory-core.md`](consumer-devfactory-core.md) |
| [`navi-ims`](https://github.com/monthop-gmail/navi-ims) | ❌ ไม่มี | `unknown` | — | — | default branch `master` · Odoo 19 · เป็น system of record ไม่ใช่ agent consumer โดยตรง |
| [`ai-web-harness`](https://github.com/monthop-gmail/ai-web-harness) | ❌ ไม่มี | `unknown` | — | — | scaffold stage · อยู่ชั้น orchestration เหนือ gateway |
| `navi-security-agent` | — | ยังไม่มี repo | — | — | Phase 0 ต้องการ event + policy contract |
| `enterprise-knowledge` | — | ยังไม่มี repo | — | — | ต้องการ tool + policy (ACL-aware retrieval) |
| `agent-backend-os` | — | ยังไม่มี repo | — | — | บ้านของ native runtime ตาม [ADR-0005 C2](../decisions/0005-agent-runtime-boundary.md) |
| `agent-fleet` | — | ยังไม่มี repo | — | — | ต้องการ execution + capability |
| `model-gateway` | — | ยังไม่มี repo | — | — | ต้องการ provider + capability |
| `farm-agent` | — | ยังไม่มี repo | — | — | ต้องการ agent + tool |

## วิธีอ่านคอลัมน์ Status

| ค่า | ความหมาย |
| --- | --- |
| `passing` | CI conformance ผ่าน และ `last_verified` ไม่เกิน 90 วัน |
| `failing` | test ไม่ผ่าน — **ห้ามปล่อย release** ตาม ADR-0006 |
| `unknown` | ไม่มี manifest, ไม่เคยรัน, หรือ `last_verified` เกิน 90 วัน |
| `waived` | ยกเว้นชั่วคราว ต้องมีวันหมดอายุและ issue/ADR อ้างอิง |

`passing` ที่ `last_verified` เกิน 90 วัน platform ถือเป็น `unknown` ทันที ไม่ว่าไฟล์เขียนว่าอะไร

## Version usage — ปิด vN ได้หรือยัง

ตารางนี้จะเติมได้เมื่อมี consumer จริง ใช้ตัดสินใจ deprecation ตาม [ADR-0006](../decisions/0006-contract-versioning.md)

| Contract | v1 pinned by | v2 pinned by | ปิด v1 ได้? |
| --- | --- | --- | --- |
| `identity` `agent` `capability` `provider` `model` | *(ยังไม่มีใคร)* | — | ไม่มี v2 |
| `tool` `mcp` `execution` `policy` `artifact` `error` `profile` | *(ยังไม่มีใคร)* | — | ไม่มี v2 |

v1 ทุกตัวยังไม่มี consumer pin — เมื่อมี repo แรกขึ้นทะเบียน ให้แตกเป็นบรรทัดต่อ contract

**กฎ:** vN ที่ยังมี consumer pin อยู่ **ห้ามปิด** ไม่ว่าครบกำหนด 90 วันหรือไม่

## ผลการนำร่อง — `devfactory-core`

ทดสอบ contract v1 กับ repo จริงตัวแรกเมื่อ 2026-08-17 — ผลเต็มอยู่ที่ [`consumer-devfactory-core.md`](consumer-devfactory-core.md)

**สรุป: contract ไม่ต้องแก้** ทุกช่องว่างที่เจออยู่ฝั่ง consumer ไม่ใช่ฝั่ง contract

| เจอ | ระดับ |
| --- | --- |
| ไม่มี `tenant_id` ที่ไหนเลย ทั้งที่ ADR-0007 บังคับ | 🔴 high — ต้องมี RFC ใหม่ที่ repo นั้น |
| RFC-0001 `FAILED` terminal แต่ execution retry ได้ — job-level retry ยังไม่มีคำตอบ | 🟠 medium |
| RFC-0001 ไม่มี `cancelled` / `timed_out` | 🟠 medium |
| execution ที่รออนุมัติกลางคัน มองไม่เห็นจากระดับ job | 🟠 medium |
| RFC-0003 บังคับ `job_id` — เข้ากันได้ทางเดียว | 🟡 low |
| `packages/proxy` = outbound provider access → ชนกับชื่อ `model-gateway` | 🟡 low |

⚠️ **ยังไม่ใช่ conformance จริง** — เป็น *document alignment* เพราะ `devfactory-core` ไม่มี code ให้ validate · ถ้าต้องการ conformance ที่พิสูจน์ด้วย payload จริง consumer ที่มี code อยู่แล้วคือ `navi-ims`

## วิธีขึ้นทะเบียน

1. เพิ่ม `platform-contract.yaml` ที่ root ของ repo ([รูปแบบใน ADR-0006](../decisions/0006-contract-versioning.md))
2. เพิ่ม conformance test ใน CI ที่ validate payload จริงกับ schema ที่ pin
3. ทำให้ test เป็นเงื่อนไขของ release
4. เปิด PR แก้ตารางด้านบน — platform ไม่ไปดึงเอง เพื่อให้มีจุดที่คนตรวจได้

## Maintenance

* รีวิวตารางนี้ทุกครั้งที่ปล่อย contract version ใหม่ และก่อนปิด vN ใด ๆ
* `unknown` ที่ค้างเกิน 1 major ควรถูกถามว่ายังเป็น consumer อยู่จริงหรือไม่ — ถ้าไม่ ให้ย้ายออกจากตาราง
