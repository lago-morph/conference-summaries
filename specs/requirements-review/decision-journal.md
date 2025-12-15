# Decision Journal

**⚠️ ONE-TIME TASK DOCUMENTATION - DO NOT READ FOR CONTEXT**
*This journal captures all decisions made during the December 2024 requirements review process. Future AI agents should ignore this file.*

## Review Process Status

**Current Phase:** Phase 3 - Systematic Review Process
**Issues to Review:** 26 total
**Decisions Made:** 2
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

## DECISION INPUT SECTION
*Fill in your decisions below, then I'll process them into the formal log*

### Other decisions that should be added and addressed

#### Need more phases
As an update to the decision for A1, we should explicitly define in the phase list when we will be implementing the conference classifier (chosen as phase 7.2 below under decision A2), the transcript formatter (phase 7.4), the dense knowledge encoder (phase 7.8), and the summarizer (phase 7.6).

#### Need phase for introducing nosql database
We need a new phase, phase 11, where we migrate from a file-based to a nosql database for the shared state.  This is necessary to expose parallelism so we can have multiple tasks running at the same time.  Again, the orchestration and coordination of those tasks is outside of the scope of this project.  This phase may be done out of order, or never done at all.  It is only needed if we want to start running multiple tasks at once (for instance, we are performing task 2 on several conferenes at once, while a task 3 run is going on a totally different conference).

#### Need phase for controlling task scope
We need a new phase, phase 12, where we add optional arguments to task execution jobs that limit the scope of what they will work on.  The exact form of this will be determined when we do design for phase 12.  Some ideas are to filter by tags on talks, or to allow one run of task 2 or 3 to work on a single conference and ignore others.  This allows us to do a lot of high level capturing of conferences and conference talks, without then automatically doing follow-on processing.  This also allows us to take advantage of parallelism when we expose it with a nosql database.  This phase may be performed out of order - it can be done any time that I want to work on multiple conferences at the same time.  This may happen early in the process, it may happen never.


### R1. Missing Testability for Key Requirements (HIGH PRIORITY)
**Your Decision (1-5):** ___
both 1 and 2, for different recommendations.
**Your Reasoning:** ___
We should immediately update requirement 3.2 to remove the phrase "intelligent decisions".  We will instead say that troubleshooting is triggered when the information retrieved is either garbled (with criteria to be added during design time of phase 4), or zero length data is retrieved.  We should say this in a way that it is clear we will be more specific in design.  Requirement 11.4 should be clarified to say that we will require that conference classification is run so that models can be primed with prompts that may improve performance.  The testable attribute is that the summarizer, formatter, and deep context agents are never run without receiving a priming prompt from the classifier agent.  Remove anything related to justifying that further, we don't need to say why we are doing it beyond that it improves performance.  For requirement 12.4, be more specific by saying that checking frequency will be decreased every time an artifact is checked as ok, and that frequency increases whenever a artifact fails checks.  Capture somewhere that as part of the design process for phase 8 we will concretely specify this algorithm and the initial parameters for the algorithm.

### R4. No MVP Definition (HIGH PRIORITY)  
**Your Decision (1-5):** ___
3 reject
**Your Reasoning:** ___
The phased plan is explicitly designed to produce a system that provides value at the end of every phase.  That means that completing phase 1 results in a minimum viable product.  Since I am building this for myself primarily, I can decide when to stop because it meets my needs.  That might be after phase 1, or it might be after everything specified up to this point has been implemented and we still do more.

### R5. Undefined Task Interfaces (HIGH PRIORITY)
**Your Decision (1-5):** ___
2 accept/defer
**Your Reasoning:** ___
This is a very valid comment.  The task interfaces will have to be defined as part of the design of phase 1.  CLI/IPC contracts are just as important as things like defining the data schema (which also has to be done as part of the design of phase 1).

### D1. Shared Data Store Schema Evolution (HIGH PRIORITY)
**Your Decision (1-5):** ___
2
**Your Reasoning:** ___
It is true that some thought has to be done for the data model.  The idea though is that the data model will have enough information to do the tasks for the phase we are at during the implementation of that phase.  Additions  to the data model will be for new capabilities.  We need to do planning during phase 1 design to make sure that we take into consideration the needs for growth so that we don't have to make major changes during some phase.  If in a future phase we are forced to do a data migration, we can do a data migration at that time.  Because this is textual data the raw size is not as bad as if we were dealing with voice, image, or video data.


