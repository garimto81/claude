# Phase 1: Implementation

**Duration**: Variable (depends on task complexity)
**Input**: Task List from Phase 0.5
**Output**: Production code + tests (1:1 paired)

---

## Overview

Phase 1 is where you write the actual code. The critical rule: **Every implementation file MUST have a corresponding test file**.

**Core Principle**: "Test as you build, not after" - Write tests alongside implementation, never after.

---

## The 1:1 Test Pairing Rule

### What It Means

```
src/auth.py          → tests/test_auth.py
src/api/users.py     → tests/api/test_users.py
src/components/Button.tsx → tests/components/Button.test.tsx
```

**Every** implementation file gets **exactly one** corresponding test file.

### Why This Matters

**Without 1:1 pairing**:
- ❌ Tests written "later" (never happens)
- ❌ Orphaned code with no coverage
- ❌ Rework when bugs found in production
- ❌ Fear of refactoring (no safety net)

**With 1:1 pairing**:
- ✅ Tests exist from day 1
- ✅ Bugs caught early
- ✅ Refactoring confidence
- ✅ Living documentation

---

## Workflow

### Step 1: Pick a Task
```markdown
## Task 1.1: Create authentication module
- [ ] Create `src/auth/oauth.py`
- [ ] Create `tests/auth/test_oauth.py` (1:1 pair)
```

### Step 2: Implement + Test (Same Session)

**Option A: Test First (TDD)**
```bash
# 1. Write failing test
vim tests/auth/test_oauth.py

def test_google_oauth_redirects_to_correct_url():
    oauth = GoogleOAuth()
    url = oauth.get_authorization_url()
    assert "accounts.google.com/o/oauth2" in url

# 2. Run (should fail)
pytest tests/auth/test_oauth.py

# 3. Implement to make it pass
vim src/auth/oauth.py

# 4. Run (should pass)
pytest tests/auth/test_oauth.py -v
```

**Option B: Implementation First**
```bash
# 1. Write implementation
vim src/auth/oauth.py

# 2. Write test (same session!)
vim tests/auth/test_oauth.py

# 3. Run test
pytest tests/auth/test_oauth.py -v
```

**Both are valid. Never skip writing the test.**

### Step 3: Validate Pairing

```bash
# Check that all files are paired
bash scripts/validate-phase-1.sh
```

**Output**:
```
✅ src/auth/oauth.py → tests/auth/test_oauth.py
✅ src/auth/session.py → tests/auth/test_session.py
❌ src/api/users.py → MISSING TEST FILE!

ERROR: Orphaned implementation files detected.
```

---

## Implementation Best Practices

### Code Quality

1. **Follow Style Guide**
   ```python
   # ✅ Good: Clear, documented, typed
   def authenticate_user(email: str, password: str) -> Optional[User]:
       """
       Authenticate user with email and password.

       Args:
           email: User's email address
           password: Plain text password (will be hashed)

       Returns:
           User object if authenticated, None otherwise
       """
       hashed = hash_password(password)
       return db.query(User).filter_by(email=email, password_hash=hashed).first()
   ```

2. **Small Functions** (< 50 lines)
   - Easier to test
   - Easier to understand
   - Easier to reuse

3. **Clear Naming**
   ```python
   # ❌ Bad
   def process(d):
       return d * 2

   # ✅ Good
   def calculate_discounted_price(original_price: Decimal) -> Decimal:
       return original_price * Decimal("0.5")
   ```

