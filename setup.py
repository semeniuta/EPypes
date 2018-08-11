from setuptools import setup, find_packages

requirements = ['pyzmq', 'protobuf', 'networkx']

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    author="Oleksandr Semeniuta",
    author_email='oleksandr.semeniuta@gmail.com',
    name='epypes',
    version='0.1dev',
    packages=find_packages(include=['epypes']),
    license='BSD license',
    long_description=readme,
    install_requires=requirements,
    test_suite='test',
    tests_require=['pytest'],
)
