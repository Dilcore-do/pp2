-- =====================================================
-- UPSERT CONTACT
-- Если контакт существует (имя + фамилия) → обновляем
-- иначе создаём нового
-- =====================================================
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_email VARCHAR,
    p_birthday DATE,
    p_group_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INT;
    v_group_id INT;
BEGIN
    -- ищем или создаём группу
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    IF v_group_id IS NULL THEN
        INSERT INTO groups(name)
        VALUES (p_group_name)
        RETURNING id INTO v_group_id;
    END IF;

    -- проверяем существование контакта
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name = p_first_name AND last_name = p_last_name;

    IF v_contact_id IS NOT NULL THEN
        -- обновление контакта
        UPDATE contacts
        SET email = p_email,
            birthday = p_birthday,
            group_id = v_group_id
        WHERE id = v_contact_id;

    ELSE
        -- создание контакта
        INSERT INTO contacts(first_name, last_name, email, birthday, group_id)
        VALUES (p_first_name, p_last_name, p_email, p_birthday, v_group_id)
        RETURNING id INTO v_contact_id;
    END IF;

    -- добавляем телефон (всегда отдельная таблица)
    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;


-- =====================================================
-- BULK INSERT CONTACTS
-- Массовая загрузка контактов из массивов
-- =====================================================
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    p_names TEXT[],
    p_phones TEXT[],
    p_emails TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    v_contact_id INT;
BEGIN
    FOR i IN 1..array_length(p_names, 1)
    LOOP
        -- простая проверка телефона
        IF p_phones[i] ~ '^[0-9+]{6,}$' THEN

            INSERT INTO contacts(first_name, email)
            VALUES (p_names[i], p_emails[i])
            RETURNING id INTO v_contact_id;

            INSERT INTO phones(contact_id, phone, type)
            VALUES (v_contact_id, p_phones[i], 'mobile');

        ELSE
            RAISE NOTICE 'Invalid phone: %', p_phones[i];
        END IF;
    END LOOP;
END;
$$;


-- =====================================================
-- DELETE CONTACT
-- Удаление по имени или телефону
-- =====================================================
CREATE OR REPLACE PROCEDURE delete_contact(
    p_value TEXT,
    p_type TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_type = 'name' THEN
        DELETE FROM contacts
        WHERE first_name = p_value;

    ELSIF p_type = 'phone' THEN
        DELETE FROM contacts
        WHERE id IN (
            SELECT contact_id FROM phones WHERE phone = p_value
        );
    END IF;
END;
$$;


-- =====================================================
-- ADD PHONE (TSIS requirement)
-- добавляет телефон существующему контакту
-- =====================================================
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE v_id INT;
BEGIN
    SELECT id INTO v_id
    FROM contacts
    WHERE first_name = p_contact_name
    LIMIT 1;

    IF v_id IS NULL THEN
        RAISE NOTICE 'Contact not found';
    ELSE
        INSERT INTO phones(contact_id, phone, type)
        VALUES (v_id, p_phone, p_type);
    END IF;
END;
$$;


-- =====================================================
-- MOVE CONTACT TO GROUP (TSIS requirement)
-- создаёт группу если её нет
-- =====================================================
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INT;
BEGIN
    -- ищем группу
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- если нет → создаём
    IF v_group_id IS NULL THEN
        INSERT INTO groups(name)
        VALUES (p_group_name)
        RETURNING id INTO v_group_id;
    END IF;

    -- обновляем контакт
    UPDATE contacts
    SET group_id = v_group_id
    WHERE first_name = p_contact_name;
END;
$$;


-- =====================================================
-- SEARCH CONTACTS (TSIS UPGRADED VERSION)
-- ищет по:
-- имя, фамилия, email, телефон
-- =====================================================
CREATE OR REPLACE FUNCTION search_contacts(
    p_query TEXT
)
RETURNS TABLE(
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phone VARCHAR,
    type VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.first_name,
           c.last_name,
           c.email,
           c.birthday,
           g.name,
           p.phone,
           p.type
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE
        c.first_name ILIKE '%' || p_query || '%'
        OR c.last_name ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR p.phone ILIKE '%' || p_query || '%';
END;
$$;


-- =====================================================
-- PAGINATION (если ещё нет / фикс версии)
-- =====================================================
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_limit INT,
    p_offset INT
)
RETURNS TABLE(
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phone VARCHAR,
    type VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.first_name,
           c.last_name,
           c.email,
           c.birthday,
           g.name,
           p.phone,
           p.type
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$;