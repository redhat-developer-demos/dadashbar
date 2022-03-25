import os

DEBUG = False
TESTING = False
CSRF_ENABLED = True
SECRET_KEY = os.getenv('SECRET_KEY','2621a03cd4e5881cac070d675dac75d2d973c46f466aa1b5')
ADMIN_USER = os.getenv('ADMIN_USER', 'admin@email.tld')
ADMIN_PASS = os.getenv('ADMIN_PASS', '_some_difficult_pass@')