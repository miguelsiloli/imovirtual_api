from setuptools import setup, find_packages

setup(
    name='imovirtual_api',
    version='0.1.0',
    author='Miguel Oliveira',
    author_email='miguelsiloli99@gmail.com',
    description='Wrapper of imovirtual api',
    long_description=open('README.md').read(),
    packages=find_packages(where='src'), 
    package_dir={'': 'src'},
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/mypackage',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    install_requires=[
    ],
    include_package_data=True,
)
