## ADDED Requirements

### Requirement: Orphan Dataset Detection
The system SHALL identify datasets with no upstream or downstream connections as orphan candidates.

#### Scenario: Detect orphan datasets
- **WHEN** redundancy detection service runs
- **THEN** all datasets with no upstream AND no downstream connections are identified
- **AND** orphan datasets are marked as candidates for deletion
- **AND** orphan datasets are returned via API endpoint

#### Scenario: Orphan detection API endpoint
- **WHEN** API receives request for orphan datasets
- **THEN** list of orphan datasets is returned
- **AND** each orphan dataset includes metadata (namespace, name, layer, system, owner)
- **AND** orphan datasets are marked as deletion candidates (require human review)

#### Scenario: Exclude datasets with connections
- **WHEN** redundancy detection service runs
- **THEN** datasets with at least one upstream OR downstream connection are excluded
- **AND** only truly isolated datasets are identified as orphans

### Requirement: Duplicate Table Identification
The system SHALL identify duplicate intermediate table candidates based on name similarity, layer matching, and path overlap.

#### Scenario: Identify duplicate tables
- **WHEN** redundancy detection service runs
- **THEN** tables with similar names, same layer, and overlapping paths are identified
- **AND** duplicate candidates are marked for potential merging
- **AND** duplicate candidates are returned via API endpoint

#### Scenario: Duplicate detection API endpoint
- **WHEN** API receives request for duplicate table candidates
- **THEN** list of duplicate candidate groups is returned
- **AND** each group contains tables that are potential duplicates
- **AND** each candidate includes similarity score and path overlap information
- **AND** duplicate candidates are marked as merge candidates (require human review)

#### Scenario: Similarity scoring for duplicates
- **WHEN** duplicate detection analyzes tables
- **THEN** name similarity is calculated (e.g., using string similarity algorithms)
- **AND** tables in the same layer are compared
- **AND** tables with overlapping upstream/downstream paths are identified
- **AND** similarity score reflects name similarity and path overlap

### Requirement: Refactoring Recommendations
The system SHALL provide refactoring recommendations based on complexity and redundancy analysis.

#### Scenario: Generate refactoring candidate list
- **WHEN** redundancy detection service runs
- **THEN** system generates a list of refactoring candidates
- **AND** candidates include orphan datasets (deletion candidates)
- **AND** candidates include duplicate tables (merge candidates)
- **AND** all recommendations require human review before action

#### Scenario: Refactoring recommendations include context
- **WHEN** refactoring candidates are returned
- **THEN** each candidate includes sufficient context for decision-making
- **AND** orphan datasets include metadata (layer, system, owner, creation date)
- **AND** duplicate candidates include similarity scores and path overlap details
- **AND** recommendations are actionable but require human confirmation












