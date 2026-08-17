# ADR-0004: Agent Provider vs Model Provider

**Status:** Proposed
**Date:** 2026-08-17
**Blocking:** `contracts/provider/`, `contracts/model/`, `profiles/` — **vocabulary gate**

## Context

สิ่งเดียวกันถูกเรียก **5 ชื่อ** ใน `ref/` และบางที่ใช้คำเดียวเรียกของ 2 ชั้นที่ต่างกัน:

| เอกสาร | เรียกชั้น "ผู้ให้ model" ว่า | เรียกชั้น "ผู้รัน agent" ว่า |
| --- | --- | --- |
| [`knowledge-platform §1, §5`](../ref/enterprise-agent-knowledge-platform-blueprint.md) | LLM Adapter | Agent Runtime Adapter |
| [`ai-subscription-oauth-gateway §6, §7`](../ref/ai-subscription-oauth-gateway-blueprint.md) | Provider Adapter (`providers/`) | Runtime Adapter (`runtimes/`) |
| [`distributed-gateway`](../ref/distributed-multi-agent-gateway-blueprint.md) | — (ไม่แตะ model) | `AgentAdapter` (`adapters/`) |
| [`naming-convention`](../ref/naming-convention-ecosystem.md) | `agent-model-router` | `agent-adapters` |
| [`contract-review`](../ref/agent-platform-contract-review.md) | `model-provider/` | `agent-provider/` |

ความสับสนที่แพงที่สุดคือคำว่า **"Claude"** — เป็นได้ทั้ง model (`claude-opus-5` ผ่าน Anthropic API) และ agent runtime (`claude-code` ที่รัน loop เอง มี tool ของตัวเอง) ซึ่งมี auth, capability และ billing คนละแบบ

[`ai-subscription-oauth-gateway`](../ref/ai-subscription-oauth-gateway-blueprint.md) พิสูจน์ว่าสองชั้นนี้แยกกันจริง: OAuth ของ ChatGPT subscription ใช้กับ Codex CLI ได้ แต่ไม่ใช่ `OPENAI_API_KEY` — *credential class คนละอัน สำหรับ entity คนละชั้น*

## Options

### A. 3 ชั้น ตาม contract-review + decisions-first plan (แนะนำ)

```text
Model Provider    ให้บริการ model inference
                  OpenAI · Anthropic · Google · Qwen · DeepSeek · xAI · MiniMax

Agent Provider    ให้บริการ agent execution (มี loop/tool/state ของตัวเอง)
                  Claude Code · Gemini CLI · Copilot CLI · Amazon Q · OpenCode · Codex CLI · Hermes · OpenClaw

Agent Platform    abstraction/orchestration ที่ทำให้สองชั้นบนอยู่ ecosystem เดียวกัน
```

กฎที่ตามมา:

* `contracts/model/` = inference contract (messages, streaming, token usage)
* `contracts/provider/` = ทั้งสองชั้นใช้ interface ร่วม แต่ประกาศ `provider_kind: model | agent`
* `agent-runtime` **ห้าม** import provider ตรง ๆ ต้องผ่าน adapter (ตาม contract-review)
* `Agent ≠ Model` — task schema ห้าม hard-code model list ([`distributed-gateway` Phase 3](../ref/distributed-multi-agent-gateway-blueprint.md))

* ✅ 2 ref ฉบับล่าสุดเห็นตรงกัน และเป็นเวอร์ชันที่ทีมรีวิวแล้ว
* ✅ อธิบายกรณี Nous Portal ได้ — เป็น *aggregator* ที่ให้ model หลายตัวผ่าน OAuth เดียว → `provider_kind: model` แต่ `is_aggregator: true`
* ❌ ต้องเลิกใช้คำ `LLM Adapter` / `Runtime Adapter` / `agent-adapters` / `agent-model-router` ในเอกสารใหม่

### B. 2 ชั้น — รวมเป็น `provider` เดียวแล้วแยกด้วย field

* ✅ interface เดียว โค้ดน้อยกว่า
* ❌ capability ต่างกันมาก (agent provider มี workspace/git/shell, model provider ไม่มี) → field optional เยอะจนไม่มีความหมาย
* ❌ ยังแก้ปัญหาคำว่า "Claude" กำกวมไม่ได้

### C. เก็บศัพท์เดิมของแต่ละ repo แล้วทำ mapping table

* ✅ ไม่ต้องแก้เอกสารเก่า
* ❌ contract กลางต้องเลือกคำใดคำหนึ่งอยู่ดี → เลื่อนปัญหาออกไป ไม่ได้แก้

## Decision

> _(รอเคาะ)_

## Consequences ถ้าเลือก A

* เพิ่ม glossary ใน `architecture/` และให้ ADR นี้เป็น authority ของสามคำนี้
* ตารางศัพท์ที่เลิกใช้:

| คำเดิม | ใช้แทน |
| --- | --- |
| LLM Adapter · Provider Adapter (เมื่อหมายถึง model) · `agent-model-router` | **Model Provider** (+ router เป็นหน้าที่ของ `model-gateway`) |
| Agent Runtime Adapter · Runtime Adapter · `agent-adapters` · `AgentAdapter` | **Agent Provider** |

* `ref/ai-subscription-oauth-gateway-blueprint.md` §6/§7 ที่แยก `providers/` กับ `runtimes/` ยังใช้ได้ — แค่เปลี่ยนชื่อเป็น `model-providers/` กับ `agent-providers/`
* `profiles/` แต่ละตัวต้องระบุ `agent-provider` ที่ใช้ (ตาม decisions-first plan Phase 4)

## Sources

[`../ref/agent-platform-contract-review.md`](../ref/agent-platform-contract-review.md) · [`../ref/agent-platform-decisions-first-plan.md`](../ref/agent-platform-decisions-first-plan.md) Phase 2 · [`../ref/ai-subscription-oauth-gateway-blueprint.md`](../ref/ai-subscription-oauth-gateway-blueprint.md) · [`../ref/enterprise-agent-knowledge-platform-blueprint.md`](../ref/enterprise-agent-knowledge-platform-blueprint.md) §5
