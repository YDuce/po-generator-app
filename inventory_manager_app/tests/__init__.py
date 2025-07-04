# Ensure a default secret key for settings before tests import modules
import os

os.environ.setdefault("APP_SECRET_KEY", "test-secret")

# test package
