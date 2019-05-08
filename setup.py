from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pyCLAWSps',
      version       ='0.1.3',
      description   ='Python Code for Power Supply Hamamatsu c11204-01/02',
      keywords      ='python hamamatsu power supply c11204',
      url           ='https://github.com/malindasds/pyCLAWSps',
      author        ='Malinda de Silva',
      author_email  ='desilva@mpp.mpg.de',
      license       ='gpl-3.0',
      packages      =['pyCLAWSps'],
      install_requires=['pySerial','numpy'],
      zip_safe      =False)
