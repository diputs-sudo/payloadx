from setuptools import setup, find_packages

setup(
    name="pbx",
    version="0.0.2",
    author="diputs",
    author_email="diputs-sudo@proton.me", 
    description="PayloadBuilder X - A modular payload compiler framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/diputs-sudo/payloadx",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'pbx = pbx.main:main',  
        ],
    },
)
