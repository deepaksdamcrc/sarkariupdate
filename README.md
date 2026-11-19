# Sarkari Update

Build: `node worker/server.mjs`. This produces the Worker module at `dist/server/index.js` and generates the public document from the shared presentation source. The public document contains no editor or credential logic.

The Site retains its private Sites audience. The administrator uses the additional username/password login at `/admin`. Configure `ADMIN_USERNAME` and the secret `ADMIN_BOOTSTRAP_PASSWORD_HASH` via Sites runtime environment variables. The bootstrap secret is a JSON object with `salt` (16 random bytes encoded as hex), `hash` (32-byte PBKDF2-SHA256 result encoded as hex), and `iterations` (100000). PBKDF2 uses the UTF-8 encoded hex salt string. No plaintext password belongs in source, build output or environment files.

Credentials are initialized once in R2 and passwords are stored only as salted PBKDF2 hashes. First login requires a password change at `/admin/password`; later changes are available from the dashboard. Changes require the current password and rotate the account version, invalidating prior sessions. The browser stores only an opaque Secure, HttpOnly, SameSite=Strict session cookie. Sessions expire after eight hours; logout revokes the active session. Login failures are throttled per client in a fifteen-minute window.

Public reads: `/`, `/api/articles` (published only), `/covers/:id.svg` (published only). The dashboard and administration APIs require a valid session. Draft covers require authorization and use private/no-store caching. All mutation requests require a matching Origin. Existing article records remain in R2; password changes do not affect articles.

Recurring article publication is documented in `AUTOMATION.md`. The scoped writer uses its own service authentication and never needs the administrator password.

Public articles and public JSON must never expose the reference brand or URL. Provenance remains private for deduplication. Latest official information overrides the reference; publish official-confirmed reports automatically. Only unresolved doubts go to approval drafts. The owner requested hourly checks and no routine permission prompts.
