from pathlib import Path

from setuptools import setup

__VERSION__ = "1.2.1"

root = Path(__file__).parent
long_description = (root / "README.md").read_text()

# 写版本号
with open("beancount_bot/__version__.py", "w") as f:
    f.write(f"__VERSION__ = '{__VERSION__}'")

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
    install_requires=[
        'beancount==2.*',
        'click==8.0.4',
        'pyTelegramBotAPI==4.1.0',
        'PyYAML==5.4.1',
        'schedule==1.1.0',
    ],
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
