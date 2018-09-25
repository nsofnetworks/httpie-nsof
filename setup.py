from setuptools import setup

VERSION = '1.1'
GITHUB_URL = 'https://github.com/nsofnetworks/httpie-nsof'
ARCHIVE_URL = GITHUB_URL + "/archive/%s.tar.gz"

setup(
    name='httpie-nsof',
    description='Nsof OAuth 2 plugin for HTTPie.',
    long_description=open('README.rst').read().strip(),
    version=VERSION,
    author='Alon Horowitz',
    author_email='alon@nsof.io',
    license='Apache License 2.0',
    url=GITHUB_URL,
    download_url=ARCHIVE_URL % VERSION,
    py_modules=['httpie_nsof'],
    scripts=['httpie-nsof-setup'],
    zip_safe=False,
    entry_points={
        'httpie.plugins.auth.v1': [
            'httpie_nsof = httpie_nsof:NsofAuthPlugin'
        ]
    },
    install_requires=[
        'httpie>=0.7.0',
        'pyjwt>=1.4.2'
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
