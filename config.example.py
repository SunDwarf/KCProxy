### Copy this to `config.py`.

# The chosen server to use for requests.
# Make sure NOT to include a `http` prefix or any full paths.
SERVER_IP = "125.6.188.25"

# The local file storage location to load modified files from.
STORAGE_LOCATION = "./modified_files"

# The port to serve on.
PORT = 7869

# The host to bind to.
HOST = "127.0.0.1"

# Enable in-memory caching?
ENABLE_CACHE = True

# The redis host to use.
REDIS_HOST = "127.0.0.1"

# The redis port to use.
REDIS_PORT = 6379

# The redis DB to use.
REDIS_DB = 0

# The amount of time to cache requests.
# Default: 300 seconds (5 minutes.)
CACHE_TIME = 300