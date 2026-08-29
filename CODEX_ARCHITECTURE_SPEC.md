# EchoSphere Repository and Agora Voice-AI Architecture Specification

This document records the complete read-only repository analysis and implementation specification. At analysis time, the working tree was clean on `feature/agora-voice-ai`. The repository was not changed during that audit.

The central finding is that the repository currently contains a polished, session-state-driven Streamlit simulation. It does not contain a functioning voice pipeline, Agora integration, backend, API client, database, CRM integration, speech recognition, language detection, AI model, TTS engine, or real-time event transport. Labels such as IndicBERT-v2, ElevenLabs, DeepFilter, CRM persistence, gateway verification, and real-time ASR/NLU are display text only.

## A. Current repository architecture

```text
KNOTIC_HT/
├── app.py
├── requirements.txt
├── .gitignore
├── components/
│   ├── call_panel.py
│   ├── case.py
│   ├── conversation.py
│   ├── demo.py
│   ├── escalation.py
│   ├── header.py
│   └── intelligence.py
└── styles/
    └── main.css
```

There is no backend service, API layer, Agora client, JavaScript/TypeScript, Streamlit custom component, database, persistence adapter, tests, schema package, Docker configuration, `.env.example`, Streamlit secrets configuration, CI/CD configuration, authentication, logging, or telemetry configuration.

`app.py` configures Streamlit, loads CSS, initializes demo state, then renders the header, demo stepper, escalation block, and a three-column layout: call/audio/language controls on the left, conversation timeline in the center, and intelligence plus case management on the right.

`requirements.txt` contains only unpinned `streamlit` and `pandas`; pandas is unused.

## B. Current dashboard functionality

### Header

`components/header.py` displays the product name “AssistAI” (not EchoSphere), a hardcoded live indicator, supplied system status, session ID, and hardcoded 124 ms latency. It has no health check or latency measurement.

### Call panel

`components/call_panel.py` displays call status/duration, a hardcoded masked caller, Hindi + English mode, a decorative CSS waveform, speaker state, mute/end/transfer buttons, hardcoded signal/noise/clarity/filter metrics, and session-state Hindi/English percentages. Mute, end, and transfer mutate local labels/state only; no audio track or call is controlled.

### Conversation

`components/conversation.py` renders `conversation_history` items of type `message`, `event`, or `interruption`. Message roles are caller, AI, and human. Interruption latency and the “TTS: ElevenLabs” label are hardcoded. External text is interpolated into `unsafe_allow_html=True`, which is an injection risk once data becomes live.

### Intelligence

`components/intelligence.py` displays intent, entities, overall confidence, an explanation, next question, and static safety claims. “Ask Caller” appends a bubble and changes a label; it does not invoke speech or an agent. IndicBERT-v2 is not integrated.

### Escalation

`components/escalation.py` renders a hardcoded summary and supports local cancel/confirm actions. Confirming locally declares transfer and appends hardcoded human messages. There is no queue, Agora transfer, context persistence, CRM, or real human.

### Existing Case Card

`components/case.py` is the existing ticket presentation. Only `ticket_id`, `ticket_status`, and `assigned_human` are read from session state (with defaults). Priority, category, summary, phone, language, order, confidence history, timestamps, and CRM claims are hardcoded. There is no canonical Case Card JSON or durable storage.

### Demo

`components/demo.py` defines 17 pre-authored stages simulating connection, Hindi/Hinglish recognition, noise handling, classification, extraction, questions, uncertainty, confidence decline, escalation, and handoff. “Play Auto Demo” advances one step per click; it is not timed playback.

## C. Existing data flow and state

```text
DEMO_STEPS → apply_demo_step() → st.session_state → render_*() → HTML/CSS
```

