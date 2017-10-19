from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_examples',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Piotr Gawlowicz, Mikolaj Chwalisz,  Anatolij Zubow',
    author_email='{gawlowicz, chwalisz, zubow}@tkn.tu-berlin.de',
    description='WiSHFUL Examples',
    long_description='WiSHFUL Examples',
    keywords='wireless control',
    install_requires=['pyyaml', 'docopt', 'jsocket', 'oml4py']
)
