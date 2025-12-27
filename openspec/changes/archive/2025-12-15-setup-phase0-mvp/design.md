## Context

Phase 0 establishes the foundational infrastructure for FlowScope's observational architecture. This phase requires setting up Marquez locally and creating example code that emits OpenLineage events. The goal is to prove that the observational pipeline works end-to-end before building any analysis capabilities.

**Stakeholders**: Development team, future users of FlowScope
**Constraints**: 
- Must run locally on personal development machines
- Must use Docker Compose for Marquez deployment (per project conventions)
- Must demonstrate complete lineage chains (job → dataset → job)

## Goals / Non-Goals

### Goals
- Deploy Marquez locally via Docker Compose
- Create working examples of OpenLineage event emission
- Verify lineage visualization in Marquez UI
- Establish minimal project structure for future phases

### Non-Goals
- Building FlowScope analysis capabilities (Phase 1+)
- Creating production-ready ETL/API code (examples only)
- Custom UI development (reuse Marquez UI)
- Database schema design for FlowScope (Phase 1)

## Decisions

### Decision: Marquez Version and Deployment
**What**: Use latest stable Marquez version compatible with OpenLineage specification, deployed via Docker Compose.

**Why**: 
- Docker Compose aligns with project conventions for local development
- Latest stable version ensures compatibility with OpenLineage spec
- Local deployment supports the "local-first" principle

**Alternatives considered**:
- Marquez cloud deployment: Rejected - violates local-first principle and adds external dependency
- Other lineage tools (DataHub, OpenMetadata): Rejected - Marquez is specified in project plan and aligns with OpenLineage standard

### Decision: Example ETL/API Structure
**What**: Create 1-2 simple Python scripts that demonstrate:
- Job execution with OpenLineage events (JobRunStateChange)
- Dataset creation/consumption events
- Complete lineage chain (job → dataset → job)

**Why**:
- Python aligns with project tech stack (FastAPI backend planned)
- Simple examples prove the concept without complexity
- Demonstrates both ETL and API use cases

**Alternatives considered**:
- More complex examples: Rejected - Phase 0 is about proving the pipeline works, not building production code
- Multiple languages: Rejected - Python is sufficient for MVP, keeps focus narrow

### Decision: Project Structure
**What**: Minimal structure with:
- `docker-compose.yml` for Marquez services
- `examples/` directory for sample ETL/API code
- `README.md` with setup instructions

**Why**:
- Minimal structure keeps Phase 0 focused on proving the concept
- Clear separation of infrastructure (docker-compose) and examples
- Documentation ensures reproducibility

**Alternatives considered**:
- Full project structure: Rejected - premature, Phase 0 is MVP only
- No structure: Rejected - need organization for future phases

## Risks / Trade-offs

### Risk: Marquez Version Compatibility
**Risk**: Marquez version may not be compatible with OpenLineage specification version used in examples.

**Mitigation**: 
- Use documented compatible versions from Marquez/OpenLineage documentation
- Test event emission and visualization during implementation
- Document version requirements in README

### Risk: Docker Resource Usage
**Risk**: Marquez Docker Compose setup may consume significant resources on development machines.

**Mitigation**:
- Document resource requirements in README
- Use lightweight Marquez configuration
- Provide guidance on resource allocation

### Risk: Example Complexity
**Risk**: Examples may be too simple to demonstrate real-world lineage patterns.

**Mitigation**:
- Focus on proving the pipeline works, not production patterns
- Ensure examples show complete lineage chains (job → dataset → job)
- Phase 1+ will handle more complex scenarios

## Migration Plan

**N/A** - This is the initial capability, no migration needed.

## Open Questions

- What specific Marquez version should be used? (To be determined during implementation, check latest stable)
- What ports should Marquez services use? (Default Marquez ports, document in README)
- Should examples use real data sources or mock data? (Mock data sufficient for Phase 0)
