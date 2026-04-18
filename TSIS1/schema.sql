CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);


INSERT INTO groups(name) VALUES
('Family'),
('Work'),
('Friend'),
('Other');


ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS email VARCHAR(100);

ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS birthday DATE;

ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES groups(id);


CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);

