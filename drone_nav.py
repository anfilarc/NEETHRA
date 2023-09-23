from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

# Connect to the drone (change the connection string as needed)
connection_string = '/dev/ttyACM0'  # Adjust this to your port
baud_rate = 115200
vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)

def arm_and_takeoff(target_altitude):
    print("Arming motors...")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    print("Taking off to altitude {} meters...".format(target_altitude))
    vehicle.simple_takeoff(target_altitude)

    while True:
        print("Altitude: {} meters".format(vehicle.location.global_relative_frame.alt))
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

def goto_position_target_global(vehicle, target_location):
    msg = vehicle.message_factory.set_position_target_global_int_encode(
        0,
        0,
        0,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b0000111111000111,
        *target_location,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
    )
    vehicle.send_mavlink(msg)

try:
    target_altitude = 10  # Change this to your desired altitude in meters
    target_location = LocationGlobalRelative(latitude, longitude, target_altitude)

    arm_and_takeoff(target_altitude)

    # Command the drone to navigate to the predefined GPS coordinates
    goto_position_target_global(vehicle, target_location)

    # Do other tasks here if needed

finally:
    # Close the connection
    vehicle.close()
    print("Connection closed.")
