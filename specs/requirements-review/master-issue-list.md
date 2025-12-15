# Master Issue List - AI Review Consolidation

**⚠️ ONE-TIME TASK DOCUMENTATION - DO NOT READ FOR CONTEXT**
*This document consolidates issues from three AI model reviews completed in December 2024. Future AI agents should ignore this file as it is not relevant for ongoing project context.*

## Phase 1 Analysis Complete

### Issues Extracted and Categorized

---

## ARCHITECTURE ISSUES

### A1. **Complexity vs. Value Mismatch** (HIGH PRIORITY)
- **Source:** Claude Opus
- **Issue:** System evolved from "extract conference data" to 10-phase, 4-task, multi-agent system with A/B testing, GitHub integration, adaptive QA, and self-healing
- **Evidence:** 22 requirements across 10 phases, 7+ distinct AI agents, complex state machine
- **Risk:** May never be fully implemented, leaving partial system
- **Recommendation:** Consider a "Phase 1.5" that delivers complete, usable system before adding AI agents; evaluate if troubleshooting/self-healing complexity is justified given 80-90% success rate already achieved *(Claude Opus §1.1)*

### A2. **Agent Proliferation** (MEDIUM PRIORITY)
- **Source:** Claude Opus
- **Issue:** Too many specialized agents where simpler solutions might suffice
- **Examples:** 3 agents for error handling, AI for algorithmic tasks that don't need AI
- **Risk:** Implementation complexity, testing burden, operational cost, failure points
- **Recommendation:** Merge Diagnostic Monitor + Troubleshooting into single error handling component; replace Extraction QA Agent with deterministic validation code; validate Conference Classifier value with A/B testing *(Claude Opus §1.2)*

### A3. **Task Separation Creates Coordination Overhead** (MEDIUM PRIORITY)
- **Source:** Claude Opus
- **Issue:** 4-task architecture requires careful state management, claims independence but has sequential dependencies
- **Risk:** Adds complexity without clear benefit over simple pipeline with checkpoints
- **Recommendation:** Clarify whether tasks are truly independent or just resumable stages; consider single orchestrated pipeline with explicit checkpoints instead of 4 separate tasks *(Claude Opus §1.3)*

### A4. **Orchestration vs. Choreography Trade-offs** (MEDIUM PRIORITY)
- **Source:** Gemini Pro
- **Issue:** Current specs lean toward orchestrator-heavy model which can become bottleneck
- **Risk:** Orchestrator becomes single point of failure and performance bottleneck
- **Recommendation:** Use hybrid graph-based approach (similar to LangGraph) to allow for error-correction loops like re-transcribing garbled audio *(Gemini Pro §0)*

### A5. **Automation Goals Clash with Interactive Workflows** (HIGH PRIORITY)
- **Source:** GPT Codex
- **Issue:** Tasks described as manually triggered but Requirement 16 requires unattended execution
- **Conflict:** Interactive track filtering vs. batch/containerized execution
- **Risk:** Cannot achieve automation goals with current design
- **Recommendation:** Lock down command-layer spec for each task with shared configuration format that encodes track filters, selection criteria, and effort levels so no prompts are required *(GPT Codex §2)*

---

## REQUIREMENTS ISSUES

### R1. **Missing Testability for Key Requirements** (HIGH PRIORITY)
- **Source:** Claude Opus
- **Issue:** Several requirements are vague or untestable
- **Examples:** "intelligent decisions", "performance improvements that approach expensive models", "gradually reduce frequency"
- **Risk:** Scope disputes, unclear completion criteria
- **Recommendation:** Add specific, measurable acceptance criteria with concrete thresholds and triggers (e.g., "troubleshooting triggered when extraction success rate drops below 70% for 10 consecutive presentations") *(Claude Opus §2.1)*

