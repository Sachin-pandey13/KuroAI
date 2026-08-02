# Testing Guide

KuroAI includes unit, security, resilience, and stress test suites.

```bash
# Unit tests
pytest tests/ -q --ignore=tests/stress

# Security tests
pytest tests/test_security.py -v

# Resilience tests
pytest tests/test_resilience.py -v

# Stress tests
pytest tests/stress/ -v

# Benchmarks
python -m benchmarks.runner
```
