-- =============================================================================
-- ЛАБОРАТОРНАЯ 3-4: ФУНКЦИИ (5 примеров разной сложности)
-- =============================================================================

-- 1. СКАЛЯРНАЯ ФУНКЦИЯ: Расчет актуальной цены игры
CREATE OR REPLACE FUNCTION ps_get_current_game_price(p_game_id INT)
RETURNS NUMERIC AS $$
DECLARE
    v_base_price NUMERIC;
    v_latest_supply_cost NUMERIC;
BEGIN
    SELECT price INTO v_base_price FROM puzzlestore_boardgame WHERE id = p_game_id;
    SELECT unit_cost INTO v_latest_supply_cost 
    FROM puzzlestore_supply WHERE game_id = p_game_id ORDER BY supply_date DESC LIMIT 1;

    IF v_latest_supply_cost IS NOT NULL AND v_latest_supply_cost > v_base_price THEN
        RETURN v_base_price;
    ELSE
        RETURN v_base_price;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 2. ТАБЛИЧНАЯ ФУНКЦИЯ: Карточка игры для витрины
CREATE OR REPLACE FUNCTION ps_get_game_card(p_game_id INT)
RETURNS TABLE (
    game_name VARCHAR,
    publisher_name VARCHAR,
    avg_rating NUMERIC,
    total_sales_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT bg.name, p.name, COALESCE(bg.rating_avg, 0.0), COALESCE(COUNT(s.id), 0)
    FROM puzzlestore_boardgame bg
    JOIN puzzlestore_publisher p ON bg.publisher_id = p.id
    LEFT JOIN puzzlestore_sale s ON bg.id = s.game_id
    WHERE bg.id = p_game_id
    GROUP BY bg.name, p.name, bg.rating_avg;
END;
$$ LANGUAGE plpgsql;

-- 3. ФУНКЦИЯ С CASE: Сегментация покупателя
CREATE OR REPLACE FUNCTION ps_get_customer_segment(p_user_id INT)
RETURNS VARCHAR AS $$
DECLARE
    v_total_spent NUMERIC;
BEGIN
    SELECT COALESCE(SUM(quantity * unit_price), 0) INTO v_total_spent
    FROM puzzlestore_sale WHERE user_id = p_user_id AND status = 'completed';

    RETURN CASE 
        WHEN v_total_spent >= 50000 THEN 'VIP'
        WHEN v_total_spent >= 10000 THEN 'Regular'
        WHEN v_total_spent > 0 THEN 'New Buyer'
        ELSE 'No Orders'
    END;
END;
$$ LANGUAGE plpgsql;

-- 4. ФУНКЦИЯ ПРОВЕРКИ: Хватит ли товара?
CREATE OR REPLACE FUNCTION ps_check_stock_availability(p_game_id INT, p_quantity INT)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_stock INT;
BEGIN
    SELECT current_stock INTO v_current_stock FROM puzzlestore_boardgame WHERE id = p_game_id;
    RETURN v_current_stock >= p_quantity;
END;
$$ LANGUAGE plpgsql;

-- 5. ПРОЦЕДУРА: Массовое применение скидки издателя
CREATE OR REPLACE PROCEDURE ps_apply_publisher_discount(p_publisher_id INT, p_percent NUMERIC)
LANGUAGE plpgsql AS $$
DECLARE
    r RECORD;
    v_new_price NUMERIC;
BEGIN
    FOR r IN SELECT id, name, price FROM puzzlestore_boardgame WHERE publisher_id = p_publisher_id LOOP
        v_new_price := r.price * (1 - p_percent / 100.0);
        UPDATE puzzlestore_boardgame SET price = v_new_price WHERE id = r.id;
        RAISE NOTICE 'Цена на "%" снижена до %', r.name, v_new_price;
    END LOOP;
    COMMIT;
END;
$$;

-- =========================================================================
-- ЗАПРОСЫ ДЛЯ ПРОВЕРКИ ФУНКЦИЙ
-- =========================================================================

-- ПРОВЕРКА 1: Скалярная функция
SELECT ps_get_current_game_price(1);

-- ПРОВЕРКА 2: Табличная функция (возвращает таблицу, поэтому пишем SELECT *)
SELECT * FROM ps_get_game_card(1);

-- ПРОВЕРКА 3: Сегментация клиента
SELECT ps_get_customer_segment(1);

-- ПРОВЕРКА 4: Проверка наличия на складе (проверяем игру 1, запрашиваем 5 штук)
SELECT ps_check_stock_availability(1, 5);

-- ПРОВЕРКА 5: Процедура массовой скидки (издатель 1, скидка 15%)
CALL ps_apply_publisher_discount(1, 15);