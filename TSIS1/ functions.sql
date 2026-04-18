-- Поиск по шаблону
CREATE OR REPLACE FUNCTION search_contacts(p_pattern TEXT)
RETURNS TABLE(first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT c.first_name, c.last_name, c.phone_number
    FROM contacts c
    WHERE c.first_name ILIKE '%' || p_pattern || '%'
       OR c.last_name ILIKE '%' || p_pattern || '%'
       OR c.phone_number ILIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- Пагинация
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT c.first_name, c.last_name, c.phone_number
    FROM contacts c
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;