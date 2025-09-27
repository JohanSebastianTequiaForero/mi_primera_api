CREATE TABLE hotels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  prefix TEXT NOT NULL
);

CREATE TABLE guests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  hotel_id INTEGER NOT NULL,
  role TEXT NOT NULL,
  tipo CHAR(1) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (hotel_id) REFERENCES hotels(id)
);

CREATE INDEX idx_guests_tipo ON guests(tipo);
CREATE INDEX idx_guests_hotel_id ON guests(hotel_id);
