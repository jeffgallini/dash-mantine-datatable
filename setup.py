import json
from pathlib import Path

from setuptools import setup

here = Path(__file__).parent
package = json.loads((here / "package.json").read_text(encoding="utf-8"))
long_description = (here / "README.md").read_text(encoding="utf-8")

package_name = package["name"].replace(" ", "_").replace("-", "_")
repository_url = "https://github.com/jeffgallini/dash-mantine-datatable"

setup(
    name=package["name"],
    version=package["version"],
    author=package["author"],
    packages=[package_name],
    include_package_data=True,
    package_data={package_name: ["*.js", "*.js.map", "*.json", "*.txt"]},
    license=package["license"],
    description=package.get("description", package_name),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=repository_url,
    project_urls={
        "Homepage": repository_url,
        "Source": repository_url,
        "Tracker": f"{repository_url}/issues",
    },
    install_requires=[
        "dash>=2.0.0",
        "dash-mantine-components>=2.6.0",
        "dash-iconify",
    ],
    extras_require={
        "demo": [
            "yfinance>=0.2.54",
        ],
    },
    classifiers=[
        "Framework :: Dash",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.9",
)
