-- =============================================================================
-- ЛАБОРАТОРНАЯ 5: ИНДЕКСЫ И ПРЕДСТАВЛЕНИЯ
-- =============================================================================

-- 1. ИНДЕКС ДЛЯ КАТАЛОГА: Ускоряет фильтрацию и сортировку на главной странице
-- Зачем: Когда пользователь фильтрует по издателю и сортирует по рейтингу, БД не сканирует всю таблицу.
CREATE INDEX IF NOT EXISTS idx_boardgame_catalog_search 
ON puzzlestore_boardgame (publisher_id, current_stock, rating_avg DESC);

-- 2. ИНДЕКС ДЛЯ ОТЧЕТОВ: Ускоряет поиск продаж по дате и статусу
CREATE INDEX IF NOT EXISTS idx_sale_date_status 
ON puzzlestore_sale (sale_date, status);

-- 3. ОБЫЧНОЕ ПРЕДСТАВЛЕНИЕ (VIEW): Статистика по издателям
-- Зачем: Скрывает сложность JOIN-ов. Django может делать SELECT * FROM ps_v_publisher_stats как из обычной таблицы.
CREATE OR REPLACE VIEW ps_v_publisher_stats AS
SELECT 
    p.id AS publisher_id,
    p.name AS publisher_name,
    COUNT(DISTINCT bg.id) AS total_games_count,
    COALESCE(SUM(s.quantity * s.unit_price), 0) AS total_revenue
FROM puzzlestore_publisher p
LEFT JOIN puzzlestore_boardgame bg ON p.id = bg.publisher_id
LEFT JOIN puzzlestore_sale s ON bg.id = s.game_id
GROUP BY p.id, p.name;

-- 4. ВРЕМЕННОЕ ПРЕДСТАВЛЕНИЕ (TEMP VIEW): Кандидаты на уценку
-- Зачем: Существует только в рамках текущей сессии. Удобно для разовых аналитических задач.
CREATE TEMP VIEW ps_temp_stagnant_games AS
SELECT bg.id, bg.name, bg.price, MAX(s.sale_date) as last_sale_date
FROM puzzlestore_boardgame bg
LEFT JOIN puzzlestore_sale s ON bg.id = s.game_id
GROUP BY bg.id, bg.name, bg.price
HAVING MAX(s.sale_date) < CURRENT_DATE - INTERVAL '60 days' OR MAX(s.sale_date) IS NULL;

-- 5. РОЛЬ ДЛЯ БЕЗОПАСНОСТИ: Только чтение каталога
-- Создаем роль (если её нет) и даем права только на представление, а не на таблицы с ценами поставок!
-- CREATE ROLE puzzlestore_reader;
-- GRANT USAGE ON SCHEMA puzzlestore TO puzzlestore_reader;
-- GRANT SELECT ON puzzlestore.ps_v_publisher_stats TO puzzlestore_reader;

-- =========================================================================
-- ЗАПРОСЫ ДЛЯ ПРОВЕРКИ ИНДЕКСОВ И ПРЕДСТАВЛЕНИЙ
-- =========================================================================

-- ПРОВЕРКА 1: Доказательство работы индекса каталога
EXPLAIN ANALYZE
SELECT id, name, price 
FROM puzzlestore_boardgame
WHERE publisher_id = 1 AND current_stock > 0
ORDER BY rating_avg DESC
LIMIT 10;

-- ПРОВЕРКА 2: Доказательство работы индекса продаж
EXPLAIN ANALYZE
SELECT id, quantity, unit_price 
FROM puzzlestore_sale
WHERE sale_date > CURRENT_DATE - INTERVAL '1 year' 
  AND status = 'completed';

-- ПРОВЕРКА 3: Обычное представление (Покажет красивую таблицу со статистикой)
SELECT * FROM ps_v_publisher_stats 
ORDER BY total_revenue DESC;

-- ПРОВЕРКА 4: Временное представление (Кандидаты на уценку)
-- Покажет игры, которые не продавались 60 дней или не продавались вообще.
SELECT * FROM ps_temp_stagnant_games 
ORDER BY last_sale_date ASC NULLS FIRST;