### D3. Under-specified for Durability and Analytics (HIGH PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
This model is stupid.  We explicitly state (where?) that we are implementing an abstract data layer, that we know that yaml is not scalable, and that we plan to move to a nosql database in the future.  The level of parallelism will be low, and the abstract data layer will allow us to move to higher-performance back-ends if we ever need to.

### T1. CSS Selector Brittleness (HIGH PRIORITY)
**Your Decision (1-5):** ___
2
**Your Reasoning:** ___
We will address this issue in its entirety during the design of phase 5, when we work on the troubleshooting agents.  We will have the option of pulling it forward to phase 1 or 3 if we find that the structure of the sched web pages differ for different conferences.

### T3. Context Window Management (HIGH PRIORITY)
**Your Decision (1-5):** ___
4
**Your Reasoning:** ___
The context windows of the models we are likely to use for processing transcripts is far larger than the presentation transcripts (e.g., Claude Sonnet at 200K, GPT-4o 128K, GPT-5.2 400K, Gemini models at 1M).  We will use a fresh context for each processing action.

### P3. QA/Metrics/Telemetry Storage Missing (HIGH PRIORITY)
**Your Decision (1-5):** ___
2
**Your Reasoning:** ___
Address design of metrics for QA agent in design for phase 8.  Note that the QA agent used during web data capture is run for every script execution.  The adaptive checking is just for the task 3 QA agent.  Consider the other recommendations as part of design for phase 8.  These are probably too specific for this point in the requirements/design process.

