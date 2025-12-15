# Decision Journal

**⚠️ ONE-TIME TASK DOCUMENTATION - DO NOT READ FOR CONTEXT**
*This journal captures all decisions made during the December 2025 requirements review process. Future AI agents should ignore this file.*

## Review Process Status

**Current Phase:** Phase 3 - Systematic Review Process  
**Issues to Review:** 26 total
**Decisions Made:** 26 + 4 conflicts = 30
**Skipped for Later:** 0
**Actions Completed:** 0

---

## Decision Log

### A1. Complexity vs. Value Mismatch (HIGH PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Phase 1 and 2 are already designed to provide significant benefit all by themselves. It is true that the whole system may not get implemented - the reality is we will do implementation until it fits our needs, then stop. This is why we are doing a phased approach, with a fully functional, useful system available at the end of each phase. Also, the AI powered task implemented in phase 2 is extremely easy to implement, so does not really add much complexity or risk.
**Status:** ✅ Complete

### A5. Automation Goals Clash with Interactive Workflows (HIGH PRIORITY)
**Decision:** Accept & Resolve Now (partial) + Reject - Disagree (partial)
**Reasoning:** It is true that the requirements do refer to things that are user selectable. The documents should be updated to change that type of language to indicate that the user selects the option by editing the shared data store between batch runs, rather than in an interactive way with a front end. This specification inconsistency leads to a misunderstanding of the rest of the architecture, which is why we will not be accepting the recommendation. We will update the specification documents, but not anything else.
**Target Documents:** Requirements and implementation context documents to clarify "user selectable" means configuration via shared data store, not interactive UI
**Status:** ✅ Complete

---

## Additional Decisions

### NEW PHASES REQUIRED
Based on decision feedback, the following new phases must be added:

#### Phase 7.2: Conference Classifier Implementation
Implement the conference classifier agent that primes other AI agents with context-specific prompts to improve performance.

#### Phase 7.4: Transcript Formatter Implementation  
Implement the transcript formatter agent with speaker diarization consistency.

#### Phase 7.6: Summarizer Implementation
Implement the summarizer agent that creates presentation summaries.

#### Phase 7.8: Dense Knowledge Encoder Implementation
Implement the dense knowledge encoder agent for creating dense representations.

#### Phase 11: NoSQL Database Migration
Migrate from file-based to NoSQL database for shared state to expose parallelism. Allows multiple tasks running simultaneously on different conferences. May be done out of order or never, depending on parallelism needs.

#### Phase 12: Task Scope Control
Add optional arguments to task execution that limit scope (e.g., filter by tags, single conference processing). Enables high-level conference capture without automatic follow-on processing. Supports parallelism when combined with NoSQL database.

---

## Formal Decision Log

### R1. Missing Testability for Key Requirements (HIGH PRIORITY)
**Decision:** Accept & Resolve Now + Accept & Defer
**Reasoning:** Update requirement 3.2 to remove "intelligent decisions" → troubleshooting triggered when information is garbled or zero-length (criteria defined in Phase 4 design). Update requirement 11.4 to clarify priming → classifier must run before summarizer/formatter/encoder agents. Update requirement 12.4 to specify frequency algorithm → decrease on success, increase on failure (algorithm details in Phase 8 design).
**Target Documents:** Requirements document
**Status:** ✅ Complete

### R4. No MVP Definition (HIGH PRIORITY)  
**Decision:** Reject - Disagree
**Reasoning:** The phased plan is explicitly designed to produce a system that provides value at the end of every phase. Completing phase 1 results in a minimum viable product. Since building for personal use, can decide when to stop based on needs.
**Status:** ✅ Complete

### R5. Undefined Task Interfaces (HIGH PRIORITY)
**Decision:** Accept & Defer
**Reasoning:** Valid comment. Task interfaces (CLI/IPC contracts) must be defined as part of Phase 1 design, equally important as data schema definition.
**Target Phase:** Phase 1 design
**Status:** ✅ Complete

### D1. Shared Data Store Schema Evolution (HIGH PRIORITY)
**Decision:** Accept & Defer
**Reasoning:** Data model planning needed during Phase 1 design to consider growth needs and avoid major changes later. Data migrations acceptable if needed since dealing with textual data.
**Target Phase:** Phase 1 design
**Status:** ✅ Complete

