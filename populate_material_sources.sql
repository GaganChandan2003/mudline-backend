-- Populate material_sources table with sample data
-- First, ensure material_types exist
INSERT IGNORE INTO material_types (id, type, description) VALUES
(UUID(), 'SAND', 'Sand material for construction'),
(UUID(), 'STONE', 'Stone material for construction');

-- Get the material type IDs for reference
SET @sand_type_id = (SELECT id FROM material_types WHERE type = 'SAND' LIMIT 1);
SET @stone_type_id = (SELECT id FROM material_types WHERE type = 'STONE' LIMIT 1);

-- Insert material sources
INSERT IGNORE INTO material_sources (id, material_type_id, source_name, location, city, state, price_per_unit, unit, availability_status) VALUES
-- Stone sources
(UUID(), @stone_type_id, 'Dumka Stone Quarry', 'Dumka', 'Dumka', 'Jharkhand', 1200.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Rampurhat Stone Quarry', 'Rampurhat', 'Birbhum', 'West Bengal', 1150.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Devipur Stone Quarry', 'Devipur', 'Deoghar', 'Jharkhand', 1250.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Pakur Stone Quarry', 'Pakur', 'Pakur', 'Jharkhand', 1180.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Mirza Chawki Stone Quarry', 'Mirza Chawki', 'Munger', 'Bihar', 1220.00, 'ton', 'available'),
(UUID(), @stone_type_id, 'Tapowan Hill Stone Quarry', 'Tapowan Hill', 'Gaya', 'Bihar', 1300.00, 'ton', 'available'),

-- Sand sources
(UUID(), @sand_type_id, 'Nawada Sand Mine', 'Nawada', 'Nawada', 'Bihar', 800.00, 'ton', 'available'),
(UUID(), @sand_type_id, 'Jamui Sand Mine', 'Jamui', 'Jamui', 'Bihar', 750.00, 'ton', 'available'),
(UUID(), @sand_type_id, 'Lakhisarai Sand Mine', 'Lakhisarai', 'Lakhisarai', 'Bihar', 780.00, 'ton', 'available'),
(UUID(), @sand_type_id, 'Sone River Sand Mine', 'Sone', 'Patna', 'Bihar', 820.00, 'ton', 'available'); 