There is no inbound source except buttons. Current keys include `demo_step`, `speaker_state`, `call_status`, `lang_hi`, `lang_en`, `overall_confidence`, `confidence_explanation`, `intent`, `entities`, `conversation_history`, `next_question`, `show_escalation_modal`, `is_muted`, and `show_case_modal`. `session_id`, `call_duration`, `assigned_human`, `ticket_id`, and `ticket_status` have fallback values but no real producers. Session state is browser-session UI state, not durable case storage.

## D. Proposed voice-AI architecture

```text
Caller browser
  ├── Streamlit dashboard
  └── Embedded/custom Agora Web client
            │ RTC audio
            ▼
       Agora channel
            ▼
Agora Conversational AI agent
  ├── streaming STT and turn handling
  ├── custom EchoSphere LLM endpoint
  ├── streaming TTS
  └── interruption/noise handling
            ▼
EchoSphere backend
  ├── session orchestration and dialogue policy
  ├── extraction, confirmation, confidence
  ├── canonical Case Card and event store
  ├── problem/expertise classification and routing
  ├── handoff orchestration and persistence
  └── WebSocket/SSE gateway
            ▼
Streamlit state adapter and existing components
```

Agora owns RTC transport/audio and conversational timing. The EchoSphere backend owns reasoning, essential-field policy, confirmation, confidence, classification, routing, persistence, events, and handoff. Do not run the long-lived agent/audio loop inside Streamlit because Streamlit reruns are not an authoritative real-time process.

## E. Exact integration points

- `app.py`: add demo/live mode, backend client, snapshot/event application, and embedded Agora component while preserving layout. Never hold Agora secrets or call privileged Agora APIs directly.
- `call_panel.py`: bind live call/audio/language state; make mute/end/transfer issue real local-track actions or backend commands.
- `conversation.py`: consume typed partial/final/corrected transcript and interruption events; escape all external content.
- `intelligence.py`: project classification, fields, confidence, uncertainty, and next action; “Ask” sends a backend command.
- `case.py`: become the canonical Live Case Card projection; remove hardcoded case/CRM claims.
- `escalation.py`: display backend handoff data and issue approve/cancel commands; never declare completion locally.
- `demo.py`: initially remain unchanged as deterministic fallback/presentation mode, never a live data source.
- `styles/main.css`: preserve design; add only semantic-state styling if needed.
- `header.py`: preserve structure; later accept real health/latency.

## F. Recommended new files/modules

```text
backend/
├── main.py, config.py, dependencies.py
├── api/{sessions,commands,cases,events,webhooks}.py
├── agora/{client,token_service,agent_manager,event_mapper}.py
├── voice/{pipeline,turn_manager,language,prompts}.py
├── case_management/{models,reducer,extraction,confidence,classification,routing,handoff}.py
├── persistence/{repository,memory_repository}.py
└── tests/
dashboard/{api_client,event_client,state_adapter,models}.py
frontend/agora_component/src/{AgoraVoiceClient,index}.tsx
shared/{contracts,event_types}.py
.env.example
Dockerfile(s)
docker-compose.yml
```

A Streamlit custom component/embedded browser client is required for a proper Agora Web SDK microphone and audio lifecycle.

## G. Required APIs

All mutations accept an idempotency key.

### Session creation

`POST /api/v1/sessions`

```json
{"caller":{"external_id":null,"phone_masked":"+91 98765-XXXXX"},"locale_hints":["hi-IN","en-IN"],"client":{"type":"streamlit_web","timezone":"Asia/Calcutta"}}
```

```json
{"session_id":"ses_01...","case_id":"case_01...","channel_name":"echo_case_01...","rtc_uid":10421,"rtc_token":"short-lived-token","expires_at":"2026-08-29T12:30:00Z","event_stream_url":"/api/v1/sessions/ses_01/events","revision":0}
```

Required endpoints:

