-- Upsert
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

-- Bulk insert
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

-- Delete
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