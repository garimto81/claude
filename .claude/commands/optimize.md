---
name: optimize
description: Analyze code performance and identify bottlenecks
---

# /optimize - Performance Optimizer

Analyze code performance to identify bottlenecks with optimization proposals.

## 연동 에이전트

| 영역 | 에이전트 | 역할 |
|------|----------|------|
| 성능 분석 | `performance-engineer` | 병목 식별 |
| DB 최적화 | `database-optimizer` | 쿼리 개선 |
| 코드 리뷰 | `code-reviewer` | 최적화 검증 |

## Usage

```
/optimize [file-path]
```

Omit `file-path` to analyze entire project.

## Analysis Steps

### 1. Performance Profiling

**Python**:
```bash
# CPU profiling
python -m cProfile -o output.prof src/main.py

# Memory profiling
python -m memory_profiler src/main.py

# Line profiling
kernprof -l -v src/main.py
```

**Node.js**:
```bash
# CPU profiling
node --prof app.js

# Heap profiling
node --inspect app.js
```

### 2. Bottleneck Detection

Identifies:
- **Slow functions** (>100ms)
- **Memory leaks**
- **N+1 queries**
- **Blocking operations**
- **Large loops** (>1000 iterations)

### 3. Optimization Suggestions

**Common Patterns**:

1. **Database Queries**
   ```python
   # ❌ Bad: N+1 query
   for user in users:
       posts = Post.query.filter_by(user_id=user.id).all()

   # ✅ Good: Eager loading
   users = User.query.options(joinedload(User.posts)).all()
   ```

2. **Caching**
   ```python
   # ❌ Bad: Repeated calculation
   def get_stats():
       return expensive_calculation()

   # ✅ Good: Cache result
   @lru_cache(maxsize=128)
   def get_stats():
       return expensive_calculation()
   ```

3. **Async Operations**
   ```python
   # ❌ Bad: Sequential I/O
   result1 = fetch_api_1()
   result2 = fetch_api_2()

   # ✅ Good: Concurrent I/O
   results = await asyncio.gather(
       fetch_api_1(),
       fetch_api_2()
   )
   ```

### 4. Performance Metrics

Target benchmarks:
- **API Response**: <500ms (p95)
- **Database Query**: <100ms
- **Page Load**: <3s
- **Memory Usage**: <512MB

## Phase Integration

### Phase 1: Implementation
- `/optimize` during development
- Catch issues early

### Phase 5: E2E & Performance
- Mandatory before production
- Load testing with optimization

### Phase 6: Deployment
- Final performance check
- Production benchmarks

## Output Format

```
⚡ Performance Analysis Report

📊 Profiling Results:
   • Total execution time: 2.45s
   • Top bottleneck: database_query() - 1.8s (73%)

🔍 Identified Issues:
   1. [CRITICAL] N+1 query in src/api/users.py:45
      → Suggestion: Use joinedload()
      → Impact: -80% query time

   2. [HIGH] Blocking I/O in src/services/fetch.py:12
      → Suggestion: Use async/await
      → Impact: -60% response time

   3. [MEDIUM] Large loop in src/utils/process.py:78
      → Suggestion: Use list comprehension
      → Impact: -30% CPU time

💡 Quick Wins:
   • Add index on users.email column
   • Enable query result caching
   • Batch database inserts

📈 Estimated Improvement:
   • Response time: 2.45s → 0.58s (-76%)
   • Memory usage: 425MB → 180MB (-58%)
```

## Integration with Agents

- **performance-engineer**: Deep analysis
- **database-optimizer**: Query optimization
- **application-performance** plugin

## Related

- `/check` - Code quality
- `application-performance` plugin
- Phase 5 performance testing
- Load testing scripts
