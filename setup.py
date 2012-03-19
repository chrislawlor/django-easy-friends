from setuptools import setup, find_packages


setup(
    name = "django-easy-friends",
    version = "0.2.dev1",
    description = "friendship, friendship invitation and friendship suggestion management for the Django web framework",
    author = "Maciej Marczewski",
    author_email = "maciej@marczewski.net.pl",
    url = "http://github.com/barszczmm/django-easy-friends/",
    packages = find_packages(),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    include_package_data = True,
    package_data = {
        "friends": [
            "templates/notification/*/*.html",
            "templates/notification/*/*.txt",
        ]
    },
    zip_safe = False,
)
