#!/usr/bin/env python
'''
MIT License

Copyright (c) 2018 Kyle Kowalczyk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This module contains code that is designed to run a 74HC959 shift register
'''
import RPi.GPIO as io
import time


class ShiftReg():

    '''
    This class contains the code that on a low level handles interfacing with the register.
    It takes care of loading values into the register, clearing out the register, and sending
    data out of the register.

    Currently you can hook the shift register up to uninterruptable power from a dedicated 3v
    GPIO pin or set it up to one of the GPIO pins, the only thing will change is the way it
    clears the register out.
    '''

    def __init__(self, ds, stcp, shcp, power_pin=None, warnings=False, bitcount=8):

        '''Sets warnings and declares class variables and initializes the GPIO pins
        with their initial values

        :param ds: GPIO pin connected to the data pin for register (goes to serial input pin #14 label: DS)
        :param stcp: GPIO pin connected to the ST_CP pit on the register (for outputting the registers values)
        :param shcp: GPIO pin connected to the SH_CP pin on the register (for loading values into the register)
        :param power_pin: GPIO pin that is supplying power to the shift register
        :param warnings: Setting for GPIO warnings
        :param bitcount: Number of outputs your shift register has
        '''

        io.setwarnings(warnings)
        io.setmode(io.BCM)

        self.power_pin = power_pin

        self.data_pin = ds
        self.clock_pin = shcp
        self.shift_pin = stcp
        self._gpio_init()

        self.bitcount = bitcount

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.clear_register()
        self.clean_gpio()

    def _gpio_init(self):

        '''Sets up GPIO pins for output and gives them their default value

        :return: Nothing
        '''

        # sets GPIO pins for output
        io.setup(self.data_pin, io.OUT)
        io.setup(self.clock_pin, io.OUT)
        io.setup(self.shift_pin, io.OUT)
        if self.power_pin:
            io.setup(self.power_pin, io.OUT)

        # sets default values on GPIO pins
        if self.power_pin:
            io.output(self.power_pin, 1)
        io.output(self.clock_pin, 0)
        io.output(self.data_pin, 0)

    def _list_constructor(self, bit=0):

        ''' Constructs a list of values that corresponds to the bitcount provided
        so that other methods that need a list generated can get a standard one that
        will have the correct number of bits in it.

        :param bit:
        :return:
        '''

        values = []
        for x in range(self.bitcount):
            values.append(bit)

        return values

    def set_bit(self, bit):

        '''Set data pin to value of "bit"

        :param bit: bit value to set the
        :raises ValueError: If the bit supplied is not a 0 or 1 it will raise this error
        :return: False if the pin was unable to be pulled up or down
        '''

        if bit > 1 or bit < 0:
            raise ValueError('Bit value must be 0 or 1, you attempted to set it as {}'.format(bit))

        try:
            io.output(self.data_pin, bit)
        except:
            return False

    def clear_data_pin(self):

        '''Set the data pin to 0 I dont think this is necissary but for
        consistancy purposes when setting value on the data pin I chose
        to always pull it back to 0 regardless if there was signal or not

        :return:
        '''

        try:
            io.output(self.data_pin, 0)
        except:
            return False

    def clear_register(self):

        '''Method to clear out all the memory in the register so they are all Zeros
        This is able to handle if the chip is being driven via a GPIO pin or is being
        fed uninterruptable power.

        :return:
        '''

        if not self.power_pin:
            self.load_register(self._list_constructor(bit=0))

        else:
            io.output(self.power_pin, 0)
            io.output(self.power_pin, 1)
            self.cycle_clock()

    def cycle_clock(self):

        '''This will shift in the current value on the data pin into the register
        Note data is shifted into the register on the high value of the 'clock_pin'
        and we reset it to low so we can shift it high later for the next bit

        :return:
        '''

        try:
            io.output(self.clock_pin, 1)
            io.output(self.clock_pin, 0)
        except:
            return False

    def output_register(self):

        '''This method cycles the ST_CP (storage register clock input) pin high then low and
        that is what sends all of the data inside the storage register out of the parallel pins.

        :return:
        '''

        try:
            io.output(self.shift_pin, 1)
            io.output(self.shift_pin, 0)
            return True
        except:
            return False

        pass

    def load_register(self, array):

        '''This will take a list (array) of numbers with the corresponding number of bits
        that your shift register has and load them into the shift register

        :param array:
        :return:
        '''

        for x in array:
            self.set_bit(x)
            self.cycle_clock()
            self.clear_data_pin()

    def clean_gpio(self):
        io.cleanup()