```text
POST /api/v1/sessions
POST /api/v1/sessions/{id}/agent:start
POST /api/v1/sessions/{id}/agent:stop
POST /api/v1/sessions/{id}/end
POST /api/v1/sessions/{id}/token:refresh
POST /api/v1/sessions/{id}/commands
GET  /api/v1/sessions/{id}/case
GET  /api/v1/sessions/{id}/transcript
GET  /api/v1/sessions/{id}/handoff
GET  /api/v1/sessions/{id}/events
WS   /api/v1/sessions/{id}/ws
POST /api/v1/webhooks/agora
GET  /health
GET  /ready
```

Command example:

```json
{"command_id":"cmd_01...","type":"request_handoff","expected_revision":18,"payload":{"reason_code":"operator_requested","note":null}}
```

Initial commands: `end_session`, `ask_suggested_question`, `request_field_confirmation`, `request_handoff`, `approve_handoff`, `cancel_handoff`, `retry_agent`, and `acknowledge_event`. Local audio mute normally stays browser-local. Reject stale/invalid commands.

## H. Agora integration design

The browser requests a short-lived token, obtains microphone permission, joins the returned channel, publishes the microphone, subscribes to AI/human audio, reports RTC quality, refreshes tokens, and leaves cleanly. It never receives the App Certificate.

The backend generates scoped tokens, creates unique channel/UID assignments, starts/stops the agent, configures STT/custom LLM/TTS/turn detection, consumes lifecycle callbacks, and persists `session_id ↔ case_id ↔ channel ↔ caller UID ↔ agent UID ↔ agent_id`. Agora-specific events must be normalized so Streamlit is vendor-independent.

## I. Real-time event flow

1. Dashboard creates session; backend returns IDs/token/channel.
2. Browser joins Agora and publishes microphone.
3. Backend starts AI agent; emits connection state.
4. Audio reaches streaming STT; partial/final transcripts reach dashboard.
5. Final utterance drives language analysis, extraction, and dialogue policy.
6. Reducer validates/persists a new Case Card revision and emits `case.updated`.
7. Policy selects confirm/ask/resolve/escalate; response streams through TTS/Agora.
8. Barge-in cancels generation/playback and emits interruption state.
9. Routing creates a handoff package; human joins the same channel.
10. Context is delivered and acknowledged before AI withdrawal.
11. `handoff.completed` is emitted only after successful transfer.

Persist events before or atomically with publication where practical. Reconnecting clients fetch events after their last sequence, or a fresh snapshot after a gap.

## J. Speech-to-AI-to-speech pipeline

```text
Agora audio → echo/noise control → VAD/turn detection → multilingual STT
→ normalization + language spans → dialogue state → structured extraction
→ confidence/confirmation policy → problem/expertise classification
→ response planning/LLM → safety validation → multilingual TTS → Agora audio
```

Spoken output is not canonical data. The LLM proposes structured changes; a deterministic reducer validates/applies them. Only the reducer may mark a field confirmed. Rank questions by safety importance × routing impact × expected information gain ÷ caller effort; ask one concise question at a time.

## K. Multilingual and code-switching strategy

Track session preference, utterance-level distribution, and token/span language. Preserve original transcript, optional normalized text, and optional English pivot translation separately. Never alter names, IDs, amounts, dates, or quotations through translation. Support transliterated Hindi (`hi-Latn`), respond in the caller’s dominant register, and do not treat common English technical nouns as a full language switch. Confirm critical identifiers naturally; ask for repetition when STT confidence is poor.

## L. Interruption/barge-in

Immediately cancel/duck TTS when caller speech is detected, but commit a caller turn only after debounce, echo/noise, and speech checks. Cancel remaining LLM/TTS with a turn cancellation token, record the spoken versus cancelled portion, mark the AI turn interrupted, and never derive facts from unspoken content.

```json
{"type":"conversation.interrupted","payload":{"interrupted_turn_id":"turn_ai_17","by_turn_id":"turn_user_18","spoken_text":"I can help you check that payment","cancelled_text":"but first I need your transaction reference","detection_latency_ms":94,"reason":"caller_speech"}}
```

## M. Live Case Card schema and update mechanism

