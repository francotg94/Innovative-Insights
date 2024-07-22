select f.title, sum(p.amount) as revenue from payment as p
JOIN rental r ON p.rental_id = r.rental_id
JOIN inventory i on r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
GROUP BY f.title
ORDER by sum(p.amount) DESC;
