CREATE TABLE providers (
    provider_id INT PRIMARY KEY,
    name TEXT,
    type TEXT,
    address TEXT,
    city TEXT,
    contact TEXT
);

 -- Create table Receivers
CREATE TABLE receivers (
    receiver_id INT PRIMARY KEY,
    name TEXT,
    type TEXT,
    city TEXT,
    contact TEXT
);

-- Create table Food_Listing
CREATE TABLE food_listings (
    food_id INT PRIMARY KEY,
    food_name TEXT,
    quantity INT,
    expiry_date DATE,
    provider_id INT REFERENCES providers(provider_id),
    provider_type TEXT,
    location TEXT,
    food_type TEXT,
    meal_type TEXT
);

-- create table claims
CREATE TABLE claims (
    claim_id INT PRIMARY KEY,
    food_id INT REFERENCES food_listings(food_id),
    receiver_id INT REFERENCES receivers(receiver_id),
    status TEXT,
    timestamp TIMESTAMP
);