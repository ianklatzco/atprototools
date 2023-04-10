from setuptools import setup, find_packages

setup(
    name='atprototools',
    version='0.0.8',
    description='tools for posting / deleting things from bsky, in python',
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
