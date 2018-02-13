-- TODO: compare with builder-base-formula scripts
-- doesn't get executed!
CREATE USER app_user WITH PASSWORD 'app_password';
GRANT ALL PRIVILEGES ON DATABASE profiles TO app_user;
