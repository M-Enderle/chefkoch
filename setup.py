from setuptools import setup, find_packages

__project__ = "chefkoch_api"
__version__ = "1.0.0"
__description__ = "Python library to retrieve information from chefkoch.de"

with open("README.md", "r") as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name=__project__,
    version=__version__,
    author="Moritz Enderle",
    author_email='contact@moritzenderle.com',
    description=__description__,
    license='MIT',
    packages=find_packages(),
    keywords=["chefkoch", "chefkoch-api", "chefkoch-api", "get_chefkoch", "chefkoch_retrieval", "german"],
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type="text/markdown",
    url="https://github.com/THDMoritzEnderle/chefkoch",
    python_required=">=3.0"
)

install_requires = [
    'beautifulsoup4',
    'requests'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires, include_package_data=True)
