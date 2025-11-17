-- ==============================================
-- ShopifyMind AI - Products Table Migration
-- ==============================================
-- Description: Store product inventory for AI context and recommendations
-- Created: 2025-11-15
-- Author: Winston (Architect Agent)

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    category VARCHAR(100),
    sku VARCHAR(100),
    image_url VARCHAR(500),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);

-- Create full-text search index on name and description
CREATE INDEX IF NOT EXISTS idx_products_search ON products
    USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own products
CREATE POLICY "Users can view own products" ON products
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

-- Users can insert their own products
CREATE POLICY "Users can insert own products" ON products
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

-- Users can update their own products
CREATE POLICY "Users can update own products" ON products
    FOR UPDATE
    USING (auth.uid()::text = user_id::text);

-- Users can delete their own products
CREATE POLICY "Users can delete own products" ON products
    FOR DELETE
    USING (auth.uid()::text = user_id::text);

-- Add comments for documentation
COMMENT ON TABLE products IS 'Product inventory for AI context and customer queries';
COMMENT ON COLUMN products.id IS 'Unique product identifier (UUID)';
COMMENT ON COLUMN products.user_id IS 'Store owner who owns this product';
COMMENT ON COLUMN products.name IS 'Product name (searchable)';
COMMENT ON COLUMN products.description IS 'Product description (searchable, optional)';
COMMENT ON COLUMN products.price IS 'Product price in store currency';
COMMENT ON COLUMN products.category IS 'Product category for filtering';
COMMENT ON COLUMN products.sku IS 'Stock keeping unit (optional, unique per store)';
COMMENT ON COLUMN products.image_url IS 'URL to product image (optional)';
COMMENT ON COLUMN products.stock_quantity IS 'Available stock quantity';
COMMENT ON COLUMN products.is_active IS 'Product visibility status';
COMMENT ON COLUMN products.metadata IS 'Additional product data as JSON';
COMMENT ON COLUMN products.created_at IS 'Product creation timestamp';
COMMENT ON COLUMN products.updated_at IS 'Last update timestamp (auto-updated)';

-- Create function for full-text search
CREATE OR REPLACE FUNCTION search_products(
    search_user_id UUID,
    search_query TEXT,
    limit_count INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    name VARCHAR,
    description TEXT,
    price DECIMAL,
    category VARCHAR,
    image_url VARCHAR,
    relevance REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.name,
        p.description,
        p.price,
        p.category,
        p.image_url,
        ts_rank(
            to_tsvector('english', p.name || ' ' || COALESCE(p.description, '')),
            plainto_tsquery('english', search_query)
        ) AS relevance
    FROM products p
    WHERE
        p.user_id = search_user_id
        AND p.is_active = TRUE
        AND to_tsvector('english', p.name || ' ' || COALESCE(p.description, '')) @@ plainto_tsquery('english', search_query)
    ORDER BY relevance DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_products IS 'Full-text search for products with relevance ranking';