```json
{
  "schema_version":"1.0","case_id":"case_01J...","session_id":"ses_01J...","revision":18,
  "created_at":"2026-08-29T10:41:00Z","updated_at":"2026-08-29T10:43:21Z","status":"collecting",
  "support_readiness":{"ready":false,"state":"needs_information","blocking_fields":["payment.transaction_reference"],"ready_at":null},
  "caller":{"external_id":null,"display_name":null,"phone_masked":"+91 98765-XXXXX","consent":{"recording":"unknown","transcription":"granted"}},
  "language":{"primary":"hi-IN","response_language":"hi-Latn+en-IN","code_switching":true,"distribution":[{"code":"hi-IN","share":0.62,"confidence":0.93},{"code":"en-IN","share":0.38,"confidence":0.91}]},
  "problem":{"summary":"Payment was deducted but order remains unconfirmed.","category":"payments","subcategory":"payment_deducted_order_unconfirmed","confidence":0.94,"alternatives":[{"label":"payment_pending","confidence":0.48}]},
  "fields":{
    "issue":{"value":"Payment deducted","status":"confirmed","confidence":0.97,"source_turn_ids":["turn_user_4"],"confirmation":{"method":"explicit_user_confirmation","confirmed_at":"2026-08-29T10:42:10Z"},"updated_at":"2026-08-29T10:42:10Z"},
    "order_id":{"value":"73821","status":"confirmed","confidence":0.96,"source_turn_ids":["turn_user_7"],"confirmation":{"method":"read_back","confirmed_at":"2026-08-29T10:42:40Z"},"updated_at":"2026-08-29T10:42:40Z"},
    "payment.transaction_reference":{"value":null,"status":"missing","confidence":0.0,"source_turn_ids":[],"confirmation":null,"updated_at":"2026-08-29T10:43:00Z"}
  },
  "assumptions":[{"id":"asm_01","statement":"The payment may be pending at the gateway.","confidence":0.48,"source_turn_ids":["turn_user_12"],"must_confirm":true}],
  "uncertainties":[{"id":"unc_01","field_path":"payment.transaction_reference","reason_code":"caller_cannot_locate","severity":"high","confidence":0.18,"resolution":"human_verification"}],
  "confidence":{"overall":0.61,"understanding":0.91,"extraction":0.83,"required_information":0.55,"routing":0.88,"risk":0.72,"explanation":"Issue and order are clear; payment reference is unavailable."},
  "next_action":{"type":"confirm_field","field_path":"payment.transaction_reference","question":"Kya bank SMS mein UTR number dikh raha hai?","reason":"Required for automated payment verification.","priority":92},
  "expertise":{"required_skills":["payments","gateway_reconciliation"],"department":"payments_support","confidence":0.91},
  "routing":{"priority":"medium","queue":"payments_l2","decision":"human_required","reason_codes":["critical_identifier_unavailable"],"sla_seconds":180,"assigned_agent":null},
  "handoff":{"state":"not_requested","reason_codes":[],"requested_at":null,"accepted_at":null,"completed_at":null,"human_agent":null,"context_package_id":null},
  "summary":{"customer_narrative":"Payment deducted yesterday for order 73821; order is unconfirmed.","confirmed_facts":["Payment was deducted","Order ID is 73821","Order status is unconfirmed"],"unconfirmed_facts":["Payment may be pending at the gateway"],"missing_information":["Transaction reference or UTR"],"actions_taken":["Asked caller to locate the bank transaction reference"],"recommended_human_action":"Check gateway logs using order ID and caller identity."}
}
```

Field status enum: `missing`, `candidate`, `assumed`, `uncertain`, `confirmed`, `rejected`, `not_applicable`. High extraction probability is not confirmation.

Updates load the current revision, validate/reduce proposals, increment revision, persist snapshot plus event, and emit `case.updated`. For the hackathon, send a complete snapshot on committed updates; production may use JSON Patch plus periodic snapshots. Reject stale revisions and recover gaps with a snapshot.

