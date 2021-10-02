from setuptools import setup

from beancount_bot import __VERSION__

with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='beancount-bot',
    version=__VERSION__,
    packages=['beancount_bot', 'beancount_bot.builtin'],
    url='https://github.com/kaaass/beancount_bot',
    entry_points={
        "console_scripts": [
            'beancount_bot = beancount_bot:main'
        ]
    },
    install_requires=install_requires,
    python_requires='>=3.6.0',
    license='MIT',
    author='KAAAsS',
    author_email='admin@kaaass.net',
    description='A telegram bot designed for Beancount',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
