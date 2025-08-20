-- 1. How many food providers and receivers are there in each city?
SELECT city,
       COUNT(DISTINCT p.provider_id) AS total_providers,
       COUNT(DISTINCT r.receiver_id) AS total_receivers
FROM providers p
FULL JOIN receivers r USING (city)
GROUP BY city;


--2. Which type of food provider contributes the most food?
SELECT provider_type,
       SUM(quantity) AS total_quantity
FROM food_listings
GROUP BY provider_type
ORDER BY total_quantity DESC
LIMIT 1;



-- 3. What is the contact information of food providers in a specific city? (example: East Sheena
)
SELECT name, contact
FROM providers
WHERE city = 'East Sheena';


-- 4. Which receivers have claimed the most food?
SELECT r.name,
       COUNT(c.claim_id) AS total_claims
FROM receivers r
JOIN claims c ON r.receiver_id = c.receiver_id
GROUP BY r.name
ORDER BY total_claims DESC
LIMIT 5;


-- 5. What is the total quantity of food available from all providers?
SELECT SUM(quantity) AS total_available_food
FROM food_listings;


-- 6. Which city has the highest number of food listings?
SELECT p.city,
       COUNT(f.food_id) AS total_listings
FROM food_listings f
JOIN providers p ON f.provider_id = p.provider_id
GROUP BY p.city
ORDER BY total_listings DESC
LIMIT 1;



-- 7. What are the most commonly available food types?
SELECT food_type,
       COUNT(*) AS total_listings
FROM food_listings
GROUP BY food_type
ORDER BY total_listings DESC;


-- 8. How many food claims have been made for each food item?
SELECT f.food_name,
       COUNT(c.claim_id) AS total_claims
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
GROUP BY f.food_name
ORDER BY total_claims DESC;



-- 9. Which provider has had the highest number of successful food claims?
SELECT p.name,
       COUNT(c.claim_id) AS successful_claims
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
JOIN providers p ON f.provider_id = p.provider_id
WHERE c.status = 'Completed'
GROUP BY p.name
ORDER BY successful_claims DESC
LIMIT 1;



-- 10. What percentage of food claims are completed vs. pending vs. canceled?
SELECT status,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM claims), 2) AS percentage
FROM claims
GROUP BY status;

-- 11. What is the average quantity of food claimed per receiver?
SELECT r.name,
       ROUND(AVG(f.quantity), 2) AS avg_quantity
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
JOIN receivers r ON c.receiver_id = r.receiver_id
GROUP BY r.name
ORDER BY avg_quantity DESC;



-- 12. Which meal type is claimed the most?
SELECT f.meal_type,
       COUNT(c.claim_id) AS total_claims
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
GROUP BY f.meal_type
ORDER BY total_claims DESC
LIMIT 1;



-- 13. Total quantity of food donated by each provider
SELECT p.name,
       SUM(fl.quantity) AS total_donated
FROM food_listings fl
JOIN providers p ON fl.provider_id = p.provider_id
GROUP BY p.name
ORDER BY total_donated DESC;

-- 14. Expired food count
SELECT COUNT(*) AS expired_food_count
FROM food_listings
WHERE expiry_date < CURRENT_DATE;


-- 15. Near-expiry donations (≤ 3 days)
SELECT *
FROM food_listings
WHERE expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '3 days';


-- 16. Providers with surplus food in last 7 days
SELECT p.name,
       SUM(f.quantity) AS total_quantity
FROM providers p
JOIN food_listings f ON p.provider_id = f.provider_id
WHERE f.expiry_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY p.name
ORDER BY total_quantity DESC;


-- 17. Location-wise most common food type
SELECT location,
       food_type,
       COUNT(*) AS count_food_type
FROM food_listings
GROUP BY location, food_type
ORDER BY location, count_food_type DESC;


-- 18. Average quantity per provider
SELECT p.name,
       ROUND(AVG(f.quantity), 2) AS avg_quantity
FROM providers p
JOIN food_listings f ON p.provider_id = f.provider_id
GROUP BY p.name
ORDER BY avg_quantity DESC;


-- 19. Top cities with most expired donations
SELECT p.city,
       COUNT(*) AS expired_count
FROM food_listings f
JOIN providers p ON f.provider_id = p.provider_id
WHERE expiry_date < CURRENT_DATE
GROUP BY p.city
ORDER BY expired_count DESC;


-- 20. Monthly donation trends
SELECT TO_CHAR(expiry_date, 'YYYY-MM') AS month,
       COUNT(*) AS total_donations
FROM food_listings
GROUP BY month
ORDER BY month;

