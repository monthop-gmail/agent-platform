# Consumer Registry

ทะเบียน repo ที่ consume contract ของ `agent-platform` — รวมจาก `platform-contract.yaml` ของแต่ละ repo ตาม [ADR-0006](../decisions/0006-contract-versioning.md)

ตารางนี้ตอบ 2 คำถามที่ตอบไม่ได้ถ้าไม่มีทะเบียน:

```text
ใครยังไม่ conform       → ต้องตามใครก่อนปล่อย contract version ใหม่
vN ยังมีใคร pin อยู่ไหม  → ปิด vN ได้หรือยัง
```

## สถานะปัจจุบัน — 2026-09-03

> ✅ **มี consumer ที่ conform จริง 5 ราย** — [`care-agent-platform`](https://github.com/monthop-gmail/care-agent-platform) · [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) · [`ecosystem-intelligence`](https://github.com/monthop-gmail/ecosystem-intelligence) · [`botforge`](https://github.com/monthop-gmail/botforge) · [`agent-builder-dsh-poc`](https://github.com/monthop-gmail/agent-builder-dsh-poc) — ครบทั้ง 3 ข้อของ [ADR-0006](../decisions/0006-contract-versioning.md) (manifest · conformance test ใน CI ที่ validate payload จริง · release gate)
> `—` หมายถึงยังไม่ได้ pin อะไร

| Repo | Manifest | Status | Contracts ที่ pin | last_verified | หมายเหตุ |
| --- | --- | --- | --- | --- | --- |
| [`care-agent-platform`](https://github.com/monthop-gmail/care-agent-platform) | ✅ [`platform-contract.yaml`](https://github.com/monthop-gmail/care-agent-platform/blob/main/platform-contract.yaml) | `passing` | `identity/v1` `event/v1` `policy/v1` `capability/v1` `error/v1` `consent/v1` `approval/v1` `profile/v1` | 2026-09-11 | **consumer ตัวแรกที่ conform จริง** — Python/FastAPI บน pstack · [`payload_check.py`](https://github.com/monthop-gmail/care-agent-platform/blob/main/conformance/payload_check.py) รัน scenario จริงแล้ว validate audit event ที่ระบบผลิตออกมา (58 event/รอบ) กับ schema ที่ commit ที่ pin ไว้ · ทำงานใน CI ทุก PR ทั้งบน sqlite และ Postgres · ช่องว่างที่เคยเจอ (#14 #15) ปิดครบแล้ว — ใช้ `subject_type: record` และ conform `consent/v1` ตั้งแต่ `5977dd9` · pin `approval/v1` เพิ่มแล้ว (`ap_approval` — payload_check validate ใบอนุมัติที่เกิดจากคนกดจริงใน scenario) · **manifest โตเป็น 6 conformance check แล้ว** (`drift_check` · `payload_check` · `migration_check` · `db_role_check` · `profile_check` · `rls_check`) — ตรวจเมื่อ 2026-09-10 ด้วยการดึง `platform-contract.yaml` มาอ่านเอง ไม่ได้เชื่อรายงาน · `profile_check` ตรวจเพดานของ agent เทียบ [`profile/v1`](../contracts/profile/v1/) และ **3 ใน 6 ข้อเรียก `evaluate()` จริงแทนการเทียบสตริงใน YAML** เพราะไฟล์ที่ถูกอ่านผิดกับไฟล์ที่ไม่ถูกอ่านเลย ดูเหมือนกันทุกอย่างจากการอ่านไฟล์ · มี negative test สองทางตาม [ADR-0011](../decisions/0011-conformance-automation.md) · ที่มาคือเพดานของเขาเคยสะกดชื่อ capability ผิดจนเป็น no-op อยู่หนึ่งเดือน และเคยยกทับ `emergency.escalate` จนระบบจะรอคนสั่งก่อนเรียกคน ([ADR-0029](../decisions/0029-the-cost-of-not-acting.md)) · **pin `profile/v1` เพิ่มเป็นตัวที่ 8 แล้ว** หลัง agent-platform ทักว่าอ้างถึงโดยไม่ได้ pin — เขาตอบว่า check เดิมตรวจ *พฤติกรรม* ของเพดานเท่านั้น ไม่ได้ตรวจ *รูป* แล้วแก้ด้วยการปิดช่องจริง ไม่ใช่แก้ถ้อยคำ · `profile_check` ตอนนี้ validate `profiles/care-agent/profile.yaml` กับ schema ที่ pin ด้วย · **ผู้ผลิต `undoes` รายแรก** ([ADR-0029](../decisions/0029-the-cost-of-not-acting.md)) — `organization.membership.end` undoes `organization.membership.write` บังคับที่ `load_policy()` จน boot ไม่ผ่านถ้าทิศผิด · และรายงานสองกรณีที่ประกาศไม่ได้ ซึ่งกลายเป็นเส้นแบ่งในใบ · **pin ขึ้นถึง `943d496b` แล้ว** (จาก `6e97e085` · `pinned.yaml` ของเขาบังคับว่าอัปเกรด pin ต้องเป็น PR แยกเสมอ) — ทันทีที่รับ `profile/v1` `v1.1.0` มาบังคับจริง **กฎ namespace จับบั๊กได้สองตัวที่ไม่มี validator ไหนเคยเห็น** คือยุบ "ไม่มี `allow`" กับ "`allow` ว่าง" เป็นค่าเดียวจนกลายเป็น deny-all เงียบ และ `allow` ที่ไม่ตรง namespace ที่เคยเงียบ ([ADR-0026](../decisions/0026-tool-identity-ceiling-is-namespace-bound.md)) · ประกาศ `text_fields` + `cutover` ใน manifest ตามร่าง RFC-0013 และ **`payload_check` อ่าน `text_fields` จากใบโดยตรง** ไม่ถือรายการของตัวเอง · ตรวจเมื่อ 2026-09-11 ด้วยการดึง `platform-contract.yaml` กับ `conformance/pinned.yaml` มาอ่านเอง |
| [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) | ✅ [`platform-contract.yaml`](https://github.com/monthop-gmail/devfactory-core/blob/main/platform-contract.yaml) | `passing` | `identity/v1` `execution/v1` `policy/v1` `error/v1` `approval/v1` `event/v1` | 2026-09-22 | **consumer ที่เป็นต้นทางของ `approval` และ `event` ด้วย** — authority ตาม [RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) · Python ไม่มี runtime dependency · [`conformance/payload_check.py`](https://github.com/monthop-gmail/devfactory-core/blob/main/conformance/payload_check.py) เดิน job state machine จริงแล้ว validate audit event ที่ผลิตออกมากับ schema ที่ commit ที่ pin ไว้ พร้อมตรวจ guarantee ของ `event/v1` ที่ JSON Schema ตรวจไม่ได้ · ทำงานใน CI ทุก PR · **เขาเป็นคนสร้าง `carried_check` — เช็คว่าสัญญาที่ derive ไปแล้วพกข้อผูกมัดที่ต้นทาง freeze ไว้มาจริงไหม** ซึ่งเป็นเกตที่ไม่มีใครมีมาก่อนและเป็นตัวที่จับได้ว่า `event/v1` `v1.7.1` ประกาศ `semantics_version` `1.3` โดยไม่ได้พกกฎมา ([#74](https://github.com/monthop-gmail/agent-platform/issues/74) · [ADR-0034](../decisions/0034-semantics-1-5-leaf-declaration.md)) · 🔢 **ตัวเลขที่เปลี่ยนทุกรอบ — pin · จำนวน event · ผลรัน — อ่านจากใบของเขา ไม่ทำสำเนาไว้ที่นี่** ([#78](https://github.com/monthop-gmail/agent-platform/issues/78)) |
| [`ecosystem-intelligence`](https://github.com/monthop-gmail/ecosystem-intelligence) | ✅ [`platform-contract.yaml`](https://github.com/monthop-gmail/ecosystem-intelligence/blob/main/platform-contract.yaml) | `passing` | `event/v1` `identity/v1` | 2026-09-22 | **ผู้ผลิต event ไม่ใช่ผู้บริโภค — รายแรกของทะเบียน** · ปล่อย `ADVISORY_ISSUED` และ `ECOSYSTEM_DRIFT_DETECTED` (`subject_type: record` + `metadata.record_type`) · [`payload_check.py`](https://github.com/monthop-gmail/ecosystem-intelligence/blob/main/conformance/payload_check.py) รัน advisor และ guardian กับ ecosystem จริงแล้ว validate event ที่ผลิตออกมากับ schema ที่ vendor ไว้จาก commit ที่ pin · **ไม่มี fixture ที่เขียนขึ้นเพื่อให้ผ่าน** · CI job `conformance` รันทุก PR · **conform เพราะฝั่งที่ผลิต payload ผิดคือฝั่งที่ทำให้ audit log ของคนอื่นพัง** ([#40](https://github.com/monthop-gmail/agent-platform/issues/40)) · 📣 **ประกาศ `text_fields` ตาม RFC-0013 ครบก่อนที่ใครจะแจ้ง** — เห็นว่า `semantics_version` ขยับแล้วไปทำเอง และเพิ่มแกน `written_by` แยก `human` กับ `system` ซึ่งเป็นแกนที่ RFC บอกเองว่า schema แยกไม่ได้ · 📣 **ประกาศ `text_fields` ตาม RFC-0013 ครบก่อนที่ใครจะแจ้ง** และ **re-pin ขึ้น semantics `1.5` เองหลังได้รับแจ้งตาม ADR-0006** ([#27 ของเขา](https://github.com/monthop-gmail/ecosystem-intelligence/issues/27)) · 🔢 ตัวเลขที่เปลี่ยนทุกรอบอ่านจากใบของเขา ไม่ทำสำเนาไว้ที่นี่ |
| [`botforge`](https://github.com/monthop-gmail/botforge) | ✅ [`platform-contract.yaml`](https://github.com/monthop-gmail/botforge/blob/v2/platform-contract.yaml) | `passing` | `error/v1` `event/v1` | 2026-09-22 | **manifest อยู่บน branch `v2` ไม่ใช่ `main`** — `main` คือ V1 ที่ freeze ไว้ที่ tag `v1-final` มี bot 14 ตัว deploy อยู่และรับเฉพาะ security fix · ทะเบียนอ่าน ref จากลิงก์ในแถวนี้ ([#44](https://github.com/monthop-gmail/agent-platform/pull/44)) · **ผู้ผลิต event** เหมือน `ecosystem-intelligence` — ปล่อย audit event ทุกจังหวะที่ state ของ execution เปลี่ยน (V1 ไม่มีบันทึกอะไรเลย) · [`payload_check.py`](https://github.com/monthop-gmail/botforge/blob/v2/conformance/payload_check.py) เดิน scenario LINE webhook เต็มรอบผ่าน `@botforge/core` จริงแล้ว validate `error/v1` 15 ใบ + `channel-event/v1` (allOf `event/v1`) 17 ใบ/รอบ · ตรวจเพิ่มว่าห้ามมี credential · `reply_token` · chain-of-thought · `job_id` ปลอม · release gate: ruleset ทั้ง `main` และ `v2` `bypass_actors: 0` พร้อม required check `conformance — ADR-0006` · `channel-event/v1` เป็น extension ของ repo ตัวเอง **ไม่ได้ขอให้ platform รับไปดูแล** — เจ้าของประเมินเองแล้วว่าตกเกณฑ์ข้อ 2 และ 4 ([#43](https://github.com/monthop-gmail/agent-platform/issues/43)) · 📣 **ประกาศ `text_fields` 4 leaf + ตัด `actor.display_name` ที่จุด emit ก่อนเขียนใบจริงใบแรก** (`cutover.outstanding: ไม่มี` — ยังไม่เคยมี audit event ของ V2 ถูกเขียนในของจริงเลยสักใบ) · **เป็นผู้ผลิตรายแรกที่ปิดช่องนี้ก่อนจ่ายราคา** ต่างจากรายก่อนหน้าที่ชื่อคนค้างอยู่ในใบเก่าทุกใบแล้วลบไม่ได้ · ที่มาของกฎ *การประกาศแบบ wildcard กลืน ratchet ของตัวเอง* ใน `event/v1` `platform_rules` ([botforge#31](https://github.com/monthop-gmail/botforge/issues/31) · [ADR-0034](../decisions/0034-semantics-1-5-leaf-declaration.md)) |
| [`agent-builder-dsh-poc`](https://github.com/monthop-gmail/agent-builder-dsh-poc) | ✅ [`platform-contract.yaml`](https://github.com/monthop-gmail/agent-builder-dsh-poc/blob/main/platform-contract.yaml) | `passing` | `agent/v1` `tool/v1` `capability/v1` `profile/v1` `execution/v1` `identity/v1` | 2026-09-03 | **consumer รายแรกของ `capability/v1` ที่ใช้ taxonomy เป็นเพดานจริง และรายแรกที่ pin `profile/v1`** — TypeScript · [`conformance/payload-check.ts`](https://github.com/monthop-gmail/agent-builder-dsh-poc/blob/main/conformance/payload-check.ts) รัน `openai-compatible` runtime จริงกับ stub ที่ถูกบังคับให้ตอบ 503 แล้ว validate execution record ที่เกิดจากการย้าย provider จริง (ไม่มี fixture ที่เขียนขึ้นเพื่อให้ผ่าน) · ตรวจสองทาง — run ที่ไม่ย้ายต้อง **ไม่มี** `provider_switches` เลยตาม `minItems: 1` · เทียบ `canonical_scope` กับต้นทางทุกรอบ ([ADR-0024](../decisions/0024-tool-calling-and-canonical-scope.md)) · CI job `conformance` รันทุก PR · **pin `agent/v1` และ `tool/v1` เพิ่มแล้ว** หลัง [#59](https://github.com/monthop-gmail/agent-platform/issues/59) — map ชื่อภายในเป็น `ToolId` ที่ขอบเขตเดียว (`builder/tool-ids.ts`) · **`agent/v1alpha2` ไม่ต้อง bump** เพราะไม่มีอะไรที่ผู้ใช้เขียนเปลี่ยน ข้อสันนิษฐานเดิมว่าเป็น breaking จึงผิด · เขา probe MCP จริงให้ platform ด้วย ([ADR-0027](../decisions/0027-toolid-transformation-must-be-deterministic.md)) และ **ไม่ pin `model/v1`** เพราะทำตาม `platform_rules` ครบแล้วแต่ไม่มี payload ให้ validate · ที่มาของ [#46](https://github.com/monthop-gmail/agent-platform/issues/46) [#47](https://github.com/monthop-gmail/agent-platform/issues/47) [#50](https://github.com/monthop-gmail/agent-platform/issues/50) [#52](https://github.com/monthop-gmail/agent-platform/issues/52) [#53](https://github.com/monthop-gmail/agent-platform/issues/53) [#56](https://github.com/monthop-gmail/agent-platform/issues/56) |
| [`navi-ims`](https://github.com/monthop-gmail/navi-ims) | ❌ ไม่มี | `unknown` | — | — | default branch `master` · Odoo 19 · เป็น system of record ไม่ใช่ agent consumer โดยตรง |
| [`ai-web-harness`](https://github.com/monthop-gmail/ai-web-harness) | ❌ ไม่มี | `unknown` | — | — | scaffold stage · อยู่ชั้น orchestration เหนือ gateway |
| [`enterprise-knowledge`](https://github.com/monthop-gmail/enterprise-knowledge) | ❌ ยังไม่มี | `unknown` | — | — | **repo เกิดแล้ว 2026-08-20** (แถวนี้เคยเขียนว่า "ยังไม่มี repo") · Knowledge Plane — hybrid RAG สองขั้น (pgvector + RRF + cross-encoder) หลัง contract `knowledge.search` · roadmap Phase 1–10 เปิดเป็น 22 issue · การ conform เป็นงานที่วางแผนไว้แล้วที่ [#17 ของเขา](https://github.com/monthop-gmail/enterprise-knowledge/issues/17) *"align knowledge.search with the agent-platform canonical contract"* · ยังต้องการ tool + policy (ACL-aware retrieval) เหมือนเดิม |
| `navi-security-agent` | — | ยังไม่มี repo | — | — | Phase 0 ต้องการ event + policy contract |
| `agent-backend-os` | — | ยังไม่มี repo | — | — | บ้านของ native runtime ตาม [ADR-0005 C2](../decisions/0005-agent-runtime-boundary.md) |
| `agent-fleet` | — | ยังไม่มี repo | — | — | ต้องการ execution + capability |
| `model-gateway` | — | ยังไม่มี repo | — | — | ต้องการ provider + capability |
| `farm-agent` | — | ยังไม่มี repo | — | — | ต้องการ agent + tool |
| `odoo-farm` | — | ยังไม่มี repo | — | — | ปรากฏใน README เดิมแต่ไม่เคยมีแถวในทะเบียน — ยังไม่ระบุ contract ที่ต้องการ ([#20](https://github.com/monthop-gmail/agent-platform/issues/20)) |

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
| `identity` | `care-agent-platform` ✅ passing · `devfactory-core` ✅ passing · `ecosystem-intelligence` ✅ passing · `agent-builder-dsh-poc` ✅ passing | — | ไม่มี v2 |
| `execution` | `devfactory-core` ✅ passing · `agent-builder-dsh-poc` ✅ passing | — | ไม่มี v2 |
| `policy` | `care-agent-platform` ✅ passing · `devfactory-core` ✅ passing | — | ไม่มี v2 |
| `error` | `care-agent-platform` ✅ passing · `devfactory-core` ✅ passing · `botforge` ✅ passing | — | ไม่มี v2 |
| `approval` 🔗 | `care-agent-platform` ✅ passing · `devfactory-core` ✅ passing | — | ไม่มี v2 |
| `event` 🔗 | `care-agent-platform` ✅ passing · `devfactory-core` ✅ passing · `ecosystem-intelligence` ✅ passing · `botforge` ✅ passing | — | ไม่มี v2 |
| `capability` | `care-agent-platform` ✅ passing · `agent-builder-dsh-poc` ✅ passing | — | ไม่มี v2 |
| `consent` | `care-agent-platform` ✅ passing | — | ไม่มี v2 |
| `profile` | `agent-builder-dsh-poc` ✅ passing · `care-agent-platform` ✅ passing | — | ไม่มี v2 |
| `agent` | `agent-builder-dsh-poc` ✅ passing | — | ไม่มี v2 |
| `provider` `model` | *(ยังไม่มีใคร)* | — | ไม่มี v2 |
| `tool` `mcp` `artifact` | *(ยังไม่มีใคร)* | — | ไม่มี v2 |

⚠️ **declared** = ประกาศ pin ใน `platform-contract.yaml` แล้ว แต่ยังไม่ผ่าน conformance (`status: unknown`)
declared ยังไม่ทำให้เป็น consumer ตาม ADR-0006 — **แต่มีผลกับการตัดสินใจปิด version** เพราะมี repo ที่พึ่งพา v1 นั้นอยู่จริงแล้ว

ตอนนี้ไม่มีแถวไหนเป็น `declared` แล้ว — เก็บคำอธิบายไว้เพราะยังเป็นสถานะที่ใช้ได้

🔗 **derived** = semantics เป็นของ `devfactory-core` ([ADR-0006 C2](../decisions/0006-contract-versioning.md)) · pin ปัจจุบัน `semantics_version: "1.5"` ตรงกับต้นทาง

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

> 📌 **บันทึกไว้ตามประวัติ** — ตอนนำร่อง (2026-08-17) `devfactory-core` ยังไม่มี code
> การตรวจรอบนั้นจึงเป็น *document alignment* ไม่ใช่ conformance จริง
> **ตั้งแต่ PR #13 และ #15 (2026-08-18) มี code แล้ว** และ conformance รัน payload จริงใน CI
> — สถานะปัจจุบันดูที่ตารางด้านบน ไม่ใช่ย่อหน้านี้

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

## กฎของข้อความในแถว — เพิ่ม 2026-09-20

**แถวห้ามทำสำเนาข้อเท็จจริงที่เจ้าของใบเป็นคนถือ** ([#78](https://github.com/monthop-gmail/agent-platform/issues/78))

`last_verified` · `pinned_contracts_commit` · จำนวน event ต่อรอบ · ผลรัน — เปลี่ยนทุกครั้งที่ consumer ทำงาน · สำเนาที่นี่จึงเก่าตั้งแต่วันถัดไป และไม่มีใครรู้

```text
ค่าที่ตรวจได้ทุกรอบ   →  อยู่ในคอลัมน์ · check [2] เทียบกับใบจริงให้
ค่าที่เปลี่ยนบ่อย      →  อยู่ในใบของ consumer ที่เดียว · แถวลิงก์ไป
คำตัดสินของ platform  →  อยู่ในแถว เพราะเป็นของเรา ไม่มีใครถืออีกที่
```

**ประโยคที่ไม่อ้างสิ่งที่ตัวเองตรวจไม่ได้ ก็เก่าไม่ได้** — ถ้อยคำของ `devfactory-core` ในใบที่รายงานเรื่องนี้

⚠️ ที่เขาเสนอไว้ว่าอย่าเพิ่ม check เพราะต้องพึ่งเน็ต **ใช้กับ `[5c]` จริง แต่ไม่ใช้กับ `[2]`** — `check_registry` ดึง `platform-contract.yaml` ของทุก consumer อยู่แล้วโดยนิยาม การเทียบ `last_verified` จึงไม่เสียคำขอเน็ตเพิ่มเลยสักครั้ง · เดิมอ่านค่านั้นมาถามข้อเดียวว่า *"passing แล้วมีวันไหม"* **ไม่เคยถามว่าวันที่เราเขียนไว้ตรงกับที่เขาเขียนไหม**

## Maintenance

* รีวิวตารางนี้ทุกครั้งที่ปล่อย contract version ใหม่ และก่อนปิด vN ใด ๆ
* `unknown` ที่ค้างเกิน 1 major ควรถูกถามว่ายังเป็น consumer อยู่จริงหรือไม่ — ถ้าไม่ ให้ย้ายออกจากตาราง
