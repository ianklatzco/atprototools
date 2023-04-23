from setuptools import setup, find_packages

setup(
    name='atprototools',
    version='0.0.12',
    description='Easy-to-use and ergonomic library for interacting with bluesky, packaged so you can `pip install atprototools` and go.',
    author='Ian Klatzco',
    author_email='iklatzco@gmail.com',
    url='https://github.com/ianklatzco/atprototools',
    packages=find_packages(),
    install_requires=[
        'requests>=2.22.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
