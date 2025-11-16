# AMOS Development Fork Notice

## Repository Status
This is a **development fork** of the canonical MirrorDNA Protocol repository.

**Purpose**: This fork serves as a hardening and testing ground for protocol improvements while maintaining structural alignment with the canonical repository.

## Canonical Repository
- **Canonical URL**: https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA
- **Governance**: Master Citation v15.2
- **Protocol Version**: 1.0.0 (Beta)

## Fork Objectives
1. **Harden** protocol infrastructure (configuration, error handling, logging, security)
2. **Expand** automated test coverage for core protocol logic
3. **Add** CLI tools and scripts for common workflows
4. **Improve** developer experience for external contributors

## Merge-Back Policy
This fork maintains a **one-to-one structural mirror** with the canonical repository:
- ✅ All top-level folders and canonical files preserved
- ✅ vault_id, glyphsig, and protocol headers unchanged
- ✅ Additive changes preferred over destructive refactors
- ✅ Git history preserved (no rewrites)
- ✅ All changes documented in CHANGELOG_AMOS.md

## Change Tracking
All AMOS-specific improvements are logged in:
- **CHANGELOG_AMOS.md** - Detailed change log with merge-back notes
- **Git commits** - Descriptive commit messages with rationale

## Development Branch
All AMOS development occurs on feature branches starting with `claude/` to maintain clean separation from canonical main branch.

## Contact & Questions
For questions about this development fork or merge-back coordination, please reference the commit history and CHANGELOG_AMOS.md for context.

---
**Last Updated**: 2025-11-16
**AMOS Dev Twin**: Active
