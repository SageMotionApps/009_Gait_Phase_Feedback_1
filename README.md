# Gait Phase Feedback 1 App
Compute gait phase and steps of both feet and provide feedback during the gait phase. Feedback starts when gait transitions to early stance or to early, middle, and late stance, and lasts for the configured Feedback Pulse Length.

### Nodes Required: 4
- **Sensing (2):**
  - foot_left (top, switch pointing forward)
  - foot_right (top, switch pointing forward)
- **Feedback (2):**
  - shank_left
  - shank_right

## Algorithm & Calibration
### Algorithm Information
The app calculates the gait phase using gyroscope data from the foot sensors. The gait phase transitions through the following states:
- **Early stance**
- **Middle stance**
- **Late stance**
- **Swing**

Feedback is provided based on the configured settings, either during specific gait phases or transitions.

### Calibration Process:
The angle calculated is the global roll angle for the IMU. This must be aligned with the segment. The app will take the starting position to determine yaw offset.

## Description of Data in Downloaded File
### Calculated Fields
- **time (sec):** Time since the trial started.
- **Step_Count_Left:** Number of steps detected for the left foot.
- **Gait_Phase_Left:** Gait phase of the left foot:
  - 0: Early stance
  - 1: Middle stance
  - 2: Late stance
  - 3: Swing
- **Step_Count_Right:** Number of steps detected for the right foot.
- **Gait_Phase_Right:** Gait phase of the right foot:
  - 0: Early stance
  - 1: Middle stance
  - 2: Late stance
  - 3: Swing
- **Feedback_Left:** Feedback status for the left shank:
  - 0: Feedback off
  - 1: Feedback on
- **Feedback_Right:** Feedback status for the right shank:
  - 0: Feedback off
  - 1: Feedback on

### Sensor Raw Data Values
Each of the following columns will be repeated for each sensor:
- **SensorIndex:** Index of raw sensor data.
- **AccelX/Y/Z (m/s²):** Raw acceleration data.
- **GyroX/Y/Z (deg/s):** Raw gyroscope data.
- **MagX/Y/Z (μT):** Raw magnetometer data.
- **Quat1/2/3/4:** Quaternion data (scalar-first order).
- **Sampletime:** Timestamp of the sensor value.
- **Package:** Package number of the sensor val## App Configuration
### Parameters
- **Left Foot Feedback On?** (`left_feedback_enabled`): Enable or disable feedback for the left foot.
- **Right Foot Feedback On?** (`right_feedback_enabled`): Enable or disable feedback for the right foot.
- **When to Give Feedback?** (`whenFeedback`): Specify when to give feedback:
  - Early stance
  - Early, Middle, and Late stance
- **Feedback Pulse Length (sec):** (`pulse_length`): Duration of the feedback pulse in seconds.
- **Save Mode:** (`save_mode`): Format for saving data:
  - csv
  - h5
  - xlsx

## Development and App Processing Loop
The app processes data in a loop, performing the following steps:
1. Retrieve raw sensor data.
2. Update the gait phase for both feet using the `GaitPhase` class.
3. Provide feedback based on the configured settings.
4. Save and stream the processed data.

For more information on app development, refer to the [SageMotion Documentation](http://docs.sagemotion.com/index.html).