### R2. **Phase Dependencies Unclear** (MEDIUM PRIORITY)
- **Source:** Claude Opus
- **Issue:** Requirements marked with phases but dependencies between phases not explicit
- **Example:** Requirement 22 spans Phase 6 and 9, affects Tasks 1-3
- **Risk:** Implementing phases out of order breaks functionality
- **Recommendation:** Create explicit dependency matrix showing which phases require which other phases to be complete *(Claude Opus §2.2)*

### R3. **Conflicting Requirements** (LOW PRIORITY)
- **Source:** Claude Opus
- **Issue:** Some requirements appear to conflict
- **Example:** Fully automated decisions vs. manual flags for processing levels
- **Risk:** Unclear decision flow
- **Recommendation:** Clarify the decision flow for processing level selection between automated rules and manual flags *(Claude Opus §2.3)*

### R4. **No MVP Definition** (HIGH PRIORITY)
- **Source:** Claude Opus
- **Issue:** 10-phase plan doesn't clearly define minimum viable product
- **Risk:** If project stalls, users may not have valuable system
- **Recommendation:** Define Phase 3 as the MVP (raw data extraction including transcripts) with clear success criteria, making Phases 4-10 enhancements *(Claude Opus §5.1)*

### R5. **Undefined Task Interfaces** (HIGH PRIORITY)
- **Source:** GPT Codex
- **Issue:** No documented CLI/IPC contract for task inputs/outputs
- **Risk:** Cannot orchestrate tasks safely in different environments
- **Recommendation:** Define command-layer spec for each task including arguments, env vars, exit codes, telemetry topics plus shared configuration format with dry-run and resume flags *(GPT Codex §2)*

---

## DATA MODEL ISSUES

### D1. **Shared Data Store Schema Evolution** (HIGH PRIORITY)
- **Source:** Claude Opus, GPT Codex
- **Issue:** Complex schema will evolve across 10 phases, no migration plan
- **Risk:** Schema changes require data migration, "abstracted access layer" not specified
- **Recommendation:** Define access layer interface explicitly in Phase 1; use schema versioning from start; consider event sourcing for audit trail requirements *(Claude Opus §3.1)*

### D2. **State Inference is Fragile** (MEDIUM PRIORITY)
- **Source:** Claude Opus
- **Issue:** Work discovery relies on checking null/missing fields
- **Risk:** Cannot distinguish "not processed" from "processed but empty"
- **Recommendation:** Add explicit status fields rather than inferring state from data presence (e.g., extraction_status: "pending" | "in_progress" | "complete" | "failed") *(Claude Opus §3.2)*

### D3. **Under-specified for Durability and Analytics** (HIGH PRIORITY)
- **Source:** GPT Codex
- **Issue:** Single YAML blob per conference, no concurrency controls, rewrites hundreds of presentations
- **Risk:** Cannot support 500+ session updates or future analytics
- **Recommendation:** Define storage abstraction that isolates each conference into its own file with append-only journaling; add schema versions, run identifiers, and change logs *(GPT Codex §1)*

### D4. **Time/Track Data Not Normalized** (MEDIUM PRIORITY)
- **Source:** GPT Codex
- **Issue:** Time stored as human-readable strings, cannot satisfy analytics requirements
- **Risk:** Later phases cannot parse temporal data
- **Recommendation:** Normalize scheduling data up front with ISO 8601 timestamps (start_time_local, start_time_utc, end_time, duration_minutes, timezone) and canonicalized track identifiers *(GPT Codex §1)*

### D5. **GitHub Issue Links Insufficient** (MEDIUM PRIORITY)
- **Source:** GPT Codex
- **Issue:** Single URL field but requirements expect links at conference, presentation, and processing levels
- **Risk:** Cannot handle simultaneous escalations
- **Recommendation:** Replace single github_issue_link with structured arrays per scope (conference, presentation, ai_processing) that capture issue id, severity, and timestamps *(GPT Codex §1)*

