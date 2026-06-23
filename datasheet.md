Features
- Angle Displacement Measurement
- Bends and Flexes physically with motion device
- Possible Uses
 - Robotics
 - Gaming (Virtual Motion)
 - Medical Devices
 - Computer Peripherals
 - Musical Instruments
 - Physical Therapy
- Simple Construction
- Low Profile
spectrasymbol.com Rev A1 - Page 1 (888) 795-2283
Mechanical Specifications Electrical Specifications
-Life Cycle: >1 million
-Height: 0.43mm (0.017")
-Temperature Range: -35°C to +80°C
-Flat Resistance: 10K Ohms
-Resistance Tolerance: ±30%
-Bend Resistance Range: 60K to 110K Ohms
-Power Rating : 0.50 Watts continuous. 1 Watt
 Peak
Dimensional Diagram - Stock Flex Sensor
6.35 [0.250]
ACTIVE LENGTH
95.25 [3.750]
PART LENGTH
112.24 [4.419]
How It Works
Flat (nominal resistance)
45˚ Bend (increased resistance)
90˚ Bend (resistance increased further)
How to Order - Stock Flex Sensor
103
Resistance
103 = 10 KOhms
L
Model
L = Linear
FS
Series
FS = Flex Sensor
Active Length
0095 = 95.25mm
0095 ST
Connectors
ST = Solder Tab
spectrasymbol.com Page 2 (888) 795-2283
Schematics
Following are notes from the ITP Flex Sensor Workshop
"The impedance buffer in the [Basic Flex Sensor Circuit] (above) is a single sided operational amplifier, used with these
sensors because the low bias current of the op amp reduces errer due to source impedance of the flex sensor as
voltage divider. Suggested op amps are the LM358 or LM324."
"You can also test your flex sensor using the simplest circut, and skip the op amp."
"Adjustable Buffer - a potentiometer can be added to the
circuit to adjust the sensitivity range."
"Variable Deflection Threshold Switch - an op amp is used
and outputs either high or low depending on the voltage of the
inverting input. In this way you can use the flex sensor as a
switch without going through a microcontroller."
"Resistance to Voltage Converter - use the sensor as the
input of a resistance to voltage converter using a dual sided
supply op-amp. A negative reference voltage will give a positive
output. Should be used in situations when you want output at a
low degree of bending."