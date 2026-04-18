-- =========================
-- UPSERT
-- =========================
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM contacts 
        WHERE first_name = p_first_name AND last_name = p_last_name
    ) THEN
        UPDATE contacts
        SET phone_number = p_phone
        WHERE first_name = p_first_name AND last_name = p_last_name;
    ELSE
        INSERT INTO contacts(first_name, last_name, phone_number)
        VALUES (p_first_name, p_last_name, p_phone);
    END IF;
END;
$$;


-- =========================
-- BULK INSERT
-- =========================
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(p_names, 1)
    LOOP
        IF p_phones[i] ~ '^[0-9]{10,}$' THEN
            INSERT INTO contacts(first_name, phone_number)
            VALUES (p_names[i], p_phones[i]);
        ELSE
            RAISE NOTICE 'Invalid phone: %', p_phones[i];
        END IF;
    END LOOP;
END;
$$;


-- =========================
-- DELETE
-- =========================
CREATE OR REPLACE PROCEDURE delete_contact(
    p_value TEXT,
    p_type TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_type = 'name' THEN
        DELETE FROM contacts WHERE first_name = p_value;

    ELSIF p_type = 'phone' THEN
        DELETE FROM contacts WHERE phone_number = p_value;
    END IF;
END;
$$;


-- =========================
-- ADD PHONE 
-- =========================
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE contacts
    SET phone_number = p_phone
    WHERE first_name = p_contact_name;

    IF NOT FOUND THEN
        RAISE NOTICE 'Contact not found: %', p_contact_name;
    END IF;
END;
$$;


-- =========================
-- MOVE TO GROUP 
-- =========================
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    -- старая схема не поддерживает groups
    RAISE NOTICE 'Move % to group % (not supported in current schema)', 
        p_contact_name, p_group_name;
END;
$$;


-- =========================
-- SEARCH CONTACTS FUNCTION
-- =========================
CREATE OR REPLACE FUNCTION search_contacts(
    p_query TEXT
)
RETURNS TABLE(
    first_name VARCHAR,
    last_name VARCHAR,
    phone_number VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.first_name, c.last_name, c.phone_number
    FROM contacts c
    WHERE c.first_name ILIKE '%' || p_query || '%'
       OR c.last_name ILIKE '%' || p_query || '%'
       OR c.phone_number ILIKE '%' || p_query || '%';
END;
$$;