### D3. Under-specified for Durability and Analytics (HIGH PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** System explicitly implements abstract data layer, acknowledges YAML isn't scalable, plans NoSQL migration. Low parallelism level acceptable, abstract layer enables higher-performance backends when needed.
**Status:** ✅ Complete

### T1. CSS Selector Brittleness (HIGH PRIORITY)
**Decision:** Accept & Defer
**Reasoning:** Address entirely during Phase 5 design (troubleshooting agents). Option to pull forward to Phase 1 or 3 if Sched page structures differ across conferences.
**Target Phase:** Phase 5 design
**Status:** ✅ Complete

### T3. Context Window Management (HIGH PRIORITY)
**Decision:** Reject - Out of Scope
**Reasoning:** Modern model context windows (Claude Sonnet 200K, GPT-4o 128K, GPT-5.2 400K, Gemini 1M) far exceed presentation transcript sizes. Fresh context used for each processing action.
**Status:** ✅ Complete

### P3. QA/Metrics/Telemetry Storage Missing (HIGH PRIORITY)
**Decision:** Accept & Defer
**Reasoning:** Address QA metrics design in Phase 8. Note: QA agent for web capture runs every execution; adaptive checking only for Task 3 QA agent. Recommendations too specific for current requirements/design level.
**Target Phase:** Phase 8 design
**Status:** ✅ Complete

### A2. Agent Proliferation (MEDIUM PRIORITY)
**Decision:** Accept & Defer
**Reasoning:** Learn proper abstraction level through phases. Defer consolidation decisions: QA/troubleshooting agents → Phase 5 design, extraction QA deterministic → Phase 4 design, classifier validation → Phase 7.2 design.
**Target Phases:** Phase 4, 5, 7.2 designs
**Status:** ✅ Complete

### A3. Task Separation Creates Coordination Overhead (MEDIUM PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Misunderstanding of intent. Tasks find and do available work, enabling gradual accumulation of detailed information. Provides flexibility for incremental processing while other tasks run. Tasks self-checkpoint by saving work.
**Status:** ✅ Complete

### A4. Orchestration vs. Choreography Trade-offs (MEDIUM PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Orchestrator-heavy by design. NoSQL data layer will expose arbitrary parallelism, removing bottlenecks. Need work prioritization/breakdown for parallelism (addressed in Phase 12).
**Status:** ✅ Complete

### R2. Phase Dependencies Unclear (MEDIUM PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Reviewer misinterpreted dependencies. Not necessary.
**Status:** ✅ Complete

### D2. State Inference is Fragile (MEDIUM PRIORITY)
**Decision:** Accept & Resolve Now
**Reasoning:** Clarify semantics: missing = not processed, null = processed but empty. Tasks granular enough to not need partial completion tracking.
**Target Documents:** Data model documentation
**Status:** ✅ Complete

### D4. Time/Track Data Not Normalized (MEDIUM PRIORITY)
**Decision:** Accept & Defer
**Reasoning:** Capture local time now. Future enrichment job can normalize to GMT when needed for analytics. Super-low priority since unlikely to correlate exact times across time zones.
**Target Phase:** Future analytics ideas file
**Status:** ✅ Complete

### D5. GitHub Issue Links Insufficient (MEDIUM PRIORITY)
**Decision:** Accept & Defer (partial) + Reject - Disagree (partial)
**Reasoning:** Structured field makes sense, but recommendation goes too far. Determine structure during Phase 6 design.
**Target Phase:** Phase 6 design
**Status:** ✅ Complete

### D6. Speaker Diarization Consistency (MEDIUM PRIORITY)
**Decision:** Accept & Defer
**Reasoning:** Defer to Phase 7.4 design (formatter agent implementation).
**Target Phase:** Phase 7.4 design
**Status:** ✅ Complete

### T2. yt_dlp Dependency Risk (MEDIUM PRIORITY)
**Decision:** Accept & Defer
**Reasoning:** Address in Phase 3 design. Record YouTube API as viable alternative.
**Target Phase:** Phase 3 design
**Status:** ✅ Complete

