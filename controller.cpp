#include <cmath>
#include <iostream>
#include <string>
#include "msl/joystick.hpp"
#include "msl/serial.hpp"
#include "msl/time.hpp"

const uint8_t HEADER=0xFA;
const uint8_t ID=0xef;

int main()
{
	while(true)
	{
		auto joysticks=msl::joystick_t::list();
		size_t joystick_number=0;
		std::string serial_port="/dev/ttyUSB0";
		size_t serial_baud=57600;

		if(joysticks.size()<=joystick_number)
		{
			std::cout<<"joystick "<<joystick_number<<" does not exist"<<std::endl;
		}
		else
		{
			msl::joystick_t joystick(joysticks[joystick_number]);
			joystick.open();

			if(!joystick.good())
			{
				std::cout<<"could not open joystick "<<joystick_number<<std::endl;
			}
			else
			{
				std::cout<<"using joystick number "<<joystick_number<<" with "<<joystick.axis_count()<<
					" axes and "<<joystick.button_count()<<" buttons"<<std::endl;

				while(joystick.good())
				{
					msl::serial_t arduino(serial_port,serial_baud);
					arduino.open();

					if(!arduino.good())
					{
						std::cout<<"could not open serial port "<<serial_port<<" at "<<serial_baud<<std::endl;
					}
					else
					{
						std::cout<<"using serial port "<<serial_port<<" at "<<serial_baud<<std::endl;

						while(joystick.good()&&arduino.good())
						{
							float throttle_raw=-joystick.axis(1);
							if(throttle_raw<0)
								throttle_raw=0;
							uint8_t throttle=throttle_raw*100;
							int8_t pitch=-joystick.axis(3)*127;
							int8_t yaw=joystick.axis(2)*127;
							std::cout<<(int)throttle<<"\t"<<(int)pitch<<"\t"<<(int)yaw<<std::endl;
							arduino.write(&HEADER,1);
							arduino.write(&ID,1);
							arduino.write(&pitch,1);
							arduino.write(&yaw,1);
							arduino.write(&throttle,1);

							msl::delay_ms(20);
						}
					}

					msl::delay_ms(1);
				}
			}
		}

		msl::delay_ms(1);
	}

	return 0;
}