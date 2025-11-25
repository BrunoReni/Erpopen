# 🔐 Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Best Practices

### 🔑 Environment Variables

**NEVER commit `.env` files to version control!**

1. **Generate Secure Keys:**
   ```bash
   # Generate SECRET_KEY
   openssl rand -hex 32
   
   # Or use Python
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use Strong Passwords:**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Never use default passwords in production

3. **Rotate Keys Regularly:**
   - SECRET_KEY: Every 90 days
   - Database passwords: Every 180 days
   - API keys: As needed

### 🗄️ Database Security

1. **Development:**
   - SQLite is OK for local development
   - Use file permissions: `chmod 600 dev.db`

2. **Production:**
   - **Always use PostgreSQL** (not SQLite)
   - Use strong database passwords
   - Enable SSL/TLS connections
   - Regular backups (daily recommended)
   - Restrict network access (firewall rules)

### 🌐 CORS Configuration

1. **Development:**
   ```env
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

2. **Production:**
   ```env
   CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```
   - NEVER use `*` (allow all) in production
   - Use HTTPS only (no HTTP)

### 🔒 Authentication & Authorization

1. **JWT Tokens:**
   - Tokens expire after 24 hours (configurable)
   - Refresh tokens not implemented yet (TODO)
   - Store tokens in httpOnly cookies (recommended)

2. **Password Hashing:**
   - Using bcrypt (industry standard)
   - Password complexity enforced

3. **Permissions:**
   - RBAC (Role-Based Access Control) implemented
   - Principle of least privilege

### 📊 Logging

1. **What We Log:**
   - Authentication attempts
   - API requests (INFO level)
   - Errors and exceptions

2. **What We DON'T Log:**
   - Passwords (never!)
   - Secret keys
   - Personal sensitive data (minimized)

3. **Log Rotation:**
   - Automatic rotation at 10MB
   - Keep last 5 backups
   - Logs stored in `backend/logs/`

### 🚀 Deployment Security

1. **Environment:**
   ```env
   ENVIRONMENT=production
   DEBUG=false
   ```

2. **HTTPS:**
   - Always use HTTPS in production
   - Redirect HTTP to HTTPS
   - Use valid SSL certificates (Let's Encrypt)

3. **Firewall:**
   - Only expose necessary ports (80, 443)
   - Block direct database access from internet
   - Use VPN for admin access

4. **Updates:**
   - Keep dependencies updated
   - Monitor security advisories
   - Apply patches promptly

### 🛡️ API Security

1. **Rate Limiting:**
   - Login: 5 attempts/minute
   - API calls: TODO (implement)

2. **Input Validation:**
   - Pydantic validates all inputs
   - SQL injection protected (SQLAlchemy ORM)
   - XSS protection

3. **Error Messages:**
   - Generic messages in production
   - Detailed errors only in development

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: security@yourcompany.com (TODO: add real email)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will:
- Acknowledge within 48 hours
- Provide an initial assessment within 7 days
- Work on a fix with priority based on severity
- Credit you in release notes (if desired)

## 🔍 Security Checklist for Production

Before deploying to production, verify:

- [ ] `.env` file configured with production values
- [ ] `SECRET_KEY` is a strong random value (not default)
- [ ] `DEBUG=false`
- [ ] `ENVIRONMENT=production`
- [ ] Database is PostgreSQL (not SQLite)
- [ ] Database credentials are strong
- [ ] CORS origins limited to your domain only
- [ ] HTTPS enabled with valid certificate
- [ ] Firewall rules configured
- [ ] Log rotation enabled
- [ ] Backups configured and tested
- [ ] All dependencies updated
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] File permissions restricted (chmod 600)
- [ ] Admin password changed from default

## 📚 Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

**Last Updated:** 2025-11-25
**Version:** 1.0.0
