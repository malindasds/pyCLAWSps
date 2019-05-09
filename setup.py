from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pyCLAWSps',
      version       ='0.1.7',
      description   ='Python Code for Power Supply Hamamatsu c11204-01/02',
      long_description=readme(),
      keywords      ='python hamamatsu power supply c11204',
      url           ='https://github.com/malindasds/pyCLAWSps',
      author        ='Malinda de Silva',
      author_email  ='desilva@mpp.mpg.de',
      license       ='gpl-3.0',
      packages      =['pyCLAWSps'],
      install_requires=['pySerial','numpy'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        ],
      zip_safe      =False)
