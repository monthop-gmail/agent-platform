# Consumer Registry

ทะเบียน repo ที่ consume contract ของ `agent-platform` — รวมจาก `platform-contract.yaml` ของแต่ละ repo ตาม [ADR-0006](../decisions/0006-contract-versioning.md)

ตารางนี้ตอบ 2 คำถามที่ตอบไม่ได้ถ้าไม่มีทะเบียน:

```text
ใครยังไม่ conform       → ต้องตามใครก่อนปล่อย contract version ใหม่
vN ยังมีใคร pin อยู่ไหม  → ปิด vN ได้หรือยัง
```

## สถานะปัจจุบัน — 2026-08-18

> ✅ **มี consumer ที่ conform จริง 2 ราย** — [`care-agent-platform`](https://github.com/monthop-gmail/care-agent-platform) และ [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) ครบทั้ง 3 ข้อของ [ADR-0006](../decisions/0006-contract-versioning.md) (manifest · conformance test ใน CI ที่ validate payload จริง · release gate)
> ส่วน `devfactory-core` มี `platform-contract.yaml` แล้วแต่ยังไม่มี code จึงไม่มี payload ให้ validate — สถานะยังเป็น `unknown`
> `—` หมายถึงยังไม่ได้ pin อะไร

| Repo | Manifest | Status | Contracts ที่ pin | last_verified | หมายเหตุ |
| --- | --- | --- | --- | --- | --- |
| [`care-agent-platform`](https://github.com/monthop-gmail/care-agent-platform) | ✅ [`platform-contract.yaml`](https://github.com/monthop-gmail/care-agent-platform/blob/main/platform-contract.yaml) | `passing` | `identity/v1` `event/v1` `policy/v1` `capability/v1` `error/v1` `consent/v1` | 2026-08-19 | **consumer ตัวแรกที่ conform จริง** — Python/FastAPI บน pstack · [`payload_check.py`](https://github.com/monthop-gmail/care-agent-platform/blob/main/conformance/payload_check.py) รัน scenario จริงแล้ว validate audit event ที่ระบบผลิตออกมา (58 event/รอบ) กับ schema ที่ commit ที่ pin ไว้ · ทำงานใน CI ทุก PR ทั้งบน sqlite และ Postgres · ช่องว่างที่เคยเจอ (#14 #15) ปิดครบแล้ว — ใช้ `subject_type: record` และ conform `consent/v1` ตั้งแต่ `5977dd9` |
| [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) | ✅ [`platform-contract.yaml`](https://github.com/monthop-gmail/devfactory-core/blob/main/platform-contract.yaml) | `passing` | `identity/v1` `execution/v1` `policy/v1` `error/v1` `approval/v1` `event/v1` | 2026-08-18 | **consumer ที่เป็นต้นทางของ `approval` และ `event` ด้วย** — Python ไม่มี runtime dependency · [`conformance/payload_check.py`](https://github.com/monthop-gmail/devfactory-core/blob/main/conformance/payload_check.py) รัน 6 job ข้าม 2 tenant ผ่าน job state machine จริง แล้ว validate audit event ที่ผลิตออกมา (37 event/รอบ) กับ schema ที่ commit ที่ pin ไว้ (`72635883`) พร้อมตรวจ guarantee ของ `event/v1` อีก 8 ข้อที่ JSON Schema ตรวจไม่ได้ · ทำงานใน CI ทุก PR บน Python 3.11/3.12/3.13 · ช่องว่างที่เจอ: [#17](https://github.com/monthop-gmail/agent-platform/issues/17) · authority ตาม [RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) |
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
| `identity` | `care-agent-platform` ✅ passing · `devfactory-core` ✅ passing | — | ไม่มี v2 |
| `execution` | `devfactory-core` ✅ passing | — | ไม่มี v2 |
| `policy` | `care-agent-platform` ✅ passing · `devfactory-core` ✅ passing | — | ไม่มี v2 |
| `error` | `care-agent-platform` ✅ passing · `devfactory-core` ✅ passing | — | ไม่มี v2 |
| `approval` 🔗 | `devfactory-core` ✅ passing | — | ไม่มี v2 |
| `event` 🔗 | `care-agent-platform` ✅ passing · `devfactory-core` ✅ passing | — | ไม่มี v2 |
| `capability` | `care-agent-platform` ✅ passing | — | ไม่มี v2 |
| `consent` | `care-agent-platform` ✅ passing | — | ไม่มี v2 |
| `agent` `provider` `model` | *(ยังไม่มีใคร)* | — | ไม่มี v2 |
| `tool` `mcp` `artifact` `profile` | *(ยังไม่มีใคร)* | — | ไม่มี v2 |

⚠️ **declared** = ประกาศ pin ใน `platform-contract.yaml` แล้ว แต่ยังไม่ผ่าน conformance (`status: unknown`)
declared ยังไม่ทำให้เป็น consumer ตาม ADR-0006 — **แต่มีผลกับการตัดสินใจปิด version** เพราะมี repo ที่พึ่งพา v1 นั้นอยู่จริงแล้ว

ตอนนี้ไม่มีแถวไหนเป็น `declared` แล้ว — เก็บคำอธิบายไว้เพราะยังเป็นสถานะที่ใช้ได้

🔗 **derived** = semantics เป็นของ `devfactory-core` ([ADR-0006 C2](../decisions/0006-contract-versioning.md)) · pin ปัจจุบัน `semantics_version: "1.1"` ตรงกับต้นทาง

**กฎ:** vN ที่ยังมี consumer pin อยู่ **ห้ามปิด** ไม่ว่าครบกำหนด 90 วันหรือไม่

## ผลการนำร่อง — `devfactory-core`

ทดสอบ contract v1 กับ repo จริงตัวแรกเมื่อ 2026-08-17 — ผลเต็มอยู่ที่ [`consumer-devfactory-core.md`](consumer-devfactory-core.md)

**สรุป: contract ไม่ต้องแก้** ทุกช่องว่างที่เจออยู่ฝั่ง consumer ไม่ใช่ฝั่ง contract

`devfactory-core` ตอบครบทั้ง 6 ข้อแล้วเมื่อ 2026-08-18 — [issue #8](https://github.com/monthop-gmail/devfactory-core/issues/8) · [PR #10](https://github.com/monthop-gmail/devfactory-core/pull/10)

| เจอ | ระดับ | ปิดด้วย |
| --- | --- | --- |
| ไม่มี `tenant_id` ที่ไหนเลย ทั้งที่ ADR-0007 บังคับ | 🔴 high | RFC-0006 — ใช้ `identity/v1` ตรง ๆ · `tenant_id` required บน job/decision/event · isolation ระดับ storage · single-tenant ใช้ `default` |
| RFC-0001 `FAILED` terminal แต่ execution retry ได้ — job-level retry ยังไม่มีคำตอบ | 🟠 medium | RFC-0007 — `FAILED` ยัง terminal · recovery = job ใหม่ที่มี `supersedes_job_id` |
| RFC-0001 ไม่มี `cancelled` / `timed_out` | 🟠 medium | RFC-0007 — เพิ่มเป็น terminal ระดับ job |
| execution ที่รออนุมัติกลางคัน มองไม่เห็นจากระดับ job | 🟠 medium | RFC-0007 — state `AWAITING_APPROVAL` + field `awaiting_from` |
| RFC-0003 บังคับ `job_id` — เข้ากันได้ทางเดียว | 🟡 low | RFC-0008 — `job_id` optional · subject required · ห้ามสร้าง `job_id` ปลอม |
| `packages/proxy` = outbound provider access → ชนกับชื่อ `model-gateway` | 🟡 low | RFC-0005 — เปลี่ยนชื่อเป็น `packages/provider-proxy` + `apps/control-api` · internal ทั้งคู่ |

⚠️ **ยังไม่ใช่ conformance จริง** — เป็น *document alignment* เพราะ `devfactory-core` ไม่มี code ให้ validate · ถ้าต้องการ conformance ที่พิสูจน์ด้วย payload จริง consumer ที่มี code อยู่แล้วคือ `navi-ims`

### `approval/` และ `event/` ไม่ติด external-authority-pending แล้ว

[RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) ตัดสินเรื่อง ownership ที่ ADR-0006 ค้างไว้ โดย**แยก semantics ออกจาก schema** แทนการยกทั้งก้อน:

* **semantics** (decision/event vocabulary + guarantees) อยู่ที่ `devfactory-core`
* **canonical wire schema** อยู่ที่ `agent-platform` — เพิ่ม field ระดับ platform (`tenant_id` `correlation_id` `policy_id` `expires_at` `action_risk` …) ได้ผ่าน ADR ที่นี่อย่างเดียว ไม่ต้องรอ RFC

ส่วน semantics อยู่ในรูปที่เครื่องอ่านได้ที่ [`contract-semantics.yaml`](https://github.com/monthop-gmail/devfactory-core/blob/main/contract-semantics.yaml) — มี `frozen` block ต่อ contract, `platform_may_add_freely`, และ template ของ `derived_from` ที่ ADR-0006 ต้องการ · ตรวจ drift ด้วย `semantics_version` ไม่ใช่ commit SHA ของไฟล์ RFC

## วิธีขึ้นทะเบียน

1. เพิ่ม `platform-contract.yaml` ที่ root ของ repo ([รูปแบบใน ADR-0006](../decisions/0006-contract-versioning.md))
2. เพิ่ม conformance test ใน CI ที่ validate payload จริงกับ schema ที่ pin
3. ทำให้ test เป็นเงื่อนไขของ release
4. เปิด PR แก้ตารางด้านบน — platform ไม่ไปดึงเอง เพื่อให้มีจุดที่คนตรวจได้

## Maintenance

* รีวิวตารางนี้ทุกครั้งที่ปล่อย contract version ใหม่ และก่อนปิด vN ใด ๆ
* `unknown` ที่ค้างเกิน 1 major ควรถูกถามว่ายังเป็น consumer อยู่จริงหรือไม่ — ถ้าไม่ ให้ย้ายออกจากตาราง
