from setuptools import setup, find_packages


def get_long_description():
    description = ""
    for name in ("README.rst", "AUTHORS.rst", "CHANGELOG.rst"):
        try:
            fp = open(name, "r")
            description += fp.read()
        except IOError:
            pass
        finally:
            fp.close()
    return description


setup(
    name="django-rss-feed",
    version="0.1",
    description="App that aggregates rss feeds",
    long_description=get_long_description(),
    author="Praekelt Consulting",
    author_email="dev@praekelt.com",
    license="BSD",
    url="https://github.com/praekelt/django-rss-feed/",
    packages=find_packages(),
    dependency_links=[],
    install_requires=[
        "django",
        "feedparser",
        "django-photologue",
        "django-celery",
    ],
    tests_require=[
        "tox",
        "mock",
        "pytz",
        "BeautifulSoup",
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
    include_package_data=True
)
