# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='sbrowser',
    version='0.0.10',
    url='https://github.com/tuaplicacionpropia/webbrowser',
    download_url='https://github.com/tuaplicacionpropia/webbrowser/archive/master.zip',
    author=u'tuaplicacionpropia.com',
    author_email='tuaplicacionpropia@gmail.com',
    description='Python library for automate web browser.',
    long_description='Python library for automate web browser.',
    keywords='web, browser, selenium',
    classifiers=[
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python', 
      'Programming Language :: Python :: 2.7', 
      'Intended Audience :: Developers', 
      'Topic :: Multimedia :: Graphics',
    ],
    scripts=['bin/sbrowser', 'bin/sbrowser.cmd', 'bin/fullscreenshot', 'bin/fullscreenshot.cmd', 'bin/screenshot', 'bin/screenshot.cmd',],
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    license='MIT',
    install_requires=[
        'autopy==0.51',
        'requests==2.20.0',
        'selenium==3.11.0',
        'clipboard==0.0.4',
        'rarfile==3.0',
        'Pillow==3.4.2',
        'pyscreenshot==0.4.2',
    ],
)

