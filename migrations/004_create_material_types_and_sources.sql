-- Migration 004: Create material_types and material_sources tables
-- This migration creates a new relational structure for materials

-- Create material_types table
CREATE TABLE material_types (
    id CHAR(36) PRIMARY KEY,
    type ENUM('SAND', 'STONE') NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create material_sources table
CREATE TABLE material_sources (
    id CHAR(36) PRIMARY KEY,
    material_type_id CHAR(36) NOT NULL,
    source_name VARCHAR(200) NOT NULL,
    location VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    contact_person VARCHAR(100),
    contact_number VARCHAR(20),
    price_per_unit DECIMAL(10, 2),
    unit VARCHAR(20) DEFAULT 'ton',
    availability_status VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (material_type_id) REFERENCES material_types(id) ON DELETE CASCADE,
    INDEX idx_material_type_id (material_type_id)
);

-- Insert the two material types (SAND and STONE)
INSERT INTO material_types (id, type, description) VALUES
(UUID(), 'SAND', 'Sand material for construction'),
(UUID(), 'STONE', 'Stone material for construction');

-- Get the material type IDs for reference
SET @sand_type_id = (SELECT id FROM material_types WHERE type = 'SAND');
SET @stone_type_id = (SELECT id FROM material_types WHERE type = 'STONE');

-- Insert material sources based on existing materials data
-- Stone sources
INSERT INTO material_sources (id, material_type_id, source_name, location, city, state, price_per_unit, unit, availability_status) VALUES
(UUID(), @stone_type_id, 'Dumka Stone Quarry', 'Dumka', 'Dumka', 'Jharkhand', 1200.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Rampurhat Stone Quarry', 'Rampurhat', 'Birbhum', 'West Bengal', 1150.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Devipur Stone Quarry', 'Devipur', 'Deoghar', 'Jharkhand', 1250.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Pakur Stone Quarry', 'Pakur', 'Pakur', 'Jharkhand', 1180.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Mirza Chawki Stone Quarry', 'Mirza Chawki', 'Munger', 'Bihar', 1220.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Tapowan Hill Stone Quarry', 'Tapowan Hill', 'Gaya', 'Bihar', 1300.00, 'ton', 'available');

-- Sand sources
INSERT INTO material_sources (id, material_type_id, source_name, location, city, state, price_per_unit, unit, availability_status) VALUES
(UUID(), @sand_type_id, 'Nawada Sand Mine', 'Nawada', 'Nawada', 'Bihar', 800.00, 'ton', 'available'),
(UUID(), @sand_type_id, 'Jamui Sand Mine', 'Jamui', 'Jamui', 'Bihar', 750.00, 'ton', 'available'),
(UUID(), @sand_type_id, 'Lakhisarai Sand Mine', 'Lakhisarai', 'Lakhisarai', 'Bihar', 780.00, 'ton', 'available'),
(UUID(), @sand_type_id, 'Sone River Sand Mine', 'Sone', 'Patna', 'Bihar', 820.00, 'ton', 'available');

-- Update the existing materials table to reference material_sources
-- First, add the new column
ALTER TABLE materials ADD COLUMN material_source_id CHAR(36);

-- Update materials to reference the appropriate material sources
-- Map existing materials to new material sources based on type and source
UPDATE materials m
JOIN material_sources ms ON m.source = ms.source_name
JOIN material_types mt ON ms.material_type_id = mt.id
SET m.material_source_id = ms.id
WHERE (m.type = 'Sand' AND mt.type = 'SAND') OR (m.type = 'Stone' AND mt.type = 'STONE');

-- Make the new column NOT NULL and add foreign key constraint
ALTER TABLE materials MODIFY COLUMN material_source_id CHAR(36) NOT NULL;
ALTER TABLE materials ADD FOREIGN KEY (material_source_id) REFERENCES material_sources(id) ON DELETE CASCADE;
ALTER TABLE materials ADD INDEX idx_material_source_id (material_source_id);

-- Remove the old columns from materials table
ALTER TABLE materials DROP COLUMN type;
ALTER TABLE materials DROP COLUMN source; 