CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Documents (
    document_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    last_modified_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE Document_Owners (
    document_id INTEGER REFERENCES documents(document_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    PRIMARY KEY (document_id, user_id)
);

CREATE TABLE Versions (
    document_id INTEGER REFERENCES documents(document_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL CHECK (version_number >= 0),
    mongo_id VARCHAR(24) NOT NULL,
    modified_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (document_id, version_number)
);

CREATE TABLE Refresh_Tokens (
    token_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    token_hex VARCHAR(64) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE Documents 
ADD COLUMN current_version_number INTEGER; -- To avoid cyclical dependency --

ALTER TABLE Documents 
ADD CONSTRAINT fk_current_version 
FOREIGN KEY (document_id, current_version_number) 
REFERENCES Versions(document_id, version_number);
