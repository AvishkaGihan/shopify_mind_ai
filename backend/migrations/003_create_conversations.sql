-- ==============================================
-- ShopifyMind AI - Conversations Table Migration
-- ==============================================
-- Description: Store chat history between customers and AI
-- Created: 2025-11-15
-- Author: Winston (Architect Agent)

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    customer_identifier VARCHAR(255),
    customer_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    message_count INTEGER DEFAULT 1,
    products_referenced JSONB DEFAULT '[]',
    intent_detected VARCHAR(100),
    sentiment_score DECIMAL(3,2),
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_customer_id ON conversations(customer_identifier);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_intent ON conversations(intent_detected);
CREATE INDEX IF NOT EXISTS idx_conversations_message_count ON conversations(message_count);

-- Create full-text search index on messages
CREATE INDEX IF NOT EXISTS idx_conversations_search ON conversations
    USING gin(to_tsvector('english', customer_message || ' ' || ai_response));

-- Enable Row Level Security
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own conversations
CREATE POLICY "Users can view own conversations" ON conversations
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

-- Users can insert their own conversations
CREATE POLICY "Users can insert own conversations" ON conversations
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

-- Users can update their own conversations
CREATE POLICY "Users can update own conversations" ON conversations
    FOR UPDATE
    USING (auth.uid()::text = user_id::text);

-- Users can delete their own conversations
CREATE POLICY "Users can delete own conversations" ON conversations
    FOR DELETE
    USING (auth.uid()::text = user_id::text);

-- Add comments for documentation
COMMENT ON TABLE conversations IS 'Chat history between customers and AI assistant';
COMMENT ON COLUMN conversations.id IS 'Unique conversation message identifier (UUID)';
COMMENT ON COLUMN conversations.user_id IS 'Store owner whose AI handled this conversation';
COMMENT ON COLUMN conversations.customer_identifier IS 'Anonymous customer identifier (email, session ID, etc.)';
COMMENT ON COLUMN conversations.customer_message IS 'Customer question or message';
COMMENT ON COLUMN conversations.ai_response IS 'AI-generated response';
COMMENT ON COLUMN conversations.message_count IS 'Sequential message number in conversation';
COMMENT ON COLUMN conversations.products_referenced IS 'Array of product IDs mentioned in response';
COMMENT ON COLUMN conversations.intent_detected IS 'Detected customer intent (product_inquiry, order_lookup, etc.)';
COMMENT ON COLUMN conversations.sentiment_score IS 'Customer sentiment score (-1.0 to 1.0)';
COMMENT ON COLUMN conversations.response_time_ms IS 'AI response time in milliseconds';
COMMENT ON COLUMN conversations.created_at IS 'Message timestamp';

-- Create function to get conversation history
CREATE OR REPLACE FUNCTION get_conversation_history(
    search_user_id UUID,
    search_customer_id VARCHAR DEFAULT NULL,
    limit_count INTEGER DEFAULT 20,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    customer_identifier VARCHAR,
    customer_message TEXT,
    ai_response TEXT,
    message_count INTEGER,
    products_referenced JSONB,
    intent_detected VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.customer_identifier,
        c.customer_message,
        c.ai_response,
        c.message_count,
        c.products_referenced,
        c.intent_detected,
        c.created_at
    FROM conversations c
    WHERE
        c.user_id = search_user_id
        AND (search_customer_id IS NULL OR c.customer_identifier = search_customer_id)
    ORDER BY c.created_at DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_conversation_history IS 'Retrieve paginated conversation history for a store';

-- Create function to search conversations
CREATE OR REPLACE FUNCTION search_conversations(
    search_user_id UUID,
    search_query TEXT,
    limit_count INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    customer_message TEXT,
    ai_response TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    relevance REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.customer_message,
        c.ai_response,
        c.created_at,
        ts_rank(
            to_tsvector('english', c.customer_message || ' ' || c.ai_response),
            plainto_tsquery('english', search_query)
        ) AS relevance
    FROM conversations c
    WHERE
        c.user_id = search_user_id
        AND to_tsvector('english', c.customer_message || ' ' || c.ai_response) @@ plainto_tsquery('english', search_query)
    ORDER BY relevance DESC, c.created_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_conversations IS 'Full-text search across conversation history';