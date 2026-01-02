<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | SOP-LYNX-001 |
| **Document Type** | SOP |
| **Classification** | STANDARD |
| **Title** | Standard Operating Procedures — LYNX AI |
| **Status** | DRAFT |
| **Authority** | DERIVED |
| **Scope** | OPERATIONS |
| **Derived From** | `PRD-LYNX-001`, `SRS-LYNX-001`, `TSD-LYNX-001` |
| **Version** | 1.0.0 |
| **Owners** | `DevOps Lead`, `Operations Manager` |
| **Created** | 2026-01-01 |
| **Updated** | 2026-01-01 |

<!-- END: AIBOS_MANAGED -->

# Standard Operating Procedures — LYNX AI

**Derived from:** PRD-LYNX-001, SRS-LYNX-001, TSD-LYNX-001  
**Status:** DRAFT

---

## 1. Introduction

### 1.1 Purpose

This Standard Operating Procedures (SOP) document defines **operational procedures** for Lynx AI, including:
- Deployment procedures
- Monitoring and alerting
- Incident response
- Maintenance procedures
- Backup and recovery

### 1.2 Scope

This SOP covers:
- Production deployment
- Monitoring and observability
- Incident management
- Maintenance windows
- Disaster recovery

---

## 2. Deployment Procedures

### 2.1 Pre-Deployment Checklist

**Before deploying Lynx AI:**

- [ ] All tests passing (unit, integration, E2E)
- [ ] Code review approved
- [ ] PRD-LYNX-001 compliance verified
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Rollback plan prepared

---

### 2.2 Deployment Steps

#### Step 1: Environment Preparation

```bash
# 1. Set environment variables
export OPENAI_API_KEY="sk-..."
export KERNEL_API_URL="https://kernel.nexuscanon.com/api"
export KERNEL_API_KEY="..."
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="..."

# 2. Verify dependencies
python --version  # Must be 3.10+
uv --version     # Or pip

# 3. Install dependencies
uv sync  # Or pip install -r requirements.txt
```

#### Step 2: Database Migration

```bash
# Run Supabase migrations for audit tables
supabase migration up
```

#### Step 3: Application Deployment

```bash
# Start Lynx AI service
uv run python -m lynx.main

# Or using systemd
systemctl start lynx-ai
```

#### Step 4: Health Check

```bash
# Verify service is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

---

### 2.3 Rollback Procedure

**If deployment fails:**

1. **Stop new service:**
   ```bash
   systemctl stop lynx-ai
   ```

2. **Restore previous version:**
   ```bash
   git checkout <previous-version>
   uv sync
   systemctl start lynx-ai
   ```

3. **Verify rollback:**
   ```bash
   curl http://localhost:8000/health
   ```

---

## 3. Monitoring & Alerting

### 3.1 Key Metrics to Monitor

#### 3.1.1 Application Metrics

- **Response Time:**
  - Domain MCP: < 2s (p95)
  - Cluster MCP: < 5s (p95)
  - Cell MCP: < 10s (p95)
  - LLM Response: < 30s (p95)

- **Throughput:**
  - Requests per minute
  - Tool calls per minute
  - Concurrent users

- **Error Rate:**
  - 4xx errors: < 1%
  - 5xx errors: < 0.1%

#### 3.1.2 Business Metrics

- **Lynx Runs:** Total interactions per day
- **Tool Usage:** Most used MCP tools
- **Approval Rate:** High-risk action approvals
- **Refusal Rate:** Blocked actions

#### 3.1.3 Infrastructure Metrics

- **CPU Usage:** < 70%
- **Memory Usage:** < 80%
- **Disk Usage:** < 80%
- **Network Latency:** < 100ms

---

### 3.2 Alerting Rules

#### Critical Alerts (Immediate Response)

- **Service Down:** Lynx AI service unavailable
- **High Error Rate:** > 5% 5xx errors
- **Audit Logging Failure:** Audit logs not being written
- **Tenant Isolation Breach:** Cross-tenant access detected

#### Warning Alerts (Investigate)

- **High Response Time:** p95 > threshold
- **High CPU/Memory:** > 80% usage
- **LLM API Failure:** OpenAI/Anthropic API errors
- **Kernel API Failure:** Kernel SSOT API errors

---

### 3.3 Monitoring Tools

**Recommended Stack:**
- **Application Metrics:** Prometheus + Grafana
- **Logs:** ELK Stack or CloudWatch
- **APM:** Datadog or New Relic
- **Uptime:** Pingdom or UptimeRobot

---

## 4. Incident Response

### 4.1 Incident Severity Levels

#### P0 - Critical (Immediate)
- Service completely down
- Data breach or security incident
- Audit logging completely failed

**Response Time:** < 15 minutes  
**Resolution Time:** < 1 hour

#### P1 - High (Urgent)
- Service degraded (> 50% errors)
- High-risk tool execution failing
- Kernel API integration broken

**Response Time:** < 1 hour  
**Resolution Time:** < 4 hours

#### P2 - Medium (Important)
- Performance degradation
- Non-critical tool failures
- Monitoring gaps

**Response Time:** < 4 hours  
**Resolution Time:** < 24 hours

#### P3 - Low (Normal)
- Minor bugs
- Documentation issues
- Feature requests

**Response Time:** < 24 hours  
**Resolution Time:** Next release

---

### 4.2 Incident Response Procedure

#### Step 1: Detection

1. Alert received (monitoring system)
2. Verify incident (check dashboards)
3. Classify severity (P0/P1/P2/P3)

#### Step 2: Response

1. **Acknowledge incident** (incident tracking system)
2. **Assemble team** (on-call engineer + lead)
3. **Investigate** (check logs, metrics, recent changes)
4. **Mitigate** (restart service, rollback, disable feature)

#### Step 3: Resolution

1. **Fix root cause**
2. **Verify fix** (monitoring, tests)
3. **Document incident** (post-mortem)
4. **Update runbooks** (if needed)

---

### 4.3 Common Incidents & Solutions

#### Incident: Service Down

**Symptoms:**
- Health check failing
- No response from API

**Investigation:**
```bash
# Check service status
systemctl status lynx-ai

