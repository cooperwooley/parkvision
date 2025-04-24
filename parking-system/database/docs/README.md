# Setting up PostgreSQL

## 1. Installation
On Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

## 2. Start the service
```bash
sudo service postgresql start
```

## 3. Create a database
```bash
# Login as postgres user
sudo -u postgres psql

# In psql console
CREATE DATABASE parking_system;
CREATE USER parking_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE parking_system TO parking_admin:
\q
```