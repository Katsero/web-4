-- =============================================================================
-- ЛАБОРАТОРНАЯ 3-4: ЦИКЛЫ (FOR, WHILE, LOOP + EXIT WHEN)
-- =============================================================================

-- 1. ЦИКЛ FOR: Сбор JSON-списка игр с низким остатком
CREATE OR REPLACE FUNCTION ps_get_low_stock_games_json(p_threshold INT)
RETURNS JSON AS $$
DECLARE
    r RECORD;
    v_result JSON := '[]'::json;
BEGIN
    FOR r IN SELECT name, current_stock, price FROM puzzlestore_boardgame WHERE current_stock <= p_threshold AND current_stock > 0 LOOP
        v_result := v_result || jsonb_build_object(
            'name', r.name,
            'stock', r.current_stock,
            'action', 'Срочно заказать!'
        )::json;
    END LOOP;
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- 2. ЦИКЛ WHILE: Пакетная очистка старых корзин
CREATE OR REPLACE PROCEDURE ps_cleanup_old_carts(p_days_to_keep INT, p_batch_size INT)
LANGUAGE plpgsql AS $$
DECLARE
    v_deleted_count INT := 1;
BEGIN
    WHILE v_deleted_count > 0 LOOP
        DELETE FROM puzzlestore_cart
        WHERE id IN (
            SELECT id FROM puzzlestore_cart
            WHERE created_at < CURRENT_DATE - INTERVAL '1 day' * p_days_to_keep
            LIMIT p_batch_size
        );
        GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
        COMMIT; 
        RAISE NOTICE 'Удалено записей корзины: %', v_deleted_count;
    END LOOP;
END;
$$;

-- 3. ЦИКЛ LOOP + EXIT WHEN: Генерация уникального кода новой игры
CREATE OR REPLACE FUNCTION ps_generate_unique_game_code(p_prefix TEXT)
RETURNS TEXT AS $$
DECLARE
    v_code TEXT;
    v_exists BOOLEAN;
BEGIN
    LOOP
        v_code := p_prefix || '-' || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');
        SELECT EXISTS(SELECT 1 FROM puzzlestore_boardgame WHERE name = v_code) INTO v_exists;
        IF NOT v_exists THEN
            EXIT;
        END IF;
    END LOOP;
    RETURN v_code;
END;
$$ LANGUAGE plpgsql;

-- =========================================================================
-- ЗАПРОСЫ ДЛЯ ПРОВЕРКИ ЦИКЛОВ
-- =========================================================================

-- ПРОВЕРКА 1: Получить JSON-список игр, у которых на складе <= 5 штук
SELECT ps_get_low_stock_games_json(5);

-- ПРОВЕРКА 2: Очистка старых корзин (старше 30 дней, пачками по 100 шт.)
CALL ps_cleanup_old_carts(30, 100);

-- ПРОВЕРКА 3: Генерация уникального кода (запускай несколько раз, чтобы увидеть разные коды)
SELECT ps_generate_unique_game_code('PUZZLE');