from sage.base_app import BaseApp
from .gaitphase import GaitPhase, STANCE

# Constants for feedback state
FEEDBACK_ON = 1
FEEDBACK_OFF = 0

class Core(BaseApp):
    ###########################################################
    # INITIALIZE APP
    ###########################################################
    def __init__(self, my_sage):
        BaseApp.__init__(self, my_sage, __file__)

        self.DATARATE = self.info["datarate"]
        self.PULSE_LENGTH = float(self.config["pulse_length"])

        self.NODENUM_SENSOR_FOOT_LEFT = self.info["sensors"].index("foot_left")
        self.NODENUM_SENSOR_FOOT_RIGHT = self.info["sensors"].index("foot_right")
        self.NODENUM_FEEDBACK_SHANK_LEFT = self.info["feedback"].index("shank_left")
        self.NODENUM_FEEDBACK_SHANK_RIGHT = self.info["feedback"].index("shank_right")

        self.my_GP_left = GaitPhase(datarate=self.DATARATE)
        self.my_GP_right = GaitPhase(datarate=self.DATARATE)

        self.iteration = 0
        self.Feedback_Left = FEEDBACK_OFF
        self.Feedback_Right = FEEDBACK_OFF
        self.feedback_left_TimeSinceFeedbackStarted = 0
        self.feedback_right_TimeSinceFeedbackStarted = 0

    ###########################################################
    # CHECK NODE CONNECTIONS
    ###########################################################
    def check_status(self):
        sensors_count = self.get_sensors_count()
        feedback_count = self.get_feedback_count()
        err_msg = ""
        if sensors_count < len(self.info["sensors"]):
            err_msg += f"App requires {len(self.info['sensors'])} sensors but only {sensors_count} are connected. "
        if feedback_count < len(self.info["feedback"]):
            err_msg += f"App requires {len(self.info['feedback'])} feedback nodes but only {feedback_count} are connected."
        if err_msg != "":
            return False, err_msg
        return True, "Now running Gait Phase Feedback 1 App"

    ###########################################################
    # RUN APP IN LOOP
    ###########################################################
    def run_in_loop(self):
        # GET RAW SENSOR DATA
        data = self.my_sage.get_next_data()

        time_now = self.iteration / self.DATARATE  # time in seconds

        self.feedback_left_TimeSinceFeedbackStarted += 1 / self.DATARATE
        self.feedback_right_TimeSinceFeedbackStarted += 1 / self.DATARATE

        # Initiate GaitPhase subclasses
        self.my_GP_left.update_gaitphase(data[self.NODENUM_SENSOR_FOOT_LEFT])
        self.my_GP_right.update_gaitphase(data[self.NODENUM_SENSOR_FOOT_RIGHT])

        if self.config["left_feedback_enabled"]:
            self.Feedback_Left = self.give_feedback(
                self.my_GP_left,
                self.NODENUM_FEEDBACK_SHANK_LEFT,
                self.feedback_left_TimeSinceFeedbackStarted,
            )

        if self.config["right_feedback_enabled"]:
            self.Feedback_Right = self.give_feedback(
                self.my_GP_right,
                self.NODENUM_FEEDBACK_SHANK_RIGHT,
                self.feedback_right_TimeSinceFeedbackStarted,
            )

        # CREATE CUSTOM DATA PACKET
        my_data = {
            "time": [time_now],
            "Step_Count_Left": [self.my_GP_left.step_count],
            "Gait_Phase_Left": [int(self.my_GP_left.gaitphase.value)],
            "Step_Count_Right": [self.my_GP_right.step_count],
            "Gait_Phase_Right": [int(self.my_GP_right.gaitphase.value)],
            "Feedback_Left": [self.Feedback_Left],
            "Feedback_Right": [self.Feedback_Right],
        }

        # SAVE DATA
        self.my_sage.save_data(data, my_data)

        # STREAM DATA
        self.my_sage.send_stream_data(data, my_data)

        # Increment iteration count
        self.iteration += 1
        return True

    ###########################################################
    # MANAGE FEEDBACK FOR APP
    ###########################################################
    def give_feedback(self, gait_phase_obj, node_num, time_since_start):
        should_feedback = False
        if self.config["whenFeedback"] == "Early, Middle and Late stance":
            if (
                gait_phase_obj.gaitphase_old != gait_phase_obj.gaitphase
                and gait_phase_obj.gaitphase != STANCE.SWING
            ):
                should_feedback = True
        else:
            if (
                gait_phase_obj.gaitphase_old == STANCE.SWING
                and gait_phase_obj.gaitphase == STANCE.EARLY
            ):
                should_feedback = True

        if should_feedback:
            self.toggle_feedback(
                node_num, duration=self.PULSE_LENGTH, feedback_state=True
            )
            if self.NODENUM_FEEDBACK_SHANK_LEFT:
                self.feedback_left_TimeSinceFeedbackStarted = 0
            elif self.NODENUM_FEEDBACK_SHANK_RIGHT:
                self.feedback_right_TimeSinceFeedbackStarted = 0

            return FEEDBACK_ON
        elif time_since_start > self.PULSE_LENGTH:
            self.toggle_feedback(node_num, feedback_state=False)
            return FEEDBACK_OFF
        return 1

    def toggle_feedback(self, feedbackNode=0, duration=1, feedback_state=False):
        if feedback_state:
            self.my_sage.feedback_on(feedbackNode, duration)
        else:
            self.my_sage.feedback_off(feedbackNode)
