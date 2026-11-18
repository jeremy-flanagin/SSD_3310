SELECT 'CREATE ROLE postgres WITH LOGIN PASSWORD ''postgres'''
WHERE NOT EXISTS (
  SELECT 1 FROM pg_roles WHERE rolname = 'postgres'
)
\gexec

SELECT 'CREATE DATABASE library_system OWNER postgres'
WHERE NOT EXISTS (
  SELECT 1 FROM pg_database WHERE datname = 'library_system'
)
\gexec