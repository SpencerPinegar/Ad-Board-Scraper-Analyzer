from setuptools import setup

def readme():
      with open('README.rst') as file:
            return file.read()

setup(name='Messenger_Pigeon',
      version='0.1',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Topic :: Car Analytics :: Dealerships',
            'License :: OSI Approved :: GNU AGLv3',
            'Programming Language :: Python :: 3.6.1'
      ],
      keywords='analytics, webscraping, cars, value',
      python_requires='>3.5',
      description='Grabs and Analyzes car listings, notifying you about good deal',
      author='Spencer J Pinegar',
      license='GNU AGLv3',
      url='',
      author_email='SpencerJPinegar@gmail.com',
      packages=['Messenger_Pigeon'],
      install_requires=[
            're',
            'selenium',
            'fuzzywuzzy',
            'requests',
            'bs4',
            'csv',
            'datetime',
            'twilio',
            'pymysql',
            'textblob',
            'proxybroker', 'nose',
      ],
      zip_safe=False
      )