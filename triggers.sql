-- =============================================================================
-- ЛАБОРАТОРНАЯ 6: ТРИГГЕРЫ (3 примера: валидация, аудит, авто-обновление)
-- =============================================================================

-- Таблица для логов аудита (нужна для триггера №2)
CREATE TABLE IF NOT EXISTS ps_price_audit (
    id SERIAL PRIMARY KEY,
    game_id INT,
    game_name VARCHAR,
    old_price NUMERIC,
    new_price NUMERIC,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1. ТРИГГЕР ВАЛИДАЦИИ (BEFORE)
CREATE OR REPLACE FUNCTION ps_trg_validate_supply_cost()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.unit_cost <= 0 THEN
        RAISE EXCEPTION 'Ошибка: Стоимость поставки (unit_cost) должна быть больше 0. Получено: %', NEW.unit_cost;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validate_supply_cost ON puzzlestore_supply;
CREATE TRIGGER trg_validate_supply_cost
BEFORE INSERT OR UPDATE ON puzzlestore_supply
FOR EACH ROW EXECUTE FUNCTION ps_trg_validate_supply_cost();

-- 2. ТРИГГЕР АУДИТА (AFTER)
CREATE OR REPLACE FUNCTION ps_trg_audit_game_price()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.price IS DISTINCT FROM NEW.price THEN
        INSERT INTO ps_price_audit (game_id, game_name, old_price, new_price)
        VALUES (NEW.id, NEW.name, OLD.price, NEW.price);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_game_price ON puzzlestore_boardgame;
CREATE TRIGGER trg_audit_game_price
AFTER UPDATE ON puzzlestore_boardgame
FOR EACH ROW EXECUTE FUNCTION ps_trg_audit_game_price();

-- 3. ТРИГГЕР АВТО-ОБНОВЛЕНИЯ (AFTER)
CREATE OR REPLACE FUNCTION ps_trg_update_stock_on_sale()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE puzzlestore_boardgame
    SET current_stock = current_stock - NEW.quantity
    WHERE id = NEW.game_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_stock_on_sale ON puzzlestore_sale;
CREATE TRIGGER trg_update_stock_on_sale
AFTER INSERT ON puzzlestore_sale
FOR EACH ROW EXECUTE FUNCTION ps_trg_update_stock_on_sale();

-- =========================================================================
-- ЗАПРОСЫ ДЛЯ ПРОВЕРКИ ТРИГГЕРОВ (САМЫЕ ВАЖНЫЕ ДЛЯ ОТЧЁТА!)
-- =========================================================================

-- ПРОВЕРКА 1: Триггер валидации (ДОЛЖЕН ВЫДАТЬ КРАСНУЮ ОШИБКУ)
INSERT INTO puzzlestore_supply (game_id, quantity, unit_cost, supply_date)
VALUES (1, 10, -500, CURRENT_TIMESTAMP);

-- ПРОВЕРКА 2: Триггер аудита цен (ДВА ШАГА)
-- Шаг А: Меняем цену игры с ID 1 на 9999
UPDATE puzzlestore_boardgame SET price = 9999 WHERE id = 1;
-- Шаг Б: Смотрим, записал ли триггер это изменение в таблицу логов
SELECT * FROM ps_price_audit ORDER BY changed_at DESC LIMIT 1;

-- ПРОВЕРКА 3: Триггер авто-обновления стока (ТРИ ШАГА)
-- Шаг А: Смотрим текущий остаток игры 1 (запомни число, например, было 10)
SELECT current_stock FROM puzzlestore_boardgame WHERE id = 1;
-- Шаг Б: Делаем продажу 2 штук этой игры
INSERT INTO puzzlestore_sale (game_id, quantity, unit_price, sale_date, user_id, status)
VALUES (1, 2, 5000, CURRENT_TIMESTAMP, 1, 'completed');
-- Шаг В: Снова смотрим остаток (он ДОЛЖЕН уменьшиться на 2, стало 8!)
SELECT current_stock FROM puzzlestore_boardgame WHERE id = 1;