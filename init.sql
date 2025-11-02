-- init.sql
-- Crear extensión para mejores tipos de datos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de usuarios
CREATE TABLE users (
  "id" SERIAL PRIMARY KEY,
  "telegram_id" TEXT UNIQUE NOT NULL,
  "username" TEXT,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de gastos
CREATE TABLE expenses (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL REFERENCES users("id") ON DELETE CASCADE,
  "description" TEXT NOT NULL,
  "amount" MONEY NOT NULL,
  "category" TEXT NOT NULL,
  "added_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_expenses_user_id ON expenses("user_id");
CREATE INDEX idx_expenses_added_at ON expenses("added_at");
CREATE INDEX idx_expenses_category ON expenses("category");

-- Insertar usuarios de prueba (whitelist)
INSERT INTO users (telegram_id, username) VALUES 
  ('123456789', 'test_user_1'),
  ('987654321', 'test_user_2');

-- Insertar gastos de ejemplo
INSERT INTO expenses (user_id, description, amount, category) VALUES
  (1, 'Pizza delivery', 20.00, 'Food'),
  (1, 'Uber to work', 15.50, 'Transportation'),
  (2, 'Monthly rent', 800.00, 'Housing');