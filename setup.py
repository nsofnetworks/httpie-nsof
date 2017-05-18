from setuptools import setup


setup(
    name='httpie-nsof',
    description='Nsof OAuth 2 plugin for HTTPie.',
    long_description=open('README.rst').read().strip(),
    version='0.1',
    author='Alon Horowitz',
    author_email='alon@nsof.io',
    license='Apache License 2.0',
    url='https://github.com/nsofnetworks/httpie-nsof',
    py_modules=['httpie_nsof'],
    zip_safe=False,
    entry_points={
        'httpie.plugins.auth.v1': [
            'httpie_nsof = httpie_nsof:NsofAuthPlugin'
        ]
    },
    install_requires=[
        'httpie>=0.7.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Environment :: Plugins',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities'
    ],
    keywords='httpie oauth oauth2 nsof token',
)
