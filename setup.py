from setuptools import setup
from beancount_bot import __VERSION__

with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

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
    license='MIT',
    author='KAAAsS',
    author_email='admin@kaaass.net',
    description='A telegram bot designed for Beancount'
)
