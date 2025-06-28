-- Migration 005: Update bookings table to reference material_sources
-- This migration updates the bookings table to use the new material structure

-- Add the new column to bookings table
ALTER TABLE bookings ADD COLUMN material_source_id CHAR(36);

-- Update bookings to reference material_sources through the materials table
UPDATE bookings b
JOIN materials m ON b.material_id = m.id
SET b.material_source_id = m.material_source_id;

-- Make the new column NOT NULL and add foreign key constraint
ALTER TABLE bookings MODIFY COLUMN material_source_id CHAR(36) NOT NULL;
ALTER TABLE bookings ADD FOREIGN KEY (material_source_id) REFERENCES material_sources(id) ON DELETE CASCADE;
ALTER TABLE bookings ADD INDEX idx_material_source_id (material_source_id);

-- Remove the old material_id column and source column
ALTER TABLE bookings DROP FOREIGN KEY bookings_ibfk_2; -- Drop the foreign key constraint first (adjust constraint name if needed)
ALTER TABLE bookings DROP COLUMN material_id;
ALTER TABLE bookings DROP COLUMN source; 