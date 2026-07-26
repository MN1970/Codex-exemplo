# MAESTRO Disaster Recovery Procedures v6.0

**Document Version:** 1.0  
**Effective Date:** 2026-07-26  
**Owner:** Infrastructure & Disaster Recovery Team  
**Last Tested:** [To be updated after first DR drill]

---

## Recovery Objectives

| Objective | Target | Notes |
|-----------|--------|-------|
| **RTO (Recovery Time Objective)** | 4 hours | Time to restore full system and resume operations |
| **RPO (Recovery Point Objective)** | 1 hour | Maximum acceptable data loss (most recent backup every hour) |
| **Backup Frequency** | Hourly | Full database backup + continuous WAL archiving |
| **Backup Retention** | 30 days | Full backups retained 30 days, WAL 7 days |
| **Test Frequency** | Quarterly | Full DR drill every 3 months |
| **Failover Type** | Active-Standby | Hot standby in secondary region ready to promote |

---

## Disaster Scenarios Covered

1. **Database total loss** - Primary database corrupted/destroyed
2. **Application total loss** - All app servers down
3. **Agent pool loss** - All agents in a region down
4. **Network partition** - Cannot reach primary region
5. **Data corruption** - Database integrity compromised but not destroyed
6. **Ransomware attack** - Data encrypted, need clean restore
7. **Human error** - Accidental deletion or misconfiguration

---

## Recovery Architecture

### Backup Components

1. **Database Backups:**
   - Type: Full logical backup (pg_dump) + physical backup (pg_basebackup)
   - Frequency: Hourly full backup, continuous WAL streaming
   - Storage: S3 (us-west-2, different region from primary)
   - Encryption: AES-256 at rest, TLS in transit

2. **Configuration Backups:**
   - Components: PostgreSQL config, application secrets, Kubernetes manifests
   - Storage: Git repository (encrypted secrets via sealed-secrets)
   - Frequency: On every change

3. **Application State:**
   - What: Workflow execution state, agent status, task metadata
   - Where: Database (included in DB backup)
   - Frequency: Continuous (transaction log archiving)

4. **Standby Database:**
   - Type: PostgreSQL streaming replication
   - Location: Secondary region (us-west-2)
   - Lag: < 1 second
   - Promotion: 5 minutes automated or manual promotion

---

## Full System Restoration

### Phase 1: Pre-Recovery Assessment (30 minutes)

**Steps:**

1. Declare disaster recovery activation
2. Assess primary system failure (is it really down?)
3. Confirm backup validity (are backups recent?)
4. Verify standby database status (if using replication)
5. Decision gate: Use standby or restore from backup?

### Phase 2: Standby Promotion (5-30 minutes)

If standby database is healthy and replication lag acceptable:

1. Stop replication and promote standby to primary
2. Update application connection strings to point to new primary
3. Trigger rolling restart of app pods
4. Verify application connectivity
5. Validate data integrity with spot checks

### Phase 3: Full Database Restore from Backup (30-120 minutes)

If standby is not available or backup restore required:

1. Obtain latest backup from S3
2. Prepare recovery database (use standby or create new RDS instance)
3. Restore database from backup file
4. Apply WAL archives for point-in-time recovery
5. Verify data integrity
6. Update application connection strings
7. Monitor restoration progress

---

## Data Integrity Verification

After recovery, validate data integrity:

```sql
-- Check record counts match expected
SELECT COUNT(*) FROM maestro.workflows;
SELECT COUNT(*) FROM maestro.tasks;
SELECT COUNT(*) FROM maestro.consensus_polls;

-- Verify recent data is present
SELECT created_at FROM maestro.workflows ORDER BY created_at DESC LIMIT 1;

-- Check for corruption
SELECT * FROM maestro.workflows WHERE created_at < NOW() - INTERVAL '24 hours' LIMIT 5;

-- Verify agent status
SELECT * FROM maestro.agent_status;
```

---

## Testing & Validation

### Pre-Recovery Checks

- [ ] Backup files exist and are recent (<1 hour old)
- [ ] Standby database is in good health
- [ ] WAL archives are available and complete
- [ ] Replication lag is acceptable (<1 hour)

### Post-Recovery Validation

- [ ] Database is accepting connections
- [ ] Application can connect to database
- [ ] All tables exist and have data
- [ ] Record counts match expectations
- [ ] Recent workflows are visible
- [ ] Agents show healthy status
- [ ] No corruption detected

### End-to-End Test

- [ ] Spin up test instance from latest backup
- [ ] Restore to test database
- [ ] Run application against test database
- [ ] Execute test workflow
- [ ] Verify workflow completes successfully

---

## DR Drill Schedule

- **Monthly (light):** Test backup restoration on non-prod environment
- **Quarterly (full):** Execute complete failover to standby and back
- **Annually (extended):** Test recovery from 7-day-old backup

---

## Escalation

- **Tier 1:** Infrastructure Team (first contact)
- **Tier 2:** Database Engineer (if DB-specific issues)
- **Tier 3:** VP Engineering (if multi-hour RTO unavoidable)
- **Tier 4:** CTO (if data loss or corruption)

**Support Contact:** dba@maestro.internal

---

## Post-Recovery Steps

1. **Notify stakeholders** that system is recovering
2. **Update status page** with ETA
3. **Document what happened** in incident log
4. **Run data integrity checks** before resuming normal operations
5. **Monitor system closely** for 24 hours post-recovery
6. **Schedule postmortem** within 24 hours
7. **Verify all applications** are functioning correctly
8. **Archive recovery logs** for future reference

---

**Document Status:** Production Ready  
**Last Updated:** 2026-07-26  
**Next Review:** 2026-10-26 (quarterly)

For complete procedures, contact: dba@maestro.internal
