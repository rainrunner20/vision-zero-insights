# Vision Zero Insights — NYC traffic crash research prototype

An exploratory React / Mapbox visualization and Flask / PostgreSQL backend for investigating NYC traffic crash records. This is **not an operational crash-warning system** or validated injury forecast. Published files are research source code, not proof of a working hosted deployment.

## Security update

The original public repository contained a PostgreSQL connection string and admin tokens in `.env` files, a deployment blueprint, data-loading code, and generated repository snapshots. Those secrets were removed from the active tree, and the public HTTP administrative data upload was removed. **The original credentials must still be revoked/rotated at the provider**; historical Git commits and clones may retain them.

Never put `DATABASE_URL` or an administrator token into `VITE_*` variables: Vite exposes those values in the browser bundle.

## Implemented and verified locally via CI

- A read-only Flask API for recent crash records and bounding-box filtering with parameterized SQL.
- Request validation and sanitized API error responses without a database-dependent health check.
- An experimental low/high severity classification endpoint with explicit input checks (not a measured injury count or reliable prediction).
- Vite frontend build and Mapbox map when a **restricted public** Mapbox browser token is configured.
- Automated API tests without provider credentials, plus frontend build checks.

## Local setup (Windows PowerShell)

Use a **fresh database credential** in a local environment file, not in Git.

```powershell
cd backend
py -m pip install -r requirements.txt
$env:DATABASE_URL = "<your rotated PostgreSQL connection string>"
$env:VISIONZERO_ALLOWED_ORIGINS = "http://localhost:5173"
py app.py
```

Then in another terminal:

```powershell
cd vision-zero-frontend
npm ci
# Set VITE_MAPBOX_PUBLIC_TOKEN to a token restricted to your domain and allowed APIs.
npm run dev
```

Use `py -m unittest discover -s backend/tests -v` from the root for offline checks. External DB/model integration has not been verified. Before production use, audit SQL privileges, map token restrictions, authentication, provenance, and independent evaluation.

See [credential response](SECURITY_CREDENTIAL_ROTATION.md) for the mandatory owner actions.
