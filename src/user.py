#!/usr/bin/env python3.8
import logging

logging.basicConfig(level=logging.INFO)


class User:

    def __init__(self, name):
        self._name = name
        self._image_file_name = "{}_image.png".format(self._name)
        self._feeder_topic = "{}/feeder".format(self._name)
        self._led_topic = "{}/LED".format(self._name)
        self._feeding_times = []

    def add_feeding_times(self, times):
        if type(times) is not list:
            raise TypeError("Times must be a list")
        for time in times:
            if time in times:
                logging.info("{} already exists.".format(time))
            self._feeding_times.append(time)

    @property
    def name(self):
        return self._name

    @property
    def image_file_name(self):
        return self._image_file_name

    @property
    def feeder_topic(self):
        return self._feeder_topic

    @property
    def led_topic(self):
        return self._led_topic

    @property
    def feeding_times(self):
        return self._feeding_times
