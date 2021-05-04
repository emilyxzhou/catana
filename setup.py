from setuptools import setup


setup(
    name='ee250-final',
    version='1.0.1',
    packages=['ee250_final'],
    description='Use Discord and a Raspberry Pi to control an automatic cat feeder.',
    license='MIT',
    author='Emily Zhou, Jocelyn Liu',
    url='https://github.com/emilyxzhou/ee250-final.git',
    install_requires=[
        'discord',
        'grovepi',
        'paho-mqtt',
        'pillow',
        'RPi.GPIO',
        'schedule'
    ],
    python_requires='>=3.6',
)
