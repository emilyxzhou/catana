from setuptools import setup


setup(
    name='ee250-final',
    packages=['discord_bot', 'rpi_controller'],
    version='1.0.1',
    description='Use Discord and a Raspberry Pi to control an automatic cat feeder.',
    license='MIT',
    author='Emily Zhou, Jocelyn Liu',
    url='https://github.com/emilyxzhou/ee250-final.git',
    install_requires=[
        'discord',
        'paho-mqtt',
        'schedule'
    ],
    python_requires='>=3.6',
)
