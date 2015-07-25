#include <Servo.h>

uint8_t battery_pin=A0;
uint8_t right_motor=6;
uint8_t left_motor=11;
Servo left_servo;
Servo right_servo;

uint8_t voltage_cutoff=800;
uint8_t state=0;
int8_t axes[255];
uint8_t buttons[255];
uint8_t num_axes=0;
uint8_t num_buttons=0;
uint16_t data_pointer=0;
int32_t timeout_timer=0;
int16_t timeout=500;

void setup()
{
  Serial.begin(19200);

  pinMode(battery_pin,INPUT);
  pinMode(right_motor,OUTPUT);
  pinMode(left_motor,OUTPUT);
  analogWrite(right_motor,0);
  analogWrite(left_motor,0);

  left_servo.attach(5);
  right_servo.attach(3);
  left_servo.write(90);
  right_servo.write(90);
}

void loop()
{
  if(analogRead(battery_pin)>=voltage_cutoff)
  {
    while(Serial.available()>0)
    {
      int temp=Serial.read();

      if(temp!=-1)
      {
        switch(state)
        {
          case 0:
            if(temp==0xfa)
              state=1;
            break;
          case 1:
            if(temp==0xaf)
              state=2;
            else
              state=0;
            break;
          case 2:
            num_axes=temp;
            data_pointer=0;

            if(num_axes==0)
              state=4;
            else
              state=3;

            break;
          case 3:
            axes[data_pointer++]=temp;

            if(data_pointer>=num_axes)
            {
              data_pointer=0;
              state=4;
            }
            break;
          case 4:
            num_buttons=temp;
            data_pointer=0;

            if(num_axes==0)
              state=0;
            else
              state=5;

            break;
          case 5:
            buttons[data_pointer++]=temp;

            if(data_pointer>=num_buttons)
            {
              data_pointer=0;
              timeout_timer=millis()+timeout;
              state=0;
            }
            break;
          default:
            state=0;
            break;
        }
      }
    }
  }
  else
  {
    left_servo.write(90);
    right_servo.write(90);
  }

  float left_value=90-(axes[3]/127.0)*90+(axes[2]/127.0)*90;
  float right_value=90-(axes[3]/127.0)*90-(axes[2]/127.0)*90;

  left_servo.write(map(left_value,0,180,0,180));
  right_servo.write(map(right_value,180,0,0,180));

  int16_t throttle=-axes[1];

  if(throttle<0)
    throttle=0;

  throttle=map(throttle,0,127,0,100);

  if(millis()>timeout_timer)
    throttle=0;
  
  analogWrite(left_motor,throttle);
  analogWrite(right_motor,throttle);
}
