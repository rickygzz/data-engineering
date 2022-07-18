CREATE TABLE IF NOT EXISTS public.user_purchase (
    invoice_number VARCHAR,
    stock_code     VARCHAR NOT NULL,
    detail         VARCHAR,
    quantity       INTEGER NOT NULL,
    invoice_date   DATE NOT NULL,
    unit_price     NUMERIC NOT NULL,
    customer_id    INTEGER,
    country        VARCHAR NOT NULL
);
CREATE INDEX IF NOT EXISTS invoice_number_index ON public.user_purchase (invoice_number);