# Check logs
tail -f /var/log/lynx/lynx.log

# Check resource usage
top
df -h
```

**Solutions:**
1. Restart service: `systemctl restart lynx-ai`
2. Check for OOM: Increase memory limits
3. Check for disk full: Clean logs, increase disk
4. Rollback if recent deployment

---

#### Incident: High Error Rate

**Symptoms:**
- > 5% 5xx errors
- Users reporting failures

**Investigation:**
```bash
# Check error logs
grep "ERROR" /var/log/lynx/lynx.log | tail -100

# Check specific errors
grep "PermissionError" /var/log/lynx/lynx.log
grep "KernelAPIError" /var/log/lynx/lynx.log
```

**Solutions:**
1. **Permission Errors:** Check Kernel API permissions
2. **Kernel API Errors:** Verify Kernel API availability
3. **LLM API Errors:** Check OpenAI/Anthropic API status
4. **Database Errors:** Check Supabase connectivity

---

#### Incident: Audit Logging Failure

**Symptoms:**
- Audit logs not appearing in database
- Audit API returning errors

**Investigation:**
```bash
# Check Supabase connection
curl https://xxx.supabase.co/rest/v1/audit_logs

# Check audit logger
grep "AuditLogger" /var/log/lynx/lynx.log
```

**Solutions:**
1. **Supabase Down:** Use fallback logging (file)
2. **Connection Issues:** Check network, credentials
3. **Rate Limiting:** Implement backoff/retry
4. **Schema Issues:** Run migrations

---

## 5. Maintenance Procedures

### 5.1 Regular Maintenance Tasks

#### Daily
- [ ] Review error logs
- [ ] Check monitoring dashboards
- [ ] Verify audit logging working

#### Weekly
- [ ] Review performance metrics
- [ ] Check disk space
- [ ] Review security alerts
- [ ] Update dependencies (if needed)

#### Monthly
- [ ] Review audit logs for anomalies
- [ ] Performance optimization review
- [ ] Security audit
- [ ] Capacity planning

---

### 5.2 Maintenance Windows

**Scheduled Maintenance:**
- **Time:** Sunday 2:00 AM - 4:00 AM UTC
- **Frequency:** Monthly (first Sunday)
- **Notification:** 7 days advance notice

**Maintenance Tasks:**
1. Database maintenance (vacuum, analyze)
2. Log rotation
3. Dependency updates
4. Security patches

---

## 6. Backup & Recovery

### 6.1 Backup Procedures

#### 6.1.1 Database Backups

**Audit Logs (Supabase):**
- **Frequency:** Daily
- **Retention:** 7 years (SOX compliance)
- **Method:** Supabase automated backups + manual exports

```bash
# Manual backup
supabase db dump -f backup-$(date +%Y%m%d).sql
```

#### 6.1.2 Configuration Backups

**Configuration Files:**
- **Frequency:** On every change
- **Retention:** 90 days
- **Method:** Git repository

```bash
# All configs in git
git add config/
git commit -m "Config backup"
```

---

### 6.2 Recovery Procedures

#### 6.2.1 Database Recovery

```bash
# Restore from backup
supabase db restore backup-20260101.sql
```

#### 6.2.2 Service Recovery

```bash
# Full service recovery
git checkout <last-known-good>
uv sync
systemctl restart lynx-ai
```

---

## 7. Security Procedures

### 7.1 Secret Management

**Secrets Storage:**
- Use environment variables (production)
- Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Never commit secrets to git

**Secret Rotation:**
- API keys: Rotate every 90 days
- Database credentials: Rotate every 180 days
- Review access logs monthly

---

### 7.2 Access Control

**Production Access:**
- Only authorized engineers
- Two-factor authentication required
- All access logged and audited

**API Access:**
- All requests authenticated
- Rate limiting enabled
- Tenant isolation enforced

---

## 8. Performance Tuning

### 8.1 Optimization Checklist

- [ ] LLM response caching (where appropriate)
- [ ] Database query optimization
- [ ] Connection pooling
- [ ] Async operation optimization
- [ ] Resource limits (CPU, memory)

---

## 9. References

- **PRD-LYNX-001** - Master PRD
- **SRS-LYNX-001** - Software Requirements
- **TSD-LYNX-001** - Technical Specification
- **IMPLEMENTATION-LYNX-001** - Implementation Plan

---

**End of SOP**