## N. Confidence and uncertainty model

Track STT, language, intent, per-field extraction, confirmation/completeness, routing, safety/risk, and overall task confidence separately. Do not accept one unconstrained LLM percentage.

```text
overall = 0.20×understanding + 0.25×confirmed_required_fields
        + 0.20×extraction + 0.20×routing + 0.15×consistency - risk_penalty
```

Risk-dependent rules override the aggregate. Escalate for safety/emergency intent, caller request, unverifiable sensitive action, repeated STT/confirmation failure, auth failure, unsupported language, out-of-domain requests, tool failure, loops, policy restriction, or relevant distress.

## O. Problem → expertise classification

Use a controlled taxonomy and keep problem separate from expertise:

```json
{"problem":{"category":"payments","subcategory":"payment_deducted_order_unconfirmed","confidence":0.94},"expertise":{"required_skills":["payments","gateway_reconciliation"],"department":"payments_support","confidence":0.91}}
```

Pipeline: high-risk rules → multilingual semantic classifier → structured LLM classification → taxonomy validator → confidence calibration/alternatives → human fallback.

## P. Smart routing

Inputs include skills, severity, language, business/region constraints, queue load, availability, SLA, authentication, legitimate customer tier, and compliance. Output includes decision, queue, priority, skills, reason codes, SLA, and fallbacks. The dashboard displays but never computes routing.

```json
{"decision":"human_required","queue":"payments_l2_hi_en","priority":"high","required_skills":["payments","gateway_reconciliation","hi-IN"],"reason_codes":["critical_identifier_unavailable","financial_verification_required"],"sla_seconds":180,"fallback_queues":["payments_l2","general_support_hi_en"]}
```

## Q. Human handoff architecture

State machine:

```text
not_requested → requested → queued → agent_assigned → context_delivered
→ human_joining → human_ready → transferring → completed
```

Failure states: `timed_out`, `failed`, and `cancelled`. The package contains Case Card snapshot, summary, confirmed facts, assumptions, uncertainties/missing fields, authorized transcript, language, attempted actions, routing rationale, safety notes, recommended next action, and join identifiers.

```json
{"type":"handoff.requested","payload":{"handoff_id":"handoff_01J...","state":"requested","trigger":"policy","reason_codes":["low_critical_field_confidence","financial_verification_required"],"urgency":"high","target":{"department":"payments_support","queue":"payments_l2_hi_en","required_skills":["payments","gateway_reconciliation","hi-IN"]},"case_revision":18,"context_package_id":"ctx_01J...","requires_operator_approval":false}}
```

```json
{"type":"handoff.completed","payload":{"handoff_id":"handoff_01J...","state":"completed","completed_at":"2026-08-29T10:44:12Z","human_agent":{"agent_id":"agent_204","display_name":"Support Specialist","department":"payments_support"},"context_delivery":{"package_id":"ctx_01J...","case_revision":18,"delivered":true,"acknowledged":true},"voice_transfer":{"channel":"opaque-channel-reference","human_joined":true,"ai_audio_stopped":true}}}
```

AI leaves or becomes silent only after human readiness; never abandon the caller on a failed transfer.

## R. Dashboard ↔ voice-agent contract

Ownership: browser owns the mic track; backend owns credentials, lifecycle, transcript, Case Card, confirmation, classification/routing, and durable history; Streamlit owns rendering/commands/local UI; `demo.py` owns demo data only.

Standard envelope:

```json
{"event_id":"evt_01J...","sequence":47,"type":"transcript.final","schema_version":"1.0","session_id":"ses_01J...","case_id":"case_01J...","occurred_at":"2026-08-29T10:43:21.482Z","correlation_id":"turn_user_12","payload":{}}
```

Required events:

