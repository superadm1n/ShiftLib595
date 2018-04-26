from distutils.core import setup

description = '''This package was designed to act as a driver for the 74HC959 shift register 
handling the low level operations for clearing, loading, and outputting data to and from the register'''

setup(
    name='ShiftLib959',
    version='0.1.0',
    packages=['ShiftLib959'],
    keywords='Shift Register Driver Library',
    url='https://github.com/superadm1n/ShiftLib959',
    license='MIT',
    author='Kyle Kowalczyk',
    author_email='kowalkyl@gmail.com',
    description='Driver for 74HC959 Shift Register',
    long_description=description,
)