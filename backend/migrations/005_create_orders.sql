-- ==============================================
-- ShopifyMind AI - Orders Table Migration
-- ==============================================
-- Description: Store mock orders for customer lookup and tracking
-- Created: 2025-11-15
-- Author: Winston (Architect Agent)

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id VARCHAR(50) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    customer_phone VARCHAR(50),
    items JSONB NOT NULL DEFAULT '[]',
    subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0),
    tax DECIMAL(10,2) DEFAULT 0 CHECK (tax >= 0),
    shipping DECIMAL(10,2) DEFAULT 0 CHECK (shipping >= 0),
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    payment_status VARCHAR(50) DEFAULT 'pending',
    shipping_address JSONB,
    billing_address JSONB,
    estimated_delivery TIMESTAMP WITH TIME ZONE,
    actual_delivery TIMESTAMP WITH TIME ZONE,
    tracking_number VARCHAR(255),
    tracking_url VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_order_id_per_user UNIQUE (user_id, order_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer_email ON orders(customer_email);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_estimated_delivery ON orders(estimated_delivery);

-- Create composite index for common searches
CREATE INDEX IF NOT EXISTS idx_orders_user_email ON orders(user_id, customer_email);

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own orders
CREATE POLICY "Users can view own orders" ON orders
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

-- Users can insert their own orders
CREATE POLICY "Users can insert own orders" ON orders
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

-- Users can update their own orders
CREATE POLICY "Users can update own orders" ON orders
    FOR UPDATE
    USING (auth.uid()::text = user_id::text);

-- Users can delete their own orders
CREATE POLICY "Users can delete own orders" ON orders
    FOR DELETE
    USING (auth.uid()::text = user_id::text);

-- Add comments for documentation
COMMENT ON TABLE orders IS 'Customer orders for tracking and status lookup';
COMMENT ON COLUMN orders.id IS 'Unique order identifier (UUID, internal)';
COMMENT ON COLUMN orders.user_id IS 'Store owner who owns this order';
COMMENT ON COLUMN orders.order_id IS 'Human-readable order number (e.g., ORD-12345)';
COMMENT ON COLUMN orders.customer_email IS 'Customer email address (searchable)';
COMMENT ON COLUMN orders.customer_name IS 'Customer full name';
COMMENT ON COLUMN orders.customer_phone IS 'Customer phone number (optional)';
COMMENT ON COLUMN orders.items IS 'Array of order items with product details';
COMMENT ON COLUMN orders.subtotal IS 'Order subtotal before tax and shipping';
COMMENT ON COLUMN orders.tax IS 'Tax amount';
COMMENT ON COLUMN orders.shipping IS 'Shipping cost';
COMMENT ON COLUMN orders.total IS 'Total order amount (subtotal + tax + shipping)';
COMMENT ON COLUMN orders.status IS 'Order status (pending, processing, shipped, delivered, cancelled)';
COMMENT ON COLUMN orders.payment_status IS 'Payment status (pending, paid, refunded, failed)';
COMMENT ON COLUMN orders.shipping_address IS 'Shipping address as JSON';
COMMENT ON COLUMN orders.billing_address IS 'Billing address as JSON';
COMMENT ON COLUMN orders.estimated_delivery IS 'Estimated delivery date/time';
COMMENT ON COLUMN orders.actual_delivery IS 'Actual delivery date/time (when delivered)';
COMMENT ON COLUMN orders.tracking_number IS 'Carrier tracking number';
COMMENT ON COLUMN orders.tracking_url IS 'URL to carrier tracking page';
COMMENT ON COLUMN orders.notes IS 'Internal notes or customer comments';
COMMENT ON COLUMN orders.created_at IS 'Order creation timestamp';
COMMENT ON COLUMN orders.updated_at IS 'Last update timestamp (auto-updated)';

-- Create function to search orders
CREATE OR REPLACE FUNCTION search_orders(
    search_user_id UUID,
    search_query TEXT
)
RETURNS TABLE (
    id UUID,
    order_id VARCHAR,
    customer_email VARCHAR,
    customer_name VARCHAR,
    items JSONB,
    total DECIMAL,
    status VARCHAR,
    estimated_delivery TIMESTAMP WITH TIME ZONE,
    tracking_number VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.id,
        o.order_id,
        o.customer_email,
        o.customer_name,
        o.items,
        o.total,
        o.status,
        o.estimated_delivery,
        o.tracking_number,
        o.created_at
    FROM orders o
    WHERE
        o.user_id = search_user_id
        AND (
            o.order_id ILIKE '%' || search_query || '%'
            OR o.customer_email ILIKE '%' || search_query || '%'
            OR o.customer_name ILIKE '%' || search_query || '%'
        )
    ORDER BY o.created_at DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_orders IS 'Search orders by order ID, email, or customer name';

-- Create function to get order by ID
CREATE OR REPLACE FUNCTION get_order_details(
    search_user_id UUID,
    search_order_id VARCHAR
)
RETURNS TABLE (
    id UUID,
    order_id VARCHAR,
    customer_email VARCHAR,
    customer_name VARCHAR,
    customer_phone VARCHAR,
    items JSONB,
    subtotal DECIMAL,
    tax DECIMAL,
    shipping DECIMAL,
    total DECIMAL,
    status VARCHAR,
    payment_status VARCHAR,
    shipping_address JSONB,
    estimated_delivery TIMESTAMP WITH TIME ZONE,
    actual_delivery TIMESTAMP WITH TIME ZONE,
    tracking_number VARCHAR,
    tracking_url VARCHAR,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.id,
        o.order_id,
        o.customer_email,
        o.customer_name,
        o.customer_phone,
        o.items,
        o.subtotal,
        o.tax,
        o.shipping,
        o.total,
        o.status,
        o.payment_status,
        o.shipping_address,
        o.estimated_delivery,
        o.actual_delivery,
        o.tracking_number,
        o.tracking_url,
        o.notes,
        o.created_at
    FROM orders o
    WHERE
        o.user_id = search_user_id
        AND o.order_id = search_order_id
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_order_details IS 'Get complete order details by order ID';

-- Create status enum for validation
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'order_status_enum') THEN
        CREATE TYPE order_status_enum AS ENUM (
            'pending',
            'processing',
            'shipped',
            'in_transit',
            'out_for_delivery',
            'delivered',
            'cancelled',
            'refunded',
            'failed'
        );
    END IF;
END$$;

COMMENT ON TYPE order_status_enum IS 'Valid order status values';

-- Create payment status enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status_enum') THEN
        CREATE TYPE payment_status_enum AS ENUM (
            'pending',
            'authorized',
            'paid',
            'partially_refunded',
            'refunded',
            'failed',
            'cancelled'
        );
    END IF;
END$$;

COMMENT ON TYPE payment_status_enum IS 'Valid payment status values';

-- Insert sample/mock orders for testing (optional)
-- Uncomment below to create sample data
/*
INSERT INTO orders (user_id, order_id, customer_email, customer_name, items, subtotal, tax, shipping, total, status, estimated_delivery, tracking_number)
SELECT
    u.id,
    'ORD-' || LPAD((ROW_NUMBER() OVER())::TEXT, 5, '0'),
    'customer' || (ROW_NUMBER() OVER()) || '@example.com',
    'Customer ' || (ROW_NUMBER() OVER()),
    '[{"product_name": "Sample Product", "quantity": 2, "price": 29.99}]'::JSONB,
    59.98,
    5.40,
    10.00,
    75.38,
    (ARRAY['pending', 'processing', 'shipped', 'delivered'])[floor(random() * 4 + 1)],
    NOW() + (floor(random() * 7) || ' days')::INTERVAL,
    'TRK' || LPAD((ROW_NUMBER() OVER())::TEXT, 10, '0')
FROM users u
LIMIT 10;
*/