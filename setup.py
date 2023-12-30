# write me a setup script for this python package
from setuptools import setup, find_packages

setup(
    name="dashgpt",
    version="0.0.1",
    description="A Plotly Dash GPT Chat app.",
    author="Ty Andrews",
    packages=find_packages("src"),
    package_dir={"": "src"},
)