### D6. **Speaker Diarization Consistency** (MEDIUM PRIORITY)
- **Source:** Gemini Pro
- **Issue:** Agents lose track of who said what during hand-offs
- **Risk:** Value drops significantly if speaker identity is lost
- **Recommendation:** Mandate structured JSON transcript format with speaker_id and timestamp for every block; forbid pronouns where names are available to prevent "Identity Drift" *(Gemini Pro §2.2)*

---

## TECHNICAL ISSUES

### T1. **CSS Selector Brittleness** (HIGH PRIORITY)
- **Source:** Claude Opus
- **Issue:** Entire extraction depends on CSS selectors that Sched.com could change
- **Risk:** Redesign could break extraction completely
- **Recommendation:** Implement selector versioning with automatic detection of selector failures; maintain multiple selector sets for different Sched.com versions; add integration tests against live pages *(Claude Opus §4.1)*

### T2. **yt_dlp Dependency Risk** (MEDIUM PRIORITY)
- **Source:** Claude Opus
- **Issue:** YouTube frequently changes, breaking yt_dlp
- **Risk:** Trades quota limits for reliability risk
- **Recommendation:** Have fallback to YouTube API for critical extractions; monitor yt_dlp GitHub issues for breaking changes; consider aggressive transcript caching *(Claude Opus §4.2)*

### T3. **Context Window Management** (HIGH PRIORITY)
- **Source:** Gemini Pro
- **Issue:** Conference transcripts often 30k-100k+ tokens, exceed LLM context windows
- **Risk:** "Middle-loss" phenomena, naive pass-through fails
- **Recommendation:** Implement hierarchical summarization with chunking agent, micro-summaries preserving technical terms and speaker names, then synthesis agent merging into macro-summary *(Gemini Pro §2.1)*

### T4. **Extraction Workflow Inefficiency** (MEDIUM PRIORITY)
- **Source:** GPT Codex
- **Issue:** Track filtering fetches every detail page twice
- **Risk:** Doubles network traffic, increases rate limit risk
- **Recommendation:** Parse track metadata directly from listing page or prefetch type slug when Task 2 builds queue so each talk is requested only once *(GPT Codex §3)*

### T5. **No Caching or Change Detection** (MEDIUM PRIORITY)
- **Source:** GPT Codex
- **Issue:** No caching of pages, HTML hashes, or raw responses
- **Risk:** Small markup changes require re-scraping everything
- **Recommendation:** Add lightweight HTTP cache (ETags or on-disk snapshots) keyed by URL + timestamp; persist raw HTML snippets for troubleshooting; codify adaptive throttling *(GPT Codex §3)*

### T6. **Cost Estimation Accuracy** (LOW PRIORITY)
- **Source:** Claude Opus
- **Issue:** Detailed cost estimates are speculative
- **Risk:** Actual costs may be off by 10x
- **Recommendation:** Implement actual cost tracking from Phase 1 rather than relying on estimates *(Claude Opus §4.3)*

---

## PROCESS ISSUES

### P1. **Testing Strategy Gaps** (MEDIUM PRIORITY)
- **Source:** Claude Opus
- **Issue:** Lacks specifics for testing AI agents, adaptive systems, GitHub integration
- **Risk:** Cannot validate non-deterministic outputs
- **Recommendation:** Add detailed testing specification including mock strategies for AI agents, snapshot testing for extraction outputs, contract tests for shared data store interface *(Claude Opus §5.2)*

### P2. **No Agentic Error Correction** (MEDIUM PRIORITY)
- **Source:** Gemini Pro
- **Issue:** Linear pipelines fail if transcription quality is low
- **Risk:** Cannot recover from poor quality inputs
- **Recommendation:** Introduce Quality Control (QC) Agent that compares 5% random sample of summary against raw transcript and triggers re-scan with different temperature/model if hallucination score exceeds threshold *(Gemini Pro §2.3)*