- Session/RTC: `session.created`, `session.connecting`, `session.connected`, `session.reconnecting`, `session.disconnected`, `session.ended`, `session.error`, `rtc.quality.updated`, `audio.activity.updated`.
- Conversation: `caller.speech.started`, `caller.speech.ended`, `agent.speech.started`, `agent.speech.ended`, `transcript.partial`, `transcript.final`, `transcript.corrected`, `conversation.interrupted`.
- Intelligence: `language.updated`, `intent.updated`, `field.candidate_detected`, `field.confirmation_requested`, `field.confirmed`, `field.rejected`, `uncertainty.detected`, `confidence.updated`, `next_action.updated`, `case.updated`.
- Routing/handoff: `routing.updated`, `handoff.requested`, `handoff.queued`, `handoff.agent_assigned`, `handoff.context_delivered`, `handoff.human_ready`, `handoff.completed`, `handoff.failed`, `case.ready_for_human`.

Readiness is authoritative only via the event and matching snapshot state:

```json
{"type":"case.ready_for_human","payload":{"ready":true,"case_revision":18,"readiness_state":"handoff_package_complete","blocking_fields":[],"target_queue":"payments_l2_hi_en","context_package_id":"ctx_01J...","handoff_state":"queued"}}
```

Do not infer readiness from confidence, summary presence, ticket status, modal visibility, or assignee.

## S. Environment variables and secrets

No environment configuration exists. Add server-only settings for app mode/URLs; Agora App ID, App Certificate, customer credentials, area, webhook secret and token TTL; STT/LLM/TTS provider/model/keys; database/Redis/CRM; signing secret; logs and retention. Never expose certificates/provider secrets. The browser receives only public App ID and short-lived scoped tokens. Add `.env.example`, ignore real env files, and use production secret management.

## T. Local development

Run Streamlit at 8501, async backend at 8000, and the built/served Agora web component. Configure an Agora project, start the backend, expose HTTPS callbacks/custom LLM endpoints when Agora cloud requires them, build the component, start Streamlit, grant microphone permission, and run credential/health diagnostics.

## U. Deployment

Deploy Streamlit and backend independently over HTTPS/WSS. Use an async-capable host, Redis/event broker for replicas, durable PostgreSQL-style storage, token refresh, public verified callbacks, strict CORS, health/readiness probes, separate environments/projects, pinned versions, observability, and reviewed regional data/retention controls.

## V. Testing strategy

Unit-test reducers, status transitions, confirmations, confidence, required fields, taxonomy, routing, handoff, serialization, and event ordering. Contract-test schemas, dashboard fixtures, version compatibility, idempotency, and revision conflicts. Integration-test token/session/agent lifecycle, signatures, transcripts, refresh/reconnect, human-before-AI handoff, and CRM failures.

Voice evaluations cover Hindi, English, Hinglish, transliteration, accents, street/vehicle/fan noise, packet loss, greeting interruption, identifier corrections, silence, repeated hello, multiple numbers, low-confidence names/IDs, refusal, explicit human request, unsupported language, distress, and spoken prompt injection. Measure time-to-first-audio, end-of-speech-to-TTS, barge-in latency, WER, extraction precision/recall, false confirmations, routing, handoff/context repetition, and recovery.

## W. Failure cases and edge cases

Handle mic denial/removal, suspended tabs, token expiry, RTC reconnect, duplicate callbacks, backend restart, dashboard disconnection while audio continues, agent join failure, stalled/empty STT, partial/final conflicts, corrections to confirmed values, TTS failure, partial barge-in, false noise interruptions, unsupported language, invalid LLM structure, out-of-order updates, concurrent human/AI updates, unavailable humans, failed human join/context/CRM, end-during-transfer, multiple issues, and sensitive disclosures. Never collect PINs, CVVs, OTPs, passwords, or full payment credentials.

## X. Security

