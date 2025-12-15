# Requirements and Design Context

> **📋 WHEN TO READ THIS**: Read this document during requirements gathering and design phases. It captures strategic decisions, user context, and project constraints that inform system design. Not needed for general startup or implementation tasks.

This document captures the strategic context, user requirements, and design decisions that shaped the conference data extraction system.

## Major Architectural Decisions (December 2024)

### Task-Based Architecture
**Decision**: Split monolithic pipeline into 4 independent, manually-triggered tasks
**Rationale**: 
- Separate web scraping (Tasks 1-2) from AI processing (Task 3) for resource optimization
- Enable incremental processing and flexible execution order
- Allow partial dataset processing (e.g., Task 3 on incomplete Task 2 data)
- Support different infrastructure for different task types

### Shared Data Store Communication
**Decision**: All task communication through centralized data store only
**Rationale**:
- No inter-task dependencies beyond data availability
- Idempotent operations with resumable processing
- State inference through missing/null fields (missing = not processed, null = processed but empty)
- Future-proof for file-to-NoSQL migration
- All user configuration via shared data store between batch runs, not interactive UI

### GitHub Issue Integration
**Decision**: Automatic issue creation with processing suspension
**Rationale**:
- Prevent wasted resources on known failing cases
- Automated escalation when troubleshooting fails
- Self-healing system when issues are resolved
- Granular issue tracking at conference/presentation/processing levels

### Phased Implementation Strategy
**Decision**: 16 incremental phases from foundation to full AI sophistication
**Rationale**:
- Deliver immediate value with Phase 1 (working conference extraction)
- Learn from early phases to inform later requirements
- Avoid designing for requirements that may change
- Build on validated foundations incrementally

### Agent Priming Strategy
**Decision**: Conference classification must complete before all other Task 3 AI agents
**Rationale**:
- Domain-specific context improves AI processing quality across all agents
- Consistent priming ensures optimal performance even with lightweight models
- Non-negotiable timing requirement prevents suboptimal processing
- Enables cost-effective model selection through enhanced context

## Project Goals and Use Cases

### Primary Objective
Create an automated system to extract comprehensive presentation data from CNCF KubeCon conferences hosted on Sched.com websites for post-conference analysis and research.

### User's Intended Use Cases
- **Conference Analysis**: Analyze presentation topics, speaker patterns, and track distributions
- **Research Data**: Create datasets for studying cloud native ecosystem trends
- **Content Discovery**: Find relevant presentations and speakers across multiple conferences
- **Video/Slide Collection**: Systematically gather presentation materials for reference

### Success Criteria
- Extract 80-90% of presentations successfully (validated on 542 presentations)
- Handle special characters, emoji, and various content formats
- Process complete conference in ~5-6 minutes with respectful rate limiting
- Generate structured, machine-readable output (YAML format)

## Strategic Technical Decisions

### Data Format Choice: YAML
**Decision**: Store extracted data in YAML format
**Rationale**: 
- Human-readable for debugging and manual review
- Structured format suitable for further processing
- Easy to convert to JSON, CSV, or database formats later
- Handles Unicode/emoji characters well
**Future Consideration**: May change to JSON or direct database storage based on integration needs

### Rate Limiting: 100ms Between Requests
**Decision**: Minimum 100ms delay between HTTP requests
**Rationale**:
- Respectful to Sched.com servers (avoid overloading)
- Tested successfully with KubeCon 2025 (542 presentations)
- Balances extraction speed with server courtesy
- Allows for ~6 requests per second maximum
**Validation**: No rate limiting issues encountered during testing

### Target Scope: CNCF/KubeCon Initially
**Decision**: Focus on CNCF conferences first, specifically KubeCon events
**Rationale**:
- Consistent Sched.com implementation across CNCF events
- Large, well-structured conferences (500+ presentations)
- High-value content for cloud native community
- Proven extraction patterns can be validated before expansion
**Future Expansion**: Patterns should work for other Sched.com conferences

### Web Search Strategy: Multi-Engine Approach
**Decision**: Enhanced MCP server with DuckDuckGo, Bing, Google fallbacks
**Rationale**:
- Reduces dependency on single search provider
- Handles anti-bot measures through engine switching
- Free approach (no API keys required)
- Reliable conference URL discovery (100% success rate)

### Transcript Extraction: yt_dlp
**Decision**: Use yt_dlp instead of YouTube APIs for transcript extraction
**Rationale**:
- No API quota limitations
- More reliable transcript availability
- Handles various video platforms beyond YouTube
- Proven extraction capabilities from exploration phase

## User Constraints and Preferences

### Implementation Language Preference
**Stated Options**: Python or shell script
**Context**: User mentioned both as acceptable options
**Recommendation**: Python preferred for:
- Better HTML parsing libraries (BeautifulSoup, lxml)
- Robust HTTP handling (requests library)
- YAML processing capabilities
- Error handling and logging
- Cross-platform compatibility

