INSERT INTO categories (category_name, category_description)
SELECT v.n, v.d
FROM (VALUES
    ('Groceries', 'Everyday food items'),
    ('Dairy & Frozen', 'Yoghurt, ice cream and chilled items'),
    ('Snacks', 'Crisps and light snacks')
) AS v(n, d)
WHERE NOT EXISTS (SELECT 1 FROM categories c WHERE c.category_name = v.n);

INSERT INTO suppliers (supplier_name, email, phone_number, address)
SELECT v.n, v.e, v.p, v.a
FROM (VALUES
    ('Fresh Foods Rwanda', 'orders@freshfoods.example', '0780000002', 'KG 11 Ave, Kigali'),
    ('Kigali Wholesale Ltd', 'sales@kigaliwholesale.example', '0780000001', 'KN 4 Ave, Kigali')
) AS v(n, e, p, a)
WHERE NOT EXISTS (SELECT 1 FROM suppliers s WHERE s.supplier_name = v.n);

INSERT INTO products
    (category_id, supplier_id, product_name, unit_price, cost_price, stock_quantity, reserved_quantity)
SELECT c.category_id, s.supplier_id, v.pname, v.price, v.cost, v.stock, 0
FROM (VALUES
    ('Yoghurt 500ml', 'Dairy & Frozen', 'Fresh Foods Rwanda', 1200, 900, 60),
    ('Chilli Sauce 250ml', 'Groceries', 'Fresh Foods Rwanda', 1500, 1100, 50),
    ('Tomato Sauce 500ml', 'Groceries', 'Fresh Foods Rwanda', 2000, 1500, 50),
    ('Vanilla Ice Cream 1L', 'Dairy & Frozen', 'Fresh Foods Rwanda', 4500, 3500, 30),
    ('Crisps 50g', 'Snacks', 'Kigali Wholesale Ltd', 500, 350, 150)
) AS v(pname, cat, sup, price, cost, stock)
JOIN categories c ON c.category_name = v.cat
JOIN suppliers s ON s.supplier_name = v.sup
WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.product_name = v.pname);