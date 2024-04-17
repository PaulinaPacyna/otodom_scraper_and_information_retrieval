CREATE TABLE IF NOT EXISTS apartments (
    url varchar(100) PRIMARY KEY,
    table_dump text NOT NULL,
    description text NOT NULL,
    created_at TIMESTAMP NOT NULL
    );

CREATE TYPE BOOL_WITH_NA AS ENUM ('true', 'false', 'no_information');

CREATE TABLE IF NOT EXISTS retrieved_information (
    url varchar(100) PRIMARY KEY,
    long_answer text NOT NULL,
    mortgage_register BOOL_WITH_NA NOT NULl,
    lands_regulated BOOL_WITH_NA NOT NULl,
    rent_administration_fee FLOAT NULl,
    two_sided BOOL_WITH_NA NOT NULl
    );