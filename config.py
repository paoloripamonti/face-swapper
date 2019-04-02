import os

# FACE LANDMARKS
FACE_LANDMARKS_PATH = os.path.join("models", "shape_predictor_68_face_landmarks.dat")

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 20

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "4564e6f6d8ff1426ca5c1ca24baf489df36487912a5cf3b0aca2973dfeed8f0a"
SESSION_TIMEOUT = 30  # 30 minutes

# Secret key for signing cookies
SECRET_KEY = "73ef2a4edd7a7fbf07fd5f6faf99674dc0c25a025fd74c221f4c35849e5c0fb3"

# Debug variable turn False in production mode
DEBUG = True