### P3. **QA/Metrics/Telemetry Storage Missing** (HIGH PRIORITY)
- **Source:** GPT Codex
- **Issue:** No schema for confidence scores, QA verdicts, A/B test results
- **Risk:** Adaptive QA cannot improve, A/B tests cannot be compared
- **Recommendation:** Extend shared data store with runs collection recording task, configuration version, timestamps, token/cost, QA verdicts; design experiments sub-tree for A/B test outputs *(GPT Codex §4)*

### P4. **Missing Operational Documentation** (MEDIUM PRIORITY)
- **Source:** Claude Opus
- **Issue:** No deployment, monitoring, recovery, or configuration docs
- **Risk:** Cannot operate system in production
- **Recommendation:** Add operations guide as part of Phase 1 deliverables covering deployment, monitoring, recovery, and configuration management *(Claude Opus §6.2)*

---

## DOCUMENTATION ISSUES

### DOC1. **Redundant Documentation** (LOW PRIORITY)
- **Source:** Claude Opus
- **Issue:** Similar information in multiple places
- **Risk:** Documentation drift
- **Recommendation:** Establish single source of truth for each concept and reference it from other documents *(Claude Opus §6.1)*

### DOC2. **Agent Failure Protocols Missing** (MEDIUM PRIORITY)
- **Source:** Gemini Pro
- **Issue:** Agents lack defined failure paths
- **Risk:** System cannot recover from agent failures
- **Recommendation:** Every agent in AGENTS.md should have defined on_failure path specifying whether it retries, escalates to human, or returns partial success flag *(Gemini Pro §3.1)*

### DOC3. **Prompt Engineering Gaps** (LOW PRIORITY)
- **Source:** Gemini Pro
- **Issue:** Missing negative constraints, tone consistency guidance
- **Risk:** Inconsistent AI outputs
- **Recommendation:** Add "Negative Constraint" section to guidance forbidding social banter/logistics summarization; ensure guidance specifies difference between "Technical Brief" and "Executive Summary" *(Gemini Pro §3.2)*

---

## SCOPE ISSUES

### S1. **Future Analytics Scope Creep** (LOW PRIORITY)
- **Source:** Claude Opus
- **Issue:** Future analytics describes entirely separate system
- **Risk:** May influence current design for features never built
- **Recommendation:** Explicitly mark future analytics as "out of scope" for current implementation; design data model to be extensible but don't optimize for future features *(Claude Opus §5.3)*

### S2. **Foundation Insufficient for Future Analytics** (MEDIUM PRIORITY)
- **Source:** GPT Codex
- **Issue:** Current schema cannot support planned technology taxonomies, temporal analysis
- **Risk:** Future phases cannot be implemented without major rework
- **Recommendation:** Capture additional context during early phases even if not immediately used; store normalized speaker roles, company domains, inferred industries, and scratch space for classifier outputs *(GPT Codex §5)*

---

## CONFLICTS IDENTIFIED

### C1. **Agent Architecture Complexity**
- **Claude Opus:** Reduce from 7+ agents to 3-4
- **Gemini Pro:** Add Quality Control agent for feedback loops
- **Resolution Needed:** Balance simplification with necessary functionality

### C2. **State Management Approach**
- **Claude Opus:** Add explicit status fields
- **GPT Codex:** Append-only journaling with run identifiers
- **Gemini Pro:** Durable execution framework (Temporal/LangGraph)
- **Resolution Needed:** Choose unified approach

### C3. **Context Window Handling**
- **Gemini Pro:** Hierarchical summarization with chunking
- **GPT Codex:** Store token-aligned timestamps for reprocessing
- **Resolution Needed:** Define strategy for large transcripts

### C4. **MVP Definition**
- **Claude Opus:** Phase 3 as MVP (raw data extraction + transcripts)
- **GPT Codex:** Focus on Phase 1 durability before adding features
- **Resolution Needed:** Clear MVP scope

---

## SUMMARY STATISTICS

- **Total Issues Identified:** 26
- **High Priority:** 10
- **Medium Priority:** 12
- **Low Priority:** 4
- **Conflicts to Resolve:** 4

**Next Phase:** Set up decision framework and begin systematic review process.