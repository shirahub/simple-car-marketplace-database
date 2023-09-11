
# simple-car-marketplace-database


## Transactional Query


1. Mencari mobil keluaran 2015 ke atas
    ```
    select p.id, b.name, m.name, t.name, year, price
    from products p
            join models m on p.model_id = m.id
            join types t on m.type_id = t.id
            join brands b on m.brand_id = b.id
    where year >= 2015
    ```

1. Menambahkan satu data bid produk baru
    ```
    insert into bids (account_id, product_id, price, status)
    values (1, 1, 175000001, 'sent')
    ```
1. Melihat semua mobil yg dijual 1 akun dari yg paling baru
    ```
    select p.id,
       a.name as seller_name,
       b.name,
       m.name,
       t.name,
       year,
       price,
       p.created_at
    from products p
            join models m on p.model_id = m.id
            join types t on m.type_id = t.id
            join brands b on m.brand_id = b.id
            join accounts a on a.id = p.account_id
    where a.created_at = (select max(created_at) from accounts)
    ``` 
1. Mencari mobil bekas yang termurah berdasarkan keyword
    ```
    select p.id, b.name, m.name, t.name, year, price
    from products p
            join models m on p.model_id = m.id
            join types t on m.type_id = t.id
            join brands b on m.brand_id = b.id
    where m.name ilike '%yaris%'
    order by price asc
    ```


1. Mencari mobil bekas yang terdekat berdasarkan sebuah id kota, jarak terdekat dihitung berdasarkan latitude longitude. Perhitungan jarak dapat dihitung menggunakan rumus jarak euclidean berdasarkan latitude dan longitude.

    ```
    CREATE OR REPLACE FUNCTION calculate_euclidean_distance(
        p1 point,
        city_id integer
    )
        RETURNS double precision AS
    $$
    DECLARE
        p2       point;
        x_diff   double precision;
        y_diff   double precision;
        distance double precision;
    BEGIN
        -- Mengambil koordinat dari tabel "cities" berdasarkan id
        SELECT location INTO p2 FROM cities WHERE id = city_id;

        -- Menghitung selisih antara koordinat x dan y dari kedua data point
        x_diff := p2[0] - p1[0];
        y_diff := p2[1] - p1[1];

        -- Menggunakan rumus Euclidean untuk menghitung jarak
        distance := sqrt(x_diff * x_diff + y_diff * y_diff);

        RETURN distance;
    END;
    $$
        LANGUAGE plpgsql;

    select p.id, b.name, m.name, calculate_euclidean_distance(c.location, 3171) as distance
    from products p
            join models m on p.model_id = m.id
            join types t on m.type_id = t.id
            join brands b on m.brand_id = b.id
            join cities c on c.id = p.city_id
    where c.id = 3172
    order by distance asc
    ```

## Analytical Query
1. Ranking Popularitas model mobil berdasarkan jumlah bid
    ```
    with bids_summary as (
        select m.name, count(b.id) as count_bid
        from bids b
                join products p on p.id = b.product_id
                join models m on p.model_id = m.id
        group by m.name
    )
    select m.name, count(p.id), bs.count_bid
    from products p
            join models m on m.id = p.model_id
            join bids_summary bs on m.name = bs.name
    group by m.name, bs.count_bid
    order by count_bid desc
    ```

1. Membandingkan harga mobil berdasarkan harga rata-rata per kota
    ```
    select c.name,
        b.name as brand,
        m.name as model,
        t.name as body_type,
        year,
        price,
        avg(price) over (partition by city_id)
    from products p
            join cities c on c.id = p.city_id
            join models m on p.model_id = m.id
            join brands b on m.brand_id = b.id
            join types t on t.id = m.type_id
    order by city_id asc
    ```

1. Dari penawaran suatu model mobil, cari perbandingan tanggal user melakukan bid dengan bid selanjutnya beserta harga tawar yang diberikan
    ```
    select m.name                                                                             as model,
        b.account_id,
        date(b.created_at)                                                                 as first_bid_date,
        lead(date(b.created_at), 1) over (partition by b.account_id order by b.created_at) as next_bid_date,
        b.price                                                                            as first_bid_price,
        lead(b.price, 1) over (partition by b.account_id order by b.created_at)            as next_bid_price
    from products p
            join models m on p.model_id = m.id
            join bids b on p.id = b.product_id
    where p.id = 1
    ```
1. Membandingkan persentase perbedaan rata-rata harga mobil berdasarkan modelnya dan rata-rata harga bid yang ditawarkan oleh customer pada 6 bulan terakhir 
    ```
    with cte as (
        select m.name                                                                                as model,
            t.name                                                                                as body_type,
            avg(p.price)                                                                          as avg_price,
            avg(CASE WHEN b.created_at >= NOW() - INTERVAL '6 months' THEN b.price ELSE NULL END) AS avg_bid_6month
        from products p
                join models m on p.model_id = m.id
                join types t on t.id = m.type_id
                join bids b on p.id = b.product_id
        group by m.id, t.id
    )
    select model,
        body_type,
        avg_price,
        avg_bid_6month,
        (avg_bid_6month - avg_price)                     as difference,
        ((avg_bid_6month - avg_price) / avg_price) * 100 as difference_percent
    from cte
    ```
1. Membuat window function rata-rata harga bid sebuah merk dan model mobil selama 6 bulan terakhir
    ```
    WITH Last6MonthsBids AS (
        SELECT m.name                                                                                                                             AS model_name,
            avg(b.price)
            over (partition by m.name order by DATE_TRUNC('month', b.created_at) range between unbounded preceding and current row )           as avg_6_bulan_terakhir,
            avg(b.price)
            over (partition by m.name order by DATE_TRUNC('month', b.created_at) range between interval '5 months' preceding and current row ) as avg_5_bulan_terakhir,
            avg(b.price)
            over (partition by m.name order by DATE_TRUNC('month', b.created_at) range between interval '4 months' preceding and current row ) as avg_4_bulan_terakhir,
            avg(b.price)
            over (partition by m.name order by DATE_TRUNC('month', b.created_at) range between interval '3 months' preceding and current row ) as avg_3_bulan_terakhir,
            avg(b.price)
            over (partition by m.name order by DATE_TRUNC('month', b.created_at) range between interval '2 months' preceding and current row ) as avg_2_bulan_terakhir,
            avg(b.price)
            over (partition by m.name order by DATE_TRUNC('month', b.created_at) range between interval '1 months' preceding and current row ) as avg_1_bulan_terakhir,
            row_number() over (partition by m.name order by b.created_at desc)                                                                 as rn
        FROM models m
                JOIN
            products p ON m.id = p.model_id
                JOIN
            bids b ON p.id = b.product_id
        WHERE b.created_at >= DATE_TRUNC('month', now()) - INTERVAL '6 months'
        order by b.created_at
    )
    SELECT *
    FROM Last6MonthsBids
    where rn = 1
    ORDER BY model_name;
    ```
