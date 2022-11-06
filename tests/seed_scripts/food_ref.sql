CREATE TABLE public.food_ref (
    id varchar NOT NULL,
    "name" varchar NULL,
    "kcal/unit" int4 NULL,
    unit_of_measure varchar NULL,
    CONSTRAINT food_ref_pkey PRIMARY KEY (id)
);

INSERT INTO
    public.food_ref (id, "name", "kcal/unit", unit_of_measure)
VALUES
('a', 'bread', 10, 'g');