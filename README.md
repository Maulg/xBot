# xBot
Your Robot must perform the following actions:

1) As your robot follows the black line,
 the RGB-LED will display Green and remain on.  

2) The robot will encounter multiple obstacles
 within it's path.  The robot should recognize
 that something in it's path by using the
 obstacle avoidance sensor and stop. 

3) Once stopped at the object, the RGB-LED
 needs to turn Red and wait for 5 seconds
 to see if the object has moved.  The object
 will be either a book or a automated gate.  

4)  If the object has not moved within 5 seconds,
 then the robot needs to activate the sound
 device (buzzer). 

5) Once the sound device is activated, the robot
 also needs to send 5 pulses through the
 infrared transmitter in order to open the gate.
  The pulses need to have a duration of 150ms with
 a back off time of 150ms (pulse for 150ms, then
 wait 150ms before the next pulse).  If the object
 is the automated gate then these pulses will open
 the gate.

6) Once the object is removed, the robot needs
 to turn the RGB-LED to Green, disable the buzzer
 then continue moving forward.

7) At any point if the temperature sensor detects
 a heat source (a temperature that exceeds 28
 degrees Celsius) the robot will stop and the
 3RGD-LED will turn blue. The robot will remain
 stopped for an elapsed time of 10 seconds. After
 10 seconds the robot will begin following the
 black line once again and the 3RGB-LED will once
 again turn green. 
