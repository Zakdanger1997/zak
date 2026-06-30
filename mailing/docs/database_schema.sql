-- Mailing Outreach System - Database Schema
-- Run this in PostgreSQL before importing n8n workflows

CREATE TABLE IF NOT EXISTS contacts (
    id              SERIAL PRIMARY KEY,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    email           VARCHAR(255) UNIQUE NOT NULL,
    company         VARCHAR(255),
    title           VARCHAR(255),
    phone           VARCHAR(50),
    source          VARCHAR(100) DEFAULT 'manual',  -- 'apollo', 'traceparts', 'manual'

    -- Outreach status
    status          VARCHAR(50) DEFAULT 'new',
    -- Values: new | emailed | replied | no_response | call_done | closed

    follow_up_count INTEGER DEFAULT 0,
    last_email_sent_at  TIMESTAMPTZ,
    replied         BOOLEAN DEFAULT FALSE,
    replied_at      TIMESTAMPTZ,

    -- Call tracking (personal follow-up)
    needs_call      BOOLEAN DEFAULT FALSE,
    call_done       BOOLEAN DEFAULT FALSE,
    call_done_at    TIMESTAMPTZ,
    notes           TEXT DEFAULT '',

    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast status queries
CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(LOWER(email));
CREATE INDEX IF NOT EXISTS idx_contacts_needs_call ON contacts(needs_call, call_done);
CREATE INDEX IF NOT EXISTS idx_contacts_last_email ON contacts(last_email_sent_at);

-- Optional: email log table to track every email sent
CREATE TABLE IF NOT EXISTS email_log (
    id              SERIAL PRIMARY KEY,
    contact_id      INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    email_type      VARCHAR(50),  -- initial | followup1 | followup2 | followup3
    subject         TEXT,
    sent_at         TIMESTAMPTZ DEFAULT NOW(),
    status          VARCHAR(20) DEFAULT 'sent'  -- sent | bounced | failed
);

CREATE INDEX IF NOT EXISTS idx_email_log_contact ON email_log(contact_id);
