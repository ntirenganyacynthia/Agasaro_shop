INSERT INTO suppliers (supplier_name, email, phone_number, address)
SELECT v.n, v.e, v.p, v.a
FROM (VALUES
    ('Umuganda Traders', 'info@umuganda.example', '0780000003', 'Nyabugogo, Kigali'),
    ('Rwanda Dairy Distributors', 'orders@rwandadairy.example', '0780000004', 'Kimironko, Kigali'),
    ('Musanze Fresh Produce', 'sales@musanzefresh.example', '0780000005', 'Musanze'),
    ('Kimironko Stationers', 'hello@kimironkostationers.example', '0780000006', 'Kimironko, Kigali')
) AS v(n, e, p, a)
WHERE NOT EXISTS (SELECT 1 FROM suppliers s WHERE s.supplier_name = v.n);