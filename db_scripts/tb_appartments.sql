CREATE TABLE public.tb_apartments
(
    tb_apartment_id serial PRIMARY KEY NOT NULL,
    country_region VARCHAR(255),
    country VARCHAR(255),
    city VARCHAR(255) NOT NULL,
    city_region VARCHAR(255),
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    close_price REAL NOT NULL,
    distance_to_bus REAL,
    distance_to_school REAL,
    distance_to_shopping REAL
);
CREATE UNIQUE INDEX appartments_appartment_id_uindex ON public.appartments (appartment_id);