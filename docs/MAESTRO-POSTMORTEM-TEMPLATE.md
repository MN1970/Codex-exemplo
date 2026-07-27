# MAESTRO Post-Incident Review Template v6.0

This is a template for post-incident postmortems. After any P1 or P0 incident, complete this template within 24 hours.

**Key Sections:**
1. Incident Summary (basic info, severity, impact)
2. Impact Assessment (customer/business/metrics)
3. Timeline (chronological event log + narrative)
4. Root Cause Analysis (primary + contributing factors)
5. Lessons Learned (what went well, what could be better)
6. Action Items (preventive, detective, responsive)
7. Sign-Off & Approval

**Estimated Time to Complete:** 2-4 hours

---

## Quick Links

- **Incident Response Plan:** `docs/MAESTRO-INCIDENT-RESPONSE-PLAN.md`
- **Troubleshooting Procedures:** `docs/MAESTRO-TROUBLESHOOTING-PROCEDURES.md`
- **Evidence Collection:** `/incidents/[incident-id]/` directory

---

## Template Usage

1. **Copy this template** to `/incidents/[incident-id]/POSTMORTEM.md`
2. **Schedule postmortem meeting** within 24 hours of incident resolution
3. **Gather all evidence** (logs, metrics, snapshots, command history)
4. **Facilitate discussion** with incident response team
5. **Document findings** in template sections below
6. **Define action items** with clear owners and due dates
7. **Distribute postmortem** to all stakeholders
8. **Track action items** in GitHub Issues (link from postmortem)
9. **Follow-up meeting** 2 weeks post-incident to verify completion

---

## Key Principles

- **Blameless:** Focus on systems and processes, not individuals
- **Transparent:** Document honestly, including what we could have done better
- **Actionable:** Every lesson learned should result in at least one action item
- **Timely:** Complete within 24 hours while details are fresh
- **Shareable:** Postmortems are learning documents for the whole team

---

## Action Item Tracking

Link action items to GitHub Issues:

```bash
# Create tracking issue
gh issue create \
  --title "Postmortem Action: Add connection pool alert" \
  --body "From incident PM-2026-0726-001: Implement explicit DB connection pool alert when >80% utilized." \
  --label "infrastructure,monitoring" \
  --assignee jane-doe \
  --milestone "v6.0.2"

# Reference in postmortem
[Action P1: Add connection pool alert (#1234)](https://github.com/manta-associados/maestro-os/issues/1234)
```

---

## For More Details

See the template file at: `/docs/MAESTRO-POSTMORTEM-TEMPLATE.md`

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-26  
**Next Review:** 2026-10-26 (quarterly)
