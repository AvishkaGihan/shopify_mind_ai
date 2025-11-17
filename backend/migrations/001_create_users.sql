-- ==============================================
-- ShopifyMind AI - Users Table Migration
-- ==============================================
-- Description: Store owner accounts with authentication and store configuration
-- Created: 2025-11-15
-- Author: Winston (Architect Agent)

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    store_name VARCHAR(255),
    store_colors JSONB DEFAULT '{"primary":"#00a86b","accent":"#f97316","supporting":"#a78bfa"}',
    ai_tone VARCHAR(50) DEFAULT 'friendly' CHECK (ai_tone IN ('friendly', 'professional', 'casual', 'energetic')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT
    USING (auth.uid()::text = id::text);

-- Users can update their own data
CREATE POLICY "Users can update own data" ON users
    FOR UPDATE
    USING (auth.uid()::text = id::text);

-- Anyone can insert (for signup)
CREATE POLICY "Anyone can signup" ON users
    FOR INSERT
    WITH CHECK (true);

-- Add comments for documentation
COMMENT ON TABLE users IS 'Store owner accounts with authentication and configuration';
COMMENT ON COLUMN users.id IS 'Unique user identifier (UUID)';
COMMENT ON COLUMN users.email IS 'User email address (unique, used for login)';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password (never store plain text)';
COMMENT ON COLUMN users.store_name IS 'Display name for the store';
COMMENT ON COLUMN users.store_colors IS 'Brand colors (primary, accent, supporting) as JSON';
COMMENT ON COLUMN users.ai_tone IS 'AI personality tone for customer interactions';
COMMENT ON COLUMN users.is_active IS 'Account active status (false = suspended)';
COMMENT ON COLUMN users.is_verified IS 'Email verification status';
COMMENT ON COLUMN users.created_at IS 'Account creation timestamp';
COMMENT ON COLUMN users.updated_at IS 'Last update timestamp (auto-updated)';
COMMENT ON COLUMN users.last_login_at IS 'Last successful login timestamp';