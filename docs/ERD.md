# Entity Relationship Diagram (ERD)

## Database Schema

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ email (UK)      │
│ password_hash   │
│ role            │
│ mfa_enabled     │
│ mfa_secret      │
│ created_at      │
│ last_login_at   │
│ is_active       │
└────────┬────────┘
         │
         │ 1:N
         ├─────────────────┐
         │                 │
    ┌────▼────────┐   ┌───▼──────────┐
    │ audit_events│   │ artifacts    │
    ├─────────────┤   ├──────────────┤
    │ id (PK)     │   │ id (PK)      │
    │ actor_user  │   │ host_id (FK) │
    │ action      │   │ uploaded_by  │
    │ entity_type │   │ name         │
    │ entity_id   │   │ file_type    │
    │ ip_address  │   │ size_bytes   │
    │ created_at  │   │ uploaded_at  │
    │ metadata    │   │ file_path    │
    └─────────────┘   └──────────────┘
         │
         │ 1:N
         │
    ┌────▼──────────────┐
    │metrics_snapshots  │
    ├───────────────────┤
    │ id (PK)           │
    │ host_id (FK)      │
    │ collected_by (FK) │
    │ collected_at      │
    │ data (JSON)       │
    │ source            │
    │ ttl_expires_at    │
    └──────────────────┘

┌──────────────────┐
│      hosts       │
├──────────────────┤
│ id (PK)          │
│ hostname (IDX)   │
│ fqdn             │
│ ip (IDX)         │
│ os               │
│ environment      │
│ owner            │
│ team             │
│ criticality      │
│ tags (M:N ref)  │
│ notes            │
│ connection_type  │
│ smb_template     │
│ ssh_template     │
│ bastion_host     │
│ bastion_port     │
│ created_at       │
│ updated_at       │
│ last_seen        │
└────────┬─────────┘
         │
         │ 1:N
         ├─────────────────┐
         │                 │
    ┌────▼────────┐   ┌───▼──────────┐
    │ artifacts   │   │metrics_snaps │
    └─────────────┘   └──────────────┘

┌─────────────────┐
│  host_tags      │
├─────────────────┤
│ host_id (FK)    │
│ tag             │
│ (PK: both)      │
└─────────────────┘

┌─────────────────┐
│    settings     │
├─────────────────┤
│ id (PK)         │
│ key (UK)        │
│ value (JSON)    │
│ updated_at      │
└─────────────────┘
```

## Relationships

### users → audit_events
- Type: 1:N
- Foreign Key: `actor_user_id`
- Cascade: No delete (preserve history)

### users → artifacts
- Type: 1:N
- Foreign Key: `uploaded_by_user_id`
- Cascade: No delete

### users → metrics_snapshots
- Type: 1:N
- Foreign Key: `collected_by_user_id`
- Cascade: No delete

### hosts → artifacts
- Type: 1:N
- Foreign Key: `host_id`
- Cascade: Delete artifacts when host deleted

### hosts → metrics_snapshots
- Type: 1:N
- Foreign Key: `host_id`
- Cascade: Delete metrics when host deleted

### hosts → host_tags (M:N)
- Junction Table: `host_tags`
- Allows multiple tags per host
- Cascade: Delete tags when host deleted

## Indexes

| Table | Column | Type | Reason |
|-------|--------|------|--------|
| users | email | UNIQUE | Fast login lookups |
| hosts | hostname | BTREE | Search/filter |
| hosts | ip | BTREE | Lookup by IP |
| artifacts | host_id | BTREE | List by host |
| audit_events | action | BTREE | Filter by event type |
| audit_events | actor_user_id | BTREE | User activity tracking |
| audit_events | created_at | BTREE | Time-range queries |
| metrics_snapshots | host_id | BTREE | Latest metrics |
| metrics_snapshots | ttl_expires_at | BTREE | TTL cleanup |
| settings | key | UNIQUE | Configuration lookup |

## Cascade Behaviors

- **Host Deletion**: Artifacts and metrics deleted
- **User Deletion**: Audit events preserved (historical), uploads/metrics unassigned
- **Tag Deletion**: Only removed from association table
