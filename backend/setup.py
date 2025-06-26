from setuptools import setup, find_packages

setup(
    name="health_fitness_planner",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "agno",
        "google-generativeai",
        "python-dotenv",
    ],
) 