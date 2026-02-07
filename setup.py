from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-hub",
    version="1.0.0",
    author="AI Trend App Generator",
    description="Model Context Protocol 服务器发现与管理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zjjczzs/daily-ai-apps",
    py_modules=["mcp_hub"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-hub=mcp_hub:main",
        ],
    },
)
