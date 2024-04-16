CREATE TABLE IF NOT EXISTS apartments (
    url varchar(100) PRIMARY KEY,
    table_dump text NOT NULL,
    description text NOT NULL,
    created_at TIMESTAMP NOT NULL
    );