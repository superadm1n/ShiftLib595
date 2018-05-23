# ShiftLib595

This project is designed to be a library to interface with a 74HC595
shift register. It handles the low level clocking, loading, and discharging
of the register. As time goes I would like to add more higher level classes for different
use cases such as ways to read data from the register.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You will need a Raspberry Pi, any model should do and the RPi.GPIO module.
If you dont have it installed on  your raspberry pi you can install it with
the following command

```
pip install RPi.GPIO
```

### Installing This Project

Follow these commands to install this project into your environment

```
git clone https://github.com/superadm1n/ShiftLib595
cd ShiftLib595
python setup.py install
```

## Author

* **Kyle Kowalczyk** - [SmallGuysIT](https://smallguysit.com)



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* [Kevin Darrah](https://www.youtube.com/channel/UC42d7zFnWU0dYVk_M0JED6w) - For the awesome youtube video clearly explaining how 
the 74HC595 shift register stores and outputs data. [Video Linked Here](https://www.youtube.com/watch?v=6fVbJbNPrEU)

