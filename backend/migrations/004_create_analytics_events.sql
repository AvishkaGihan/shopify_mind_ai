-- ==============================================
-- ShopifyMind AI - Analytics Events Table Migration
-- ==============================================
-- Description: Track user interactions and engagement for analytics dashboard
-- Created: 2025-11-15
-- Author: Winston (Architect Agent)

-- Create analytics_events table
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB DEFAULT '{}',
    session_id VARCHAR(255),
    customer_identifier VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics_events(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_session_id ON analytics_events(session_id);
CREATE INDEX IF NOT EXISTS idx_analytics_customer_id ON analytics_events(customer_identifier);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_analytics_user_type_date ON analytics_events(user_id, event_type, created_at DESC);

-- Enable Row Level Security
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own analytics
CREATE POLICY "Users can view own analytics" ON analytics_events
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

-- Users can insert their own analytics
CREATE POLICY "Users can insert own analytics" ON analytics_events
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

-- Add comments for documentation
COMMENT ON TABLE analytics_events IS 'Analytics events for tracking user engagement and behavior';
COMMENT ON COLUMN analytics_events.id IS 'Unique event identifier (UUID)';
COMMENT ON COLUMN analytics_events.user_id IS 'Store owner whose analytics this belongs to';
COMMENT ON COLUMN analytics_events.event_type IS 'Type of event (question_asked, product_view, order_lookup, etc.)';
COMMENT ON COLUMN analytics_events.event_data IS 'Flexible JSON data specific to event type';
COMMENT ON COLUMN analytics_events.session_id IS 'Customer session identifier for grouping events';
COMMENT ON COLUMN analytics_events.customer_identifier IS 'Anonymous customer identifier';
COMMENT ON COLUMN analytics_events.ip_address IS 'Customer IP address (optional, for fraud detection)';
COMMENT ON COLUMN analytics_events.user_agent IS 'Browser/app user agent string';
COMMENT ON COLUMN analytics_events.created_at IS 'Event timestamp';

-- Create function to get event counts by type
CREATE OR REPLACE FUNCTION get_event_counts(
    search_user_id UUID,
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() - INTERVAL '7 days',
    end_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS TABLE (
    event_type VARCHAR,
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ae.event_type,
        COUNT(*) AS count
    FROM analytics_events ae
    WHERE
        ae.user_id = search_user_id
        AND ae.created_at BETWEEN start_date AND end_date
    GROUP BY ae.event_type
    ORDER BY count DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_event_counts IS 'Get aggregated event counts by type for a date range';

-- Create function to get daily event volume
CREATE OR REPLACE FUNCTION get_daily_event_volume(
    search_user_id UUID,
    days_back INTEGER DEFAULT 7
)
RETURNS TABLE (
    date DATE,
    event_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        DATE(ae.created_at) AS date,
        COUNT(*) AS event_count
    FROM analytics_events ae
    WHERE
        ae.user_id = search_user_id
        AND ae.created_at >= NOW() - (days_back || ' days')::INTERVAL
    GROUP BY DATE(ae.created_at)
    ORDER BY date DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_daily_event_volume IS 'Get daily event volume for the last N days';

-- Create function to get top product mentions
CREATE OR REPLACE FUNCTION get_top_product_mentions(
    search_user_id UUID,
    days_back INTEGER DEFAULT 7,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_id UUID,
    product_name VARCHAR,
    mention_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (event_data->>'product_id')::UUID AS product_id,
        event_data->>'product_name' AS product_name,
        COUNT(*) AS mention_count
    FROM analytics_events ae
    WHERE
        ae.user_id = search_user_id
        AND ae.event_type = 'product_view'
        AND ae.created_at >= NOW() - (days_back || ' days')::INTERVAL
        AND event_data->>'product_id' IS NOT NULL
    GROUP BY event_data->>'product_id', event_data->>'product_name'
    ORDER BY mention_count DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_top_product_mentions IS 'Get most frequently mentioned products in conversations';

-- Create function to calculate engagement metrics
CREATE OR REPLACE FUNCTION get_engagement_metrics(
    search_user_id UUID,
    days_back INTEGER DEFAULT 7
)
RETURNS TABLE (
    total_conversations BIGINT,
    unique_customers BIGINT,
    avg_messages_per_customer NUMERIC,
    total_events BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT CASE WHEN event_type = 'question_asked' THEN session_id END) AS total_conversations,
        COUNT(DISTINCT customer_identifier) AS unique_customers,
        ROUND(
            COUNT(CASE WHEN event_type = 'question_asked' THEN 1 END)::NUMERIC /
            NULLIF(COUNT(DISTINCT customer_identifier), 0),
            2
        ) AS avg_messages_per_customer,
        COUNT(*) AS total_events
    FROM analytics_events
    WHERE
        user_id = search_user_id
        AND created_at >= NOW() - (days_back || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_engagement_metrics IS 'Calculate engagement metrics for dashboard';

-- Create event type enum for validation (optional, can be added later)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_type_enum') THEN
        CREATE TYPE event_type_enum AS ENUM (
            'question_asked',
            'product_view',
            'order_lookup',
            'conversation_started',
            'conversation_ended',
            'csv_upload',
            'settings_updated'
        );
    END IF;
END$$;

COMMENT ON TYPE event_type_enum IS 'Valid event types for analytics tracking';