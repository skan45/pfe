
-- Insert Client group if it doesn't exist
INSERT INTO auth_group (name)
VALUES ('Client')
ON CONFLICT (name) DO NOTHING;

-- Insert Comptable group if it doesn't exist
INSERT INTO auth_group (name)
VALUES ('Comptable')
ON CONFLICT (name) DO NOTHING;