### T4. Extraction Workflow Inefficiency (MEDIUM PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Tiny optimization, misunderstood flow. No track filtering - just extracting track from URL. Data already fetched with full page.
**Status:** ✅ Complete

### T5. No Caching or Change Detection (MEDIUM PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Over-optimization of implementation detail, not architecture issue.
**Status:** ✅ Complete

### P1. Testing Strategy Gaps (MEDIUM PRIORITY)
**Decision:** Accept & Defer
**Reasoning:** Excellent catch. Phase 2: AI agent testing strategy, Phase 3: contract testing for data store, Phase 4: QA confidence system testing, Phase 6: GitHub integration testing. Schedule remaining recommendations in appropriate phase designs.
**Target Phases:** Phase 2, 3, 4, 6 designs
**Status:** ✅ Complete

### P2. No Agentic Error Correction (MEDIUM PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Misunderstanding - system uses existing YouTube transcripts, doesn't generate them. Only reformats, summarizes, or creates dense representations.
**Status:** ✅ Complete

### P4. Missing Operational Documentation (MEDIUM PRIORITY)
**Decision:** Accept & Resolve Now
**Reasoning:** Need requirements for up-to-date deployment, configuration, monitoring, and recovery documentation. Must be testable at end of every phase. Associate monitoring/recovery with Phase 5 design (troubleshooting implementation).
**Target Documents:** Requirements document + Phase 5 design
**Status:** ✅ Complete

### DOC2. Agent Failure Protocols Missing (MEDIUM PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Too low level for this review stage.
**Status:** ✅ Complete

### S2. Foundation Insufficient for Future Analytics (MEDIUM PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Will save all raw source data for future re-analysis. Won't add unused features.
**Status:** ✅ Complete

### R3. Conflicting Requirements (LOW PRIORITY)
**Decision:** Accept & Resolve Now
**Reasoning:** Clarify no user input during runs - all user input via shared data store. No automatic talk flagging currently, all talks processed identically.
**Target Documents:** Requirements document
**Status:** ✅ Complete

### T6. Cost Estimation Accuracy (LOW PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Reviewer misinterpreted document format example as actual data.
**Status:** ✅ Complete

### DOC1. Redundant Documentation (LOW PRIORITY)
**Decision:** Accept & Resolve Now
**Reasoning:** Add requirements to verify documentation is up-to-date, self-consistent, and avoids redundancy at end of every phase. Must be testable.
**Target Documents:** Requirements document
**Status:** ✅ Complete

### DOC3. Prompt Engineering Gaps (LOW PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Too specific and low-level for this review stage. Not relevant for current work.
**Status:** ✅ Complete

### S1. Future Analytics Scope Creep (LOW PRIORITY)
**Decision:** Reject - Disagree
**Reasoning:** Misunderstanding of document organization. Everything in specs/future-analytics is explicitly out of scope for current release.
**Status:** ✅ Complete

---

## Conflicts Resolved

### C1. Agent Architecture Complexity
**Decision:** Reject - Disagree
**Reasoning:** Conflict was misunderstanding - Gemini suggested QA agents for transcription, which system doesn't do.
**Status:** ✅ Complete

### C2. State Management Approach
**Decision:** Reject - Disagree
**Reasoning:** Will work with designed state management framework. Reassess if future issues arise.
**Status:** ✅ Complete

### C3. Context Window Handling
**Decision:** Reject - Disagree
**Reasoning:** Transcripts won't approach model context windows. Each transcript-processing agent gets clean context.
**Status:** ✅ Complete

### C4. MVP Definition
**Decision:** Reject - Disagree
**Reasoning:** Phases defined to deliver useful, functioning system at completion. MVP is simply first phase completion.
**Status:** ✅ Complete

### High Priority Issues (10 total)
- [x] A1. Complexity vs. Value Mismatch
- [x] A5. Automation Goals Clash with Interactive Workflows  
- [x] R1. Missing Testability for Key Requirements
- [x] R4. No MVP Definition
- [x] R5. Undefined Task Interfaces
- [x] D1. Shared Data Store Schema Evolution
- [x] D3. Under-specified for Durability and Analytics
- [x] T1. CSS Selector Brittleness
- [x] T3. Context Window Management
- [x] P3. QA/Metrics/Telemetry Storage Missing

