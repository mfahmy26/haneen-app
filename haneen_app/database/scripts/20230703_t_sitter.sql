CREATE TABLE IF NOT EXISTS t_sitter (
   user_id BIGINT PRIMARY KEY,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   username VARCHAR(50) NOT NULL,
   password VARCHAR(200) NOT NULL,
   email_address VARCHAR(100) UNIQUE NOT NULL,
   phone_number VARCHAR(20) UNIQUE NOT NULL,
   address1 VARCHAR(50) NOT NULL,
   address2 VARCHAR(50),
   city VARCHAR(100) NOT NULL,
   state VARCHAR(3) NOT NULL,
   country VARCHAR(50) NOT NULL,
   zip_code VARCHAR(24) NOT NULL,
   is_active BOOLEAN NOT NULL DEFAULT TRUE,
   created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS t_sitter_user_id_email_address_username ON t_sitter(user_id, email_address, username);



INSERT INTO t_sitter (user_id, first_name, last_name, username, password, email_address, phone_number, address1, address2, city, state, country, zip_code) VALUES (4, 'Baby3', 'Sitter3', 'bsitter3', 'TEST3', 'bsitter3@gmail.com', '4843558923', '43 sassafras ct', null, 'North Brunswick', 'NJ', 'United States', '08902');