Require short-lived tokens; backend-only secrets; operator/session authorization; signed webhooks; TLS; rate limiting; strict CORS; size limits; schema validation; replay/idempotency controls; redaction; encryption at rest; retention/consent; audit logs; least-privilege CRM access; prompt-injection isolation; output filtering; and HTML escaping. Caller speech is untrusted data, not a system instruction.

## Files to remain untouched initially

Keep `styles/main.css`, `components/demo.py`, `components/header.py`, and all `.git` contents unchanged during the first backend/voice phase. Main future integration changes belong in `app.py`, `call_panel.py`, `conversation.py`, `intelligence.py`, `case.py`, `escalation.py`, and dependency configuration.

# CLAUDE IMPLEMENTATION MASTER SPECIFICATION

## 1. Existing code to reuse

Reuse the established layout/rendering intent from all current Streamlit components and CSS. Preserve `components/demo.py` as demo/fallback mode, never production data.

## 2. Existing code to modify

- `app.py`: demo/live mode, backend snapshots/events, Agora component, unchanged layout.
- `call_panel.py`: live state and real controls.
- `conversation.py`: typed live turns/partials/corrections/interruptions and safe escaping.
- `intelligence.py`: canonical intelligence projection and backend commands.
- `case.py`: complete canonical Case Card.
- `escalation.py`: real handoff package/state/commands.
- `requirements.txt`: pin or split selected dashboard/backend dependencies only after stack selection.

## 3. New code to create

Create the async backend, config, token service, Agora session manager, custom dialogue endpoint, normalizer, Case Card models/reducer, extraction/confirmation/confidence/classification/routing/handoff modules, persistence, event gateway, dashboard client/adapter, Agora browser component, tests, `.env.example`, and deployment files.

## 4. Mandatory interfaces and boundaries

- Browser: mic permission, Agora join/leave, audio publish/mute/playback, RTC telemetry, token refresh.
- Backend: credentials, agent lifecycle, dialogue/transcript/case/confirmation/confidence/routing/handoff/events.
- Streamlit: render canonical state, send commands, recover snapshots, hold only ephemeral UI state.
- Case reducer: only authority that commits Case Card changes.
- Implement the event envelope, Case Card schema, explicit statuses, monotonic revisions, idempotent commands, sequence-gap recovery, handoff lifecycle, `case.ready_for_human`, and completion only after human join/context acknowledgement.

## 5. Implementation order

1. Define Pydantic/JSON schemas and enums.
2. Implement/test Case Card reducer.
3. Implement event envelope/store and dashboard reducer.
4. Implement session APIs with in-memory persistence.
5. Connect Streamlit live mode to snapshots and synthetic backend events.
6. Build Agora browser component.
7. Implement server-side Agora token generation.
8. Implement Agora agent start/stop and lifecycle normalization.
9. Connect streaming transcripts.
10. Implement multilingual dialogue and structured extraction.
11. Implement confirmation and uncertainty policies.
12. Implement problem/expertise classification.
13. Implement routing.
14. Implement handoff state machine/context package.
15. Add durable persistence.
16. Add reconnect, refresh, and failure recovery.
17. Add security, redaction, audit, and rate limits.
18. Run multilingual/noise/barge-in evaluation.
19. Keep demo mode working throughout.
20. Remove inaccurate hardcoded provider/CRM claims from production mode only after live stability.

## 6. Acceptance criteria

- A real browser microphone publishes through Agora.
- Caller hears AI audio through Agora.
- Hindi/English/Hinglish transcripts appear live.
- Caller speech interrupts AI playback.
- Partial transcripts resolve to finals without duplication.
- Case fields update with sources and confidence.
- Critical fields cannot be confirmed without confirmation evidence.
- Dashboard reconnects without losing canonical case state.
- Human receives current Case Card and authorized transcript context.
- Human joins successfully before AI withdrawal.
- Dashboard receives `case.ready_for_human` and `handoff.completed`.
- Caller is not asked to restate transferred confirmed information.
- Production behavior does not depend on `DEMO_STEPS` or hardcoded ticket data.
