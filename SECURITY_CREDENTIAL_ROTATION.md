# Security incident response — public repo credential exposure

While auditing this repository we found committed populated PostgreSQL connection information and admin token values in root/backend/frontend `.env` files. The same database URL had been copied into `backend/render.yaml` and an import script; generated `repopack-output.txt` files contained token references.

## Owner action — urgent

1. **Immediately revoke/rotate the PostgreSQL password** in the database provider and verify the old login can no longer connect.
2. **Revoke/rotate all ADMIN_TOKEN values**, invalidate dependent sessions/integrations, and remove any token placed in frontend environment variables.
3. Rotate/restrict Mapbox tokens: public map tokens must have the narrowest API and URL/referrer scope; never use a secret token in client code.
4. Audit provider access logs, running services, deployments, forks and old clones for unauthorized activity.
5. Configure the new secrets only in provider dashboards or private local environment files, not in Git or frontend bundles.
6. Coordinate any Git history rewrite only after rotation and backup. Deleted files remain accessible in old commits, forks, caches, or clones.

Current source no longer has the public admin data-loading route. Import data through a separately authorized maintenance process with least-privilege credentials. This patch is not a complete external penetration test or production deployment certification.
