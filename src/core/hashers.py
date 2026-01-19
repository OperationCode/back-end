"""
Custom password hashers with tuned parameters for web authentication.
"""
from django.contrib.auth.hashers import Argon2PasswordHasher


class TunedArgon2PasswordHasher(Argon2PasswordHasher):
    """
    Argon2 hasher with parameters optimized for web authentication.

    Tuned settings (vs Django defaults):
    - memory_cost: 19456 (19 MB, was 100 MB) - OWASP recommended minimum
    - parallelism: 1 (was 8) - web servers don't benefit from threading
    - time_cost: 2 (unchanged) - number of iterations

    These settings provide ~200-300ms verification time while maintaining
    strong security against GPU/ASIC attacks. Still significantly more secure
    than BCrypt for the same performance.

    References:
    - OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
    - Django default uses 100 MB which is optimized for maximum security but too slow for web
    """
    time_cost = 2
    memory_cost = 19456  # 19 MB (OWASP minimum recommendation)
    parallelism = 1      # Single-threaded for web servers
