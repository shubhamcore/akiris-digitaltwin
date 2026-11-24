# Release checks

The pre-upgrade frontend dependency audit reported two high and two moderate advisories. Updated Vite, its React plugin and the affected transitive dependencies in the npm lockfile. The final npm audit reported zero known vulnerabilities. The pinned Python dependency scan likewise reported no matching advisories among the checked packages. These are point-in-time registry results. [npm output](evidence/npm-audit.json) · [Python output](evidence/python-audit.json)

A local pattern scan covered the release tree and reachable public Git blobs, including files inside the previously deleted ZIP. The historical Compose and example environment files contained demo database credentials. The release instead requires a user-supplied disposable password and masks credentials in generation logs. Git history was preserved. No provider token, private-key block or real credential was identified. Pattern matching cannot detect every secret. The distribution excludes .env files, personal resumes, generated model binaries and full databases. The checked-in data excerpt is synthetic. No license was added.

The published PostgreSQL transcript replaces the Windows account name with <local-user>. This privacy edit leaves all measurement values unchanged.
