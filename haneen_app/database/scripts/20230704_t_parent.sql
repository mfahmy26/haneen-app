CREATE TABLE IF NOT EXISTS t_parent (
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
   updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   sitter_id BIGINT,
   CONSTRAINT fk_sitter
      FOREIGN KEY(sitter_id) 
	      REFERENCES t_sitter(user_id)
);
CREATE INDEX IF NOT EXISTS t_parent_user_id_email_address_username_sitter_id ON t_parent(user_id, email_address, username, sitter_id);