class LightShow(ShiftReg):

    '''
    This class was written to contain code that was designed to take a line of LED's connected
    to a shift register from lowest pin to highest in order and send light back and forth
    in various fashions across the line of LED's
    '''

    def __init__(self, ds, stcp, shcp, power_pin=None, warnings=False, bitcount=8):
        ShiftReg.__init__(self, ds, stcp, shcp, power_pin, warnings, bitcount)

        self.bitcount = bitcount

    def _handle_register(self, values, left_to_right, wait):

        '''Method to handle loading the register and outputting the register
        values and resetting the register

        :param values: list of bit values to load into the register
        :param left_to_right: True to start on the left, False to start on the right
        :param wait: seconds to wait before clearing out the contents of the register
        :return:
        '''

        if left_to_right is True:
            values.reverse()

        self.load_register(values)
        self.output_register()

        if left_to_right is True:
            values.reverse()

        self.clear_register()
        time.sleep(wait)
        self.output_register()

    def fill_bar(self, left_to_right=True, wait=.5, persistance=False):

        '''Method to pull up each of the register pins in sequence one after the
        other until all of the pins are live

        :param left_to_right: True to start on the left, False to start on the right
        :param wait: Time to pause before loading the second set of values in the register
        :param persistance: True to keep the bar lit up and break, False to pull all the pins down
        :return: Nothing
        '''

        values = self._list_constructor(bit=0)

        for x in range(self.bitcount):
            values[x] = 1

            if left_to_right is True:
                values.reverse()

            self.load_register(values)

            if left_to_right is True:
                values.reverse()

            self.output_register()

            if persistance is True and x == 7:
                return

            self.clear_register()
            time.sleep(wait)
            self.output_register()

    def fill_bar_walkthrough(self, left_to_right=True, wait=.5):

        '''Method to pull up all the pins in sequence and then turn
        them down in the same sequence

        :param left_to_right: True to start on the left, False to start on the right
        :param wait: Time to wait before reloading the register
        :return:
        '''

        self.fill_bar(left_to_right, wait, True)

        time.sleep(wait)

        values = self._list_constructor(bit=1)

        for x in range(self.bitcount):

            values[x] = 0

            self._handle_register(values, left_to_right, wait)

    def bar_wave(self, left_to_right=True, wait=.5):

        '''Method to pull up all the pins from one side to the other and then
        pull them back down in revers order going back the way they came

        :param left_to_right: True to start on the left, False to start on the right
        :param wait: time to wait before clearing out the shift register
        :return:
        '''

        # builds a list of values with the amount of bits the register that can hold
        values = self._list_constructor(bit=0)

        # incrementally turns up the register pins from 0 to 7
        for x in range(self.bitcount):
            # adds one to the element in the list
            values[x] = 1
            # dumps list into the register and outputs the register
            self._handle_register(values, left_to_right, wait)

        # incrementally turns down the register pins in the reverse order from 7 to 0
        for x in range(self.bitcount):
            # reverses list to modify the right side of the list
            values.reverse()
            values[x] = 0
            # reverses the list again to change it to its original orientation
            values.reverse()

            # loads the register, outputs the register, and pauses for some time.
            self._handle_register(values, left_to_right, wait)

    def bit_run(self, left_to_right=True, wait=.5):

        '''Method to pull up one pin at a time and run it across each of the
        register pins from one side to the other

        :param left_to_right: True to start on the left, False to start on the right
        :param wait: time to wait before clearing out the shift register
        :return:
        '''

        # builds a list of values with the amount of bits the register that can hold
        values = self._list_constructor(bit=0)

        for x in range(self.bitcount):
            # turns the index 'x' in your list to a 1 value, pulling that pin up
            values[x] = 1

            # if its not the first iteration it pulls the previous value in your list to 0 causing that pin
            # to go to 0
            if x != 0:
                values[x - 1] = 0

            # loads the register, outputs the register, and waits a predetrmined amount of time before clearing the register
            self._handle_register(values, left_to_right, wait)

        # This clears out the register at the end so there is nothing output on any of the pins
        # self.clear_register()  # I believe I could use this instead of the following 2 lines of code
        values = self._list_constructor(bit=0)
        self._handle_register(values, left_to_right, wait)

    def skip_across(self, left_to_right=True, wait=.05):

        values = self._list_constructor(bit=0)

        for x in range(self.bitcount):

            if x % 2 == 0:

                values[x] = 1

                if x > 1:
                    values[x-2] = 0
            else:
                values[x] = 0

            self._handle_register(values=values, left_to_right=left_to_right, wait=wait)




    def example_show(self, wait):

        '''Small example of what this class can do with LEDs driven on a shift register

        :param wait: time to wait before refreshing the data in the shift register
        :return:
        '''

        self.fill_bar_walkthrough(wait=wait)
        self.bar_wave(left_to_right=False, wait=wait)

        self.fill_bar_walkthrough(left_to_right=False, wait=wait)
        self.bar_wave(left_to_right=True, wait=wait)

        self.bit_run(left_to_right=True, wait=wait)
        self.bit_run(left_to_right=False, wait=wait)
        self.bit_run(left_to_right=True, wait=wait)
        self.bar_wave(left_to_right=False, wait=wait)
        self.bit_run(left_to_right=False, wait=wait)
        self.bar_wave(left_to_right=True, wait=wait)


if __name__ == '__main__':

    # small example to run if the module is run directly

    t = LightShow(4, 6, 5, power_pin=17)

    while True:
        try:
            t.skip_across(left_to_right=True, wait=.13)
            t.skip_across(left_to_right=False, wait=.13)
        except KeyboardInterrupt:
            t.bit_run(left_to_right=True, wait=.02)
            t.bit_run(left_to_right=False, wait=.02)
            t.clear_register()
            t.output_register()
            break

    while True:
        try:
            t.example_show(.04)
        except KeyboardInterrupt:
            t.bit_run(left_to_right=True, wait=.02)
            t.bit_run(left_to_right=False, wait=.02)
            t.clear_register()
            t.output_register()
            break




