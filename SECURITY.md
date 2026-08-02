# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x (RC-2+) | ✅ Active |
| 1.0.0-rc1 | ⚠️ Security fixes only |
| < 1.0.0-rc1 | ❌ Not supported |

---

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Please report security vulnerabilities by emailing: **security@kuroai.dev**

Include in your report:
1. Description of the vulnerability
2. Steps to reproduce
3. Affected versions
4. Potential impact
5. (Optional) Suggested fix

We will respond within **72 hours** with an acknowledgement and remediation timeline.

---

## Security Design Principles

KuroAI is designed with security-in-depth:

### Prompt Injection Defense
- `PromptSafetyValidator` scans all user-provided prompts before they reach any LLM provider
- Configurable forbidden pattern registry
- Character length limits enforced per-request

### Secret Protection
- `SecretRedactor` masks credentials in all log outputs
- `SecretManager` resolves secrets from environment variables only — never hardcoded
- `.env` is in `.gitignore` by default; `.env.example` contains no real values

### Path Traversal Prevention
- `sanitize_filename()` and `assert_safe_path()` guard all file I/O operations
- Directory traversal patterns (`../`) detected before `os.path` normalization

### Rate Limiting
- `TokenBucketRateLimiter` and `SlidingWindowRateLimiter` protect provider endpoints
- Configurable via `RATE_LIMIT_REQUESTS_PER_MINUTE` environment variable

### Dependency Security
- Dependencies pinned in `requirements-lock.txt`
- GitHub Actions Dependabot configured for automated dependency updates

---

## Known Security Considerations

- KuroAI does not sandbox LLM-generated code execution. If you implement code execution capabilities, you must sandbox them yourself.
- The `SecretManager` reads from environment variables — ensure your deployment environment has proper secret rotation policies.