### Deployment Environment
**Context**: Not explicitly specified
**Assumptions**: 
- Local execution (user's development machine)
- Windows environment (based on file paths observed)
- Node.js available (for MCP server)
**Consideration**: Should support cross-platform deployment

### Integration Requirements
**Current**: Standalone extraction system
**Future Considerations**:
- Integration with data analysis tools
- Database storage capabilities
- API endpoints for programmatic access
- Batch processing multiple conferences

## Performance and Scale Expectations

### Tested Scale
- **Single Conference**: 542 presentations (KubeCon 2025 North America)
- **Processing Time**: ~5.6 minutes total
- **Success Rate**: 80-90% extraction success
- **Data Volume**: ~500KB YAML output per conference

### Expected Scale
- **Multiple Conferences**: Process 5-10 conferences per year
- **Historical Data**: Potentially process past conferences
- **Growth**: Conference sizes may increase over time

### Performance Requirements
- **Reliability**: Graceful handling of missing data and network issues
- **Resumability**: Ability to resume interrupted extractions
- **Progress Tracking**: User feedback during long extractions
- **Error Reporting**: Clear reporting of failed extractions

## Quality and Reliability Requirements

### Data Quality Standards
- **Completeness**: Extract all available metadata fields
- **Accuracy**: Preserve original formatting, especially for titles and names
- **Consistency**: Standardized date/time formats across presentations
- **Unicode Support**: Full emoji and special character preservation

### Error Handling Requirements
- **Network Resilience**: Handle timeouts, connection failures
- **Content Variations**: Adapt to missing speakers, videos, or files
- **Rate Limiting**: Respect server limits and implement backoff
- **Validation**: Verify extracted data completeness and format

### User Experience Requirements
- **Progress Feedback**: Show extraction progress for long operations
- **Track Filtering**: Allow users to exclude unwanted presentation categories via shared data store configuration
- **Output Options**: Flexible output formats and locations
- **Error Recovery**: Clear guidance when extractions fail

### Operational Excellence Requirements
- **Documentation Consistency**: Automated validation of documentation completeness and accuracy
- **Deployment Documentation**: Up-to-date installation, configuration, and dependency documentation
- **Monitoring and Recovery**: Comprehensive failure detection and recovery procedures
- **Configuration Management**: Clear documentation of all settings and their effects
- **Testable Operations**: All operational procedures must be validated at phase completion

## Future Evolution Considerations

### Potential Expansions
1. **Conference Types**: Expand beyond CNCF to other Sched.com conferences
2. **Data Sources**: Support other conference platforms beyond Sched.com
3. **Output Formats**: JSON, CSV, database direct insertion
4. **Analysis Features**: Built-in data analysis and visualization
5. **API Integration**: RESTful API for programmatic access

### Technical Debt Considerations
- **CSS Selector Maintenance**: Selectors may need updates as Sched.com evolves
- **Rate Limiting Optimization**: May need adjustment based on server responses
- **Error Handling Enhancement**: More sophisticated retry and recovery logic
- **Performance Optimization**: Parallel processing for large conferences

### Maintenance Requirements
- **Regular Testing**: Validate extraction patterns with new conferences
- **Selector Updates**: Monitor and update CSS selectors as needed
- **Documentation Updates**: Keep implementation docs current with changes
- **User Feedback Integration**: Incorporate user experience improvements

## Decision Log

### Key Decisions Made During Exploration
1. **Multi-engine web search** - Implemented for reliability
2. **Track filtering system** - Presentation categories configurable via shared data store
3. **Emoji support** - Full Unicode handling implemented
4. **Sub-track hierarchy** - Support for nested track categories
5. **File type detection** - PDF, PPTX, PPT file extraction
6. **Video platform support** - YouTube primary, extensible to others

### Key Decisions Made During Requirements Review (December 2024)
1. **Enhanced Phase Structure** - Expanded from 10 to 16 phases with 6 new AI agent phases
2. **Agent Priming Strategy** - Conference classification mandatory before all Task 3 processing
3. **Requirements Testability** - Replaced vague criteria with specific, measurable requirements
4. **Operational Excellence** - Added comprehensive documentation and validation requirements
5. **State Semantics Clarification** - Missing vs null field meanings clearly defined
6. **User Configuration Approach** - All configuration via shared data store, no interactive UI

### Validation Results
- **Conference Discovery**: 100% success rate finding Sched.com URLs
- **Track Extraction**: 26 tracks identified including 4 with emoji
- **Presentation Extraction**: 4/5 test presentations successful
- **Special Character Handling**: Emoji and Unicode fully supported
- **Performance**: 5.6 minutes for 542 presentations acceptable

## System Architecture Overview

### 4-Task Structure
1. **Task 1**: Conference Discovery + Basic Metadata (light AI + light web scraping)
2. **Task 2**: Raw Data Extraction (light AI + heavy web scraping)
3. **Task 3**: AI Processing Pipeline (heavy AI + no web scraping)
4. **Task 4**: GitHub Issue Resolution Monitoring (API monitoring)

### Quality Assurance Strategy
- **Extraction QA Agent**: Algorithmic criteria for Tasks 1-2 (file sizes, log analysis)
- **Processing QA Agent**: Adaptive confidence scoring for Task 3 (content quality)
- **Dual Approach**: Different QA strategies for different task types

### A/B Testing Approach
- **Task-Specific Testing**: Test individual tasks with alternative configurations
- **Baseline Preservation**: Use existing processed records as "A" baseline
- **Manual Selection**: User selects subset of records for testing
- **Configuration Optimization**: Compare alternative task configurations against defaults

## Implementation Phases

### Complete 16-Phase Implementation Strategy

**Phase 1**: Foundation + Manual Task 1 (data store, basic extraction, manual URL input)
- Shared data store with abstracted access layer
- Manual Task 1 (user provides Sched.com URL)
- Basic extraction scripts without AI assistance
- Foundation for all subsequent phases

**Phase 2**: AI-Powered Task 1 (Conference Discovery Agent)
- AI-powered conference discovery from unstructured information
- Web search integration for Sched.com URL finding
- Automated URL validation and accessibility checking

**Phase 3**: Basic Task 2 (raw data extraction scripts only)
- Raw data extraction scripts for presentation details
- YouTube transcript extraction using yt_dlp
- Rate limiting and respectful scraping implementation

**Phase 4**: Task 1 + 2 QA Agents (extraction quality assurance)
- Extraction QA Agent with algorithmic criteria
- File size and log analysis for quality assessment
- Lightweight pass/fail/warn assessment per presentation

**Phase 5**: Troubleshooting Agents (for Tasks 1 + 2)
- Troubleshooting Agent for automatic issue resolution
- CSS selector failure detection and alternative identification
- Network issue handling and retry strategy recommendations

**Phase 6**: GitHub Issue Integration (for Tasks 1 + 2)
- GitHub Issue Reporter Agent for unresolvable problems
- Automatic issue creation with detailed context
- Processing suspension for records with GitHub issue links

**Phase 7**: Basic Task 3 (AI processing without QA)
- Basic Task 3 framework and data flow setup
- Foundation for AI processing pipeline

**Phase 7.2**: Conference Classifier Implementation (priming agent for AI processing)
- Conference Classifier Agent that analyzes presentation titles and tracks
- Domain-specific context generation for all subsequent AI agents
- Technology focus identification and terminology extraction
- **Critical Timing**: Must complete before all other Task 3 AI agents

**Phase 7.4**: Transcript Formatter Implementation (speaker diarization consistency)
- Transcript Formatter Agent with human-readable formatting
- Speaker diarization consistency with structured JSON format
- Timestamp preservation and section-based organization

**Phase 7.6**: Summarizer Implementation (presentation summaries)
- Summarizer Agent with tiered processing (light and deep)
- Cost-effective model selection based on effort level
- Both quick decision-making summaries and comprehensive analysis

**Phase 7.8**: Dense Knowledge Encoder Implementation (dense representations)
- Dense Knowledge Encoder Agent for RAG-optimized summaries
- Compressed summaries suitable for semantic search
- Vector-friendly text generation for knowledge databases

**Phase 8**: Task 3 QA + Troubleshooting + GitHub
- Processing QA Agent with adaptive confidence scoring
- Quality assurance for AI processing outputs
- GitHub integration for AI processing issues

**Phase 9**: Task 4 (GitHub issue monitoring)
- Automated GitHub issue status monitoring
- Automatic link removal when issues are resolved
- Processing resumption for previously blocked records

**Phase 10**: A/B Testing System
- Task-specific A/B testing with alternative configurations
- Quality evaluation and impact assessment
- Configuration optimization based on comparison results

**Phase 11**: NoSQL Database Migration (parallelism support)
- Migration from file-based to NoSQL database
- Server-side concurrency management
- Multiple tasks running simultaneously on different conferences

**Phase 12**: Task Scope Control (optional execution arguments)
- Optional arguments to limit task execution scope
- Fine-grained control for specific use cases
- Support for parallel processing workflows

### Kiro Spec-Driven Development Integration
- Each phase follows complete requirements → design → tasks → implementation cycle
- Requirements marked with phase indicators for focused design sessions
- Avoid designing for requirements that may change in later phases
- Build incrementally on validated foundations

This context ensures future development phases have complete understanding of project goals, constraints, and validated technical approaches.