4. **DRY (Don't Repeat Yourself)**
   - Extract common logic to utilities
   - Use inheritance/composition wisely
   - Create reusable components

### Security Checklist

**Mandatory checks before committing**:

- [ ] **No Hardcoded Secrets**
  ```python
  # ❌ NEVER
  API_KEY = "sk-1234567890"

  # ✅ ALWAYS
  API_KEY = os.getenv("API_KEY")
  ```

- [ ] **Input Validation**
  ```python
  # ✅ Validate and sanitize
  from pydantic import BaseModel, EmailStr

  class UserInput(BaseModel):
      email: EmailStr
      age: int = Field(ge=0, le=150)
  ```

- [ ] **SQL Injection Prevention**
  ```python
  # ❌ NEVER
  db.execute(f"SELECT * FROM users WHERE email = '{email}'")

  # ✅ ALWAYS use parameterized queries
  db.execute("SELECT * FROM users WHERE email = ?", (email,))
  ```

- [ ] **XSS Prevention**
  ```jsx
  // ✅ React auto-escapes
  <div>{userInput}</div>

  // ❌ Dangerous
  <div dangerouslySetInnerHTML={{__html: userInput}} />
  ```

---

## Testing Requirements

### Unit Tests (Required)

**Coverage target**: 80%+ for all new code

```python
# tests/auth/test_oauth.py
import pytest
from src.auth.oauth import GoogleOAuth

def test_get_authorization_url():
    """Test that authorization URL is correctly formatted"""
    oauth = GoogleOAuth(client_id="test", redirect_uri="http://localhost")
    url = oauth.get_authorization_url()

    assert "accounts.google.com/o/oauth2" in url
    assert "client_id=test" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost" in url

def test_exchange_code_for_token_success():
    """Test successful token exchange"""
    oauth = GoogleOAuth(client_id="test", client_secret="secret")
    # Mock HTTP response
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "access_token": "abc123",
            "expires_in": 3600
        }

        token = oauth.exchange_code("auth_code")
        assert token.access_token == "abc123"

def test_exchange_code_for_token_failure():
    """Test failed token exchange"""
    oauth = GoogleOAuth(client_id="test", client_secret="secret")
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400

        with pytest.raises(OAuthError):
            oauth.exchange_code("invalid_code")
```

### Test Structure

```python
# Standard test structure
def test_function_name_scenario():
    """Clear description of what this tests"""

    # 1. Arrange: Set up test data
    input_data = {"email": "test@example.com"}

    # 2. Act: Execute the function
    result = my_function(input_data)

    # 3. Assert: Verify expectations
    assert result.success is True
    assert result.user.email == "test@example.com"
```

### Edge Cases

Always test:
- Empty inputs (`""`, `[]`, `None`)
- Boundary values (0, MAX_INT, negative numbers)
- Invalid formats (malformed email, etc.)
- Error conditions (network failure, timeout)
- Concurrent access (race conditions)

---

## Tools & Agents

### Development Agents

**debugger** (Use when: bug fixing, unexpected behavior)
```
Success Rate: 81%
Average Duration: 15 seconds
Best For: TypeError, ValueError, logic errors
```

**typescript-expert** (Use when: TypeScript-specific issues)
```
Success Rate: 75%
Average Duration: 20 seconds
Best For: Type definitions, generics, advanced TS patterns
```

**test-automator** (Use when: writing unit/integration tests)
```
Success Rate: 100%
Average Duration: 25 seconds
Best For: Unit tests, integration tests with mock data
```

### Development Commands

```bash
# Run tests locally
pytest tests/auth/test_oauth.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test
pytest tests/auth/test_oauth.py::test_get_authorization_url

# Watch mode (re-run on file change)
pytest-watch tests/
```

---

## Common Patterns

### API Endpoint
```python
# src/api/users.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    name: str

@router.post("/users")
def create_user(user: UserCreate):
    # Validation happens automatically via Pydantic
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    return {"id": db_user.id, "email": db_user.email}
```

```python
# tests/api/test_users.py (1:1 pair)
from fastapi.testclient import TestClient

def test_create_user_success():
    response = client.post("/users", json={
        "email": "test@example.com",
        "name": "Test User"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_create_user_invalid_email():
    response = client.post("/users", json={
        "email": "not-an-email",
        "name": "Test"
    })
    assert response.status_code == 422  # Validation error
```

### Database Model
```python
# src/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="user")
```

```python
# tests/models/test_user.py (1:1 pair)
def test_user_creation():
    user = User(email="test@example.com", name="Test")
    db.add(user)
    db.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.created_at is not None

def test_user_email_unique_constraint():
    user1 = User(email="test@example.com", name="User 1")
    user2 = User(email="test@example.com", name="User 2")

    db.add(user1)
    db.commit()

    db.add(user2)
    with pytest.raises(IntegrityError):
        db.commit()
```

---

## Validation

**Before moving to Phase 2:**

```bash
bash scripts/validate-phase-1.sh
```

**Checks**:
- ✅ All implementation files have 1:1 test pairs
- ✅ No orphaned files
- ✅ Test files are in correct directory structure
- ✅ Tests can be imported successfully

---

## Tips

1. **Commit Often**: Small, focused commits
2. **Run Tests Frequently**: After every function/class
3. **Ask for Help**: Use debugger agent when stuck > 15 minutes
4. **Refactor Early**: Don't accumulate technical debt
5. **Document Complex Logic**: Future you will thank you

---

## Next Steps

After validation passes:
1. **Phase 2**: Run all tests with coverage analysis
2. **Code Review**: Self-review or peer review
3. **Refine**: Clean up, optimize, document

---

**References**:
- [Phase 0.5: Task Generation](01-task-generation.md)
- [Phase 2: Testing](03-testing.md)
- [Agent Usage Best Practices](../AGENT_USAGE_BEST_PRACTICES.md)
