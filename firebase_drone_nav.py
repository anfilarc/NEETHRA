import firebase_admin
from firebase_admin import credentials, db
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

# Initialize Firebase Admin SDK with your credentials JSON file
cred = credentials.Certificate("path/to/your/credentials.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://your-firebase-project.firebaseio.com'})

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

# Firebase event handler for new location data
def location_data_handler(event):
    if event.event_type == 'put':
        # New data was added to the Firebase Realtime Database
        data = event.data
        print("Received new location data:", data)

        # Extract latitude, longitude, and altitude from the received data
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        altitude = data.get("altitude")

        if latitude is not None and longitude is not None and altitude is not None:
            target_location = LocationGlobalRelative(latitude, longitude, altitude)

            # Arm and takeoff to the target altitude
            arm_and_takeoff(altitude)

            # Command the drone to navigate to the new location
            goto_position_target_global(vehicle, target_location)

# Reference to your Firebase Realtime Database node where location data is pushed
location_data_ref = db.reference('/location_data')

# Set up a listener for changes in the location data
location_data_ref.listen(location_data_handler)

try:
    while True:
        time.sleep(1)  # Keep the script running to listen for Firebase updates

finally:
    # Close the connection
    vehicle.close()
    print("Connection closed.")
