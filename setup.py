from setuptools import setup, find_packages

with open('requirements.txt') as req_f:
    requirements = req_f.readlines()

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    author="Oleksandr Semeniuta",
    author_email='oleksandr.semeniuta@gmail.com',
    name='epypes',
    version='0.1.dev0',
    packages=find_packages(include=['epypes']),
    license='BSD license',
    long_description=readme,
    install_requires=requirements,
    test_suite='test',
    tests_require=['pytest'],
)
