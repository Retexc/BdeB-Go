# setup.py  (at the root of your repo)
from setuptools import setup, find_packages

setup(
    name="bdeb_gtfs",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=[
        # server & framework
        "flask>=2.0",
        "waitress>=2.0",
        # HTTP calls
        "requests>=2.0",
        # admin dashboard dependencies
        "Flask-Session>=0.4",
        "Flask-SQLAlchemy>=2.5",
        "werkzeug>=2.0",
        # if you use any others, add them here...
    ],
    entry_points={
        "console_scripts": [
            # this lets you do: `bdeb-gfts = bdeb_gfts.main:main`
            "bdeb-gts = bdeb_gtfs.main:main",
        ],
    },
    python_requires=">=3.7",
)