### Medium Priority Issues (16 total)
- [x] A2. Agent Proliferation
- [x] A3. Task Separation Creates Coordination Overhead
- [x] A4. Orchestration vs. Choreography Trade-offs
- [x] R2. Phase Dependencies Unclear
- [x] D2. State Inference is Fragile
- [x] D4. Time/Track Data Not Normalized
- [x] D5. GitHub Issue Links Insufficient
- [x] D6. Speaker Diarization Consistency
- [x] T2. yt_dlp Dependency Risk
- [x] T4. Extraction Workflow Inefficiency
- [x] T5. No Caching or Change Detection
- [x] P1. Testing Strategy Gaps
- [x] P2. No Agentic Error Correction
- [x] P4. Missing Operational Documentation
- [x] DOC2. Agent Failure Protocols Missing
- [x] S2. Foundation Insufficient for Future Analytics

### Low Priority Issues (5 total)
- [x] R3. Conflicting Requirements
- [x] T6. Cost Estimation Accuracy
- [x] DOC1. Redundant Documentation
- [x] DOC3. Prompt Engineering Gaps
- [x] S1. Future Analytics Scope Creep

---

## Conflicts to Resolve

### C1. Agent Architecture Complexity
**Status:** ✅ Resolved - Reject - Disagree
**Reviewers:** Claude Opus (simplify), Gemini Pro (add QC agent)
**Decision:** Conflict was misunderstanding - Gemini suggested QA agents for transcription, which system doesn't do

### C2. State Management Approach  
**Status:** ✅ Resolved - Reject - Disagree
**Reviewers:** Claude Opus (status fields), GPT Codex (journaling), Gemini Pro (durable framework)
**Decision:** Will work with designed state management framework. Reassess if future issues arise

### C3. Context Window Handling
**Status:** ✅ Resolved - Reject - Disagree
**Reviewers:** Gemini Pro (hierarchical), GPT Codex (timestamps)
**Decision:** Transcripts won't approach model context windows. Each agent gets clean context

### C4. MVP Definition
**Status:** ✅ Resolved - Reject - Disagree
**Reviewers:** Claude Opus (Phase 3), GPT Codex (Phase 1 focus)
**Decision:** Phases defined to deliver useful system at completion. MVP is first phase completion

---

## Documents Requiring Updates

### Immediate Updates (Accept & Resolve Now)
- **A5**: Update requirements and implementation context - clarify "user selectable" means data store configuration, not interactive UI
- **R1**: Update requirement 3.2 (remove "intelligent decisions"), 11.4 (clarify priming), 12.4 (specify frequency algorithm)
- **D2**: Clarify missing vs null field semantics in data model documentation
- **P4**: Add operational documentation requirements (deployment, monitoring, recovery, configuration)
- **R3**: Clarify no user input during runs, all input via shared data store
- **DOC1**: Add documentation consistency requirements tested at end of each phase

### Future Phase Documentation (Accept & Defer)
- **Phase 1 Design**: Task interfaces (R5), Data model planning (D1)
- **Phase 2 Design**: AI agent testing strategy (P1)
- **Phase 3 Design**: yt_dlp fallback strategy (T2), Contract testing for data store (P1)
- **Phase 4 Design**: Extraction QA deterministic validation (A2), QA confidence system testing (P1)
- **Phase 5 Design**: CSS selector brittleness (T1), QA/troubleshooting agent consolidation (A2), Monitoring/recovery requirements (P4)
- **Phase 6 Design**: GitHub issue structure (D5), GitHub integration testing (P1)
- **Phase 7.2 Design**: Conference classifier validation (A2)
- **Phase 7.4 Design**: Speaker diarization consistency (D6)
- **Phase 8 Design**: QA metrics and telemetry storage (P3), Testing AI agents (P1)
- **Future Analytics Ideas**: Time normalization enrichment job (D4)

---

## Summary Statistics

- **Total Decisions Made:** 30/30 (26 issues + 4 conflicts)
- **Accept & Resolve Now:** 6
- **Accept & Defer:** 12  
- **Reject - Disagree:** 11
- **Reject - Out of Scope:** 1
- **Conflicts Resolved:** 4/4