### A2. Agent Proliferation (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
2 future phase
**Your Reasoning:** ___
I think as we proceed through the phases we will learn what the proper level of abstraction is.  I don't want to make the decision to combine or simplify the design now, when some of these recommendations don't take effect for a long time.  We should add this as a question that has to be asked during the relevant phases.  We will move the decision on if we should combine the QA and troubleshooting agents to the design part of phase 5 where we implement the troubleshooting agents.  We will look at if the extraction QA agent should be deterministic code to the design of phase 4.  we will move the decision on classifier validation to a new phase we will call phase 7.2, which is where we implement the classifier (we don't have a phase for that right now).  We should update the documents that refer to phases and use the numbers to incorporate that phase 7.2 if where we implement the conference classifier.  Note that we define several other phases as well above in the extra decisions section.

### A3. Task Separation Creates Coordination Overhead (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
3 reject.
**Your Reasoning:** ___
This is clearly a misunderstanding of the intent.  The intent is to have the tasks, when run, go try to find work to do, and if they find it, they do it.  This allows a gradual accumulation of increasingly detailed information.  For instance, just the conferences and talk titles is valuable information, even before we grab transcripts or do further processing.  I want the flexibility to go and grab a bunch of high level conferences, and do incremental work on those, while I'm chugging away at task 3.  A lot of the benefit will come from an orchestration layer that is out of scope for this project.  By the way, checkpoints completely miss the point - the tasks are constantly checkpointing themselves by saving the work they do.  If they are interrupted, they naturally go back to where they were and continue work, no need for an explicit checkpoint.

### A4. Orchestration vs. Choreography Trade-offs (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
3 reject
**Your Reasoning:** ___
Yes, it is orchestrator heavy.  But that's the point.  When we move to a nosql data layer we will expose arbitrary parallelism, which removes any bottlenecks.  We do need a way to prioritize work and/or break up work to expose parallelism.  I will add that above in the extra decisions section.

### R2. Phase Dependencies Unclear (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
They interpreted the dependency incorrectly.  This is not necessary.


### D2. State Inference is Fragile (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
1
**Your Reasoning:** ___
Clarify that missing means not processed, and null means processed but empty.  As of now, tasks are granular enough that we do not need to save partially completed work for a single field.  If there is an issue when we are half-done, then we leave the field missing.

### D4. Time/Track Data Not Normalized (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
2
**Your Reasoning:** ___
We should capture local time.  At some point in the future we can add an enrichment job that just goes through each conference, figures out what the local time was in relation to GMT, and normalizes the time.  However, this doesn't need to be implemented until we are trying to do analytics or something.  So push this off to something that we should consider when we do the future analytics.  Do not add it to the requirements there, just put this in a file called todo.md or ideas.md or something in that spec folder so it doesn't get lost.  But this is super-low priority, as I don't anticipate ever having to correlate the exact time two presentations are happening relative to each other in different time zones.

### D5. GitHub Issue Links Insufficient (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
parially 2, mostly 3
**Your Reasoning:** ___
It makes sense to replace the link with a structured field.  However, I think they are taking this a little too far.  We will determine what needs to be in that structured field when we do design for phase 6.

### D6. Speaker Diarization Consistency (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
2
**Your Reasoning:** ___
Defer this until we get to the design of the phase where we are implementing the formatter agent (I believe phase 7.4)

### T2. yt_dlp Dependency Risk (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
2
**Your Reasoning:** ___
Move to design of phase 3.  Record that we have a viable alternative in using the youtube API.

### T4. Extraction Workflow Inefficiency (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
This is such a tiny optimization.  I actually think it totally misunderstood the flow.  There is no track filtering, we are just extracting which track a given presentation is in by looking at a URL.  The data is already fetched, as we get the full page for each presentation.  This is just silly.

### T5. No Caching or Change Detection (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
Such small details.  This is an overoptimization of an implementation detail, not an architecture issue.  I guess I used the wrong model (Codex) from OpenAI.

### P1. Testing Strategy Gaps (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
2
**Your Reasoning:** ___
This is a really good catch.  We should add in two notes.  For phase 2, where we first implement any type of AI agent, we should as part of design specify the testing strategy for just the one AI agent we are implementing.  Because it is simple, this will be low effort and we will learn a lot specifying something straightforward.  In phase 4 design we should specify how we test the QA confidence system and the more technical things like mock strategies and snapshot testing.  In phase 6 design we should address how to test the github issue integration.  Lets add contract testing for the shared data store as part of phase 3.  Any other part of this suggestion that I missed (read the original one from the source Claude Opus section 5.2) we should schedule in the design part of the appropriate phase.

### P2. No Agentic Error Correction (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
Again, a total misunderstanding by Gemini.  We get transcripts that have already been produced by youtube, we don't generate transcripts ourselves.  We only reformat, summarize, or create dense representations of what we get.

### P4. Missing Operational Documentation (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
1
**Your Reasoning:** ___
concur.  We need requirements that state that at all times there must be up-to-date documentation for how to deploy and run the system and how to update configuration.  This should generate testable requirements that are tested at the end of every phase.  Add requirements for monitoring and recovering from failures, and associate them with design of phase 5 (this is when we start implementing troubleshooting, so logically fits there).

### DOC2. Agent Failure Protocols Missing (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
This is so low level.  I definitely used the wrong model.

### S2. Foundation Insufficient for Future Analytics (MEDIUM PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
I will save all raw source data, so they can be re-analyzed at a later date.  I'm not going to add a bunch of stuff I may never use.

### R3. Conflicting Requirements (LOW PRIORITY)
**Your Decision (1-5):** ___
1
**Your Reasoning:** ___
Need to clarify that there is no user input during a run.  Any input by the user is to the shared data store.  We do not yet have functionality to automatically flag talks, all talks are processed in the same way right now.

### T6. Cost Estimation Accuracy (LOW PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
The reviewer misinterpreted an example of a format of a document for actual data.

### DOC1. Redundant Documentation (LOW PRIORITY)
**Your Decision (1-5):** ___
1
**Your Reasoning:** ___
Need to somehow indicate in requirements that we will verify at the end of every phase that documentation is both up to date, self-consistent, and avoids redundancy.  This should probably be incorporated as one of the requirements we can test, and that we should test it at the end of every phase.

### DOC3. Prompt Engineering Gaps (LOW PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
Ugh, so specific.  So low level.  So not an appropriate issue at this level of review.  Probably not even relevant for the work I'm doing.

### S1. Future Analytics Scope Creep (LOW PRIORITY)
**Your Decision (1-5):** ___
3
**Your Reasoning:** ___
This is a misunderstanding of how the documents are organized.  Everything in spec/future-analytics is out of scope for the current release.  That's why they are in a different spec with the name "future" in it.

---

**DECISION KEY:**
1. Accept & Resolve Now - Address in current specs
2. Accept & Defer - Good idea, future phase  
3. Reject - Disagree - Don't agree with assessment
4. Reject - Out of Scope - Valid but outside boundaries
5. Skip for Now - Come back to this later

---

**CONFLICTS TO RESOLVE:**

### C1. Agent Architecture Complexity
**Your Decision:** ___
3
**Your Reasoning:** ___
The conflict was a misunderstanding - Gemini was suggesting QA agents for transcription, which is not even an action we are doing.

### C2. State Management Approach
**Your Decision:** ___
3
**Your Reasoning:** ___
I will work with the state management framework as designed.  If in the future there are issues, we will reasses.

### C3. Context Window Handling
**Your Decision:** ___
3
**Your Reasoning:** ___
None of our transcripts should be anywhere near the context windows of the agents we will be using.  Each transcript-processing agent will get a clean context window.  

### C4. MVP Definition
**Your Decision:** ___
3
**Your Reasoning:** ___
I have defined the phases to deliver a useful, functioning system at the end of the phase.  I do not need to specify an MVP, as it is just the first phase.

### High Priority Issues (10 total)
- [x] A1. Complexity vs. Value Mismatch
- [x] A5. Automation Goals Clash with Interactive Workflows  
- [ ] R1. Missing Testability for Key Requirements
- [ ] R4. No MVP Definition
- [ ] R5. Undefined Task Interfaces
- [ ] D1. Shared Data Store Schema Evolution
- [ ] D3. Under-specified for Durability and Analytics
- [ ] T1. CSS Selector Brittleness
- [ ] T3. Context Window Management
- [ ] P3. QA/Metrics/Telemetry Storage Missing

### Medium Priority Issues (12 total)
- [ ] A2. Agent Proliferation
- [ ] A3. Task Separation Creates Coordination Overhead
- [ ] A4. Orchestration vs. Choreography Trade-offs
- [ ] R2. Phase Dependencies Unclear
- [ ] D2. State Inference is Fragile
- [ ] D4. Time/Track Data Not Normalized
- [ ] D5. GitHub Issue Links Insufficient
- [ ] D6. Speaker Diarization Consistency
- [ ] T2. yt_dlp Dependency Risk
- [ ] T4. Extraction Workflow Inefficiency
- [ ] T5. No Caching or Change Detection
- [ ] P1. Testing Strategy Gaps
- [ ] P2. No Agentic Error Correction
- [ ] P4. Missing Operational Documentation
- [ ] DOC2. Agent Failure Protocols Missing
- [ ] S2. Foundation Insufficient for Future Analytics

### Low Priority Issues (4 total)
- [ ] R3. Conflicting Requirements
- [ ] T6. Cost Estimation Accuracy
- [ ] DOC1. Redundant Documentation
- [ ] DOC3. Prompt Engineering Gaps
- [ ] S1. Future Analytics Scope Creep

---

## Conflicts to Resolve

### C1. Agent Architecture Complexity
**Status:** Pending
**Reviewers:** Claude Opus (simplify), Gemini Pro (add QC agent)
**Decision:** TBD

### C2. State Management Approach  
**Status:** Pending
**Reviewers:** Claude Opus (status fields), GPT Codex (journaling), Gemini Pro (durable framework)
**Decision:** TBD

### C3. Context Window Handling
**Status:** Pending
**Reviewers:** Gemini Pro (hierarchical), GPT Codex (timestamps)
**Decision:** TBD

### C4. MVP Definition
**Status:** Pending
**Reviewers:** Claude Opus (Phase 3), GPT Codex (Phase 1 focus)
**Decision:** TBD

---

## Documents Requiring Updates

### Immediate Updates (Accept & Resolve Now)
- **A5**: Update requirements and implementation context documents to clarify "user selectable" means configuration via shared data store, not interactive UI

### Future Phase Documentation (Accept & Defer)
*Will be populated as decisions are made*

---

## Summary Statistics

- **Total Decisions Made:** 2/26
- **Accept & Resolve Now:** 1
- **Accept & Defer:** 0  
- **Reject - Disagree:** 1
- **Reject - Out of Scope:** 0
- **Conflicts Resolved:** 0/4
