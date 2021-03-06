import os
import glob

BASE_DIR = os.path.join(
    glob.glob(os.environ["VIRTUAL_ENV"] + "/lib/*/site-packages")[0],
    "spliceworks"
)

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "rssfeed",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "5432"
    }
}

ROOT_URLCONF = "rssfeed.tests.urls"

INSTALLED_APPS = [
    "celery",
    "rssfeed",
    "rssfeed.tests",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles"
]

MIDDLEWARE_CLASSES = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware"
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

SITE_ID = 1
STATIC_URL = "/static/"
SECRET_KEY = "SECRET_KEY"
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

# Disable celery
TASK_ALWAYS_EAGER = True
BROKER_BACKEND = "memory"
