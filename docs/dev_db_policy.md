# Development Database Policy

The application defaults to SQLite for local development to keep setup simple.
Set `APP_DATABASE_URL` to override the database location. CI and production
should configure this variable with a PostgreSQL URL. When running tests or CI
locally, you can run Postgres with:

```bash
docker run --rm -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16
```

Then point `APP_DATABASE_URL` to that instance. Test helpers create temporary
databases by appending a UUID to the base name and drop them after tests
complete. This deterministic pattern avoids naming collisions in concurrent runs.
