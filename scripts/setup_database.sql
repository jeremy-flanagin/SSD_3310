SELECT 'CREATE ROLE postgres WITH LOGIN PASSWORD ''postgres'''
WHERE NOT EXISTS (
  SELECT 1 FROM pg_roles WHERE rolname = 'postgres'
)

SELECT 'CREATE DATABASE library_system OWNER postgres'
WHERE NOT EXISTS (
  SELECT 1 FROM pg_database WHERE datname = 'project_task'
)