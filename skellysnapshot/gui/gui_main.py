from PySide6.QtWidgets import QWidget, QVBoxLayout

from skellysnapshot.gui.helpers.app_state_manager import AppStateManager
from skellysnapshot.gui.helpers.layout_manager import LayoutManager
from skellysnapshot.gui.widgets.calibration_menu import CalibrationMenu, CalibrationManager
from skellysnapshot.gui.widgets.main_menu import MainMenu
from skellysnapshot.gui.widgets.skellycam_camera_menu import SkellyCameraMenu
from skellysnapshot.gui.helpers.task_manager import TaskManager

import logging
logger = logging.getLogger(__name__)

class SkellySnapshotMainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.app_state_manager = AppStateManager()

        self.main_menu = MainMenu(self.app_state_manager)
        self.camera_menu = SkellyCameraMenu(parent=self)
        self.calibration_menu = CalibrationMenu()

        self.layout_manager = LayoutManager()

        self.layout_manager.register_tab(self.main_menu, "Main Menu")
        self.layout_manager.register_tab(self.camera_menu, "Cameras")
        self.layout_manager.register_tab(self.calibration_menu, "Calibration")

        self.task_manager = TaskManager(self.app_state_manager)
        self.calibration_manager = CalibrationManager(self.app_state_manager)

        layout = QVBoxLayout()
        # self.layout_manager.initialize_layout()
        layout.addWidget(self.layout_manager.tab_widget)
        self.setLayout(layout)
        self.add_calibration_subscribers()
        self.add_enable_processing_subscribers()
        self.add_snapshot_settings_subscribers()

        self.app_state_manager.check_enable_conditions()
        self.app_state_manager.check_initial_calibration_state()

        # self.connect_signals_to_event_bus()

        self.connect_signals_to_slots()

    def add_enable_processing_subscribers(self):
        enable_processing_subscribers = [
            self.check_enable_conditions,
            self.main_menu.update_process_snapshot_ready_status
        ]

        for subscriber in enable_processing_subscribers:
            self.app_state_manager.subscribe("enable_processing", subscriber)

    def check_enable_conditions(self, all_conditions_met):
        if all_conditions_met:
            self.camera_menu.enable_capture_button()
        else:
            self.camera_menu.disable_capture_button()

    def add_calibration_subscribers(self):
        calibration_subscribers = [
            self.task_manager.set_anipose_calibration_object,
            # self.check_enable_conditions,
            lambda state: self.app_state_manager.update_button_enable_conditions('calibration_loaded',
                                                                                 state.status == "LOADED"),
            lambda state: self.main_menu.update_calibration_status(state.status == "LOADED"),
            lambda state: self.calibration_menu.update_calibration_object_status(state.status == "LOADED")
        ]

        for subscriber in calibration_subscribers:
            self.app_state_manager.subscribe("calibration", subscriber)

    def add_snapshot_settings_subscribers(self):
        snapshot_settings_subscribers = [
            lambda state: self.camera_menu.update_countdown_timer(state.snapshot_state.countdown_timer)
        ]

        for subscriber in snapshot_settings_subscribers:
            self.app_state_manager.subscribe("snapshot_settings", subscriber)

    def connect_signals_to_slots(self):

        self.calibration_menu.calibration_toml_path_loaded.connect(self.calibration_manager.load_calibration_from_file)
        self.calibration_menu.return_to_main_page_signal.connect(self.layout_manager.switch_to_main_menu_tab)
        self.camera_menu.snapshot_captured.connect(self.on_snapshot_captured_signal)
        self.task_manager.new_results_ready.connect(self.on_results_ready_signal)
        self.main_menu.calibration_groupbox.clicked.connect(self.layout_manager.switch_to_calibration_tab)
        self.main_menu.process_snapshot_ready_group_box.clicked.connect(self.layout_manager.switch_to_camera_tab)
        self.main_menu.snapshot_timer_updated.connect(self.camera_menu.update_countdown_timer)


    def on_snapshot_captured_signal(self, snapshot):
        self.task_manager.process_snapshot(snapshot)

    def on_results_ready_signal(self, snapshot2d_data, snapshot3d_data, snapshot_center_of_mass_data):
        self.layout_manager.add_results_tab(snapshot2d_data, snapshot3d_data, snapshot_center_of_mass_data)


    def closeEvent(self, event):
        logger.info("Close event received - closing SkellySnapshotMainWidget....")
        self.camera_menu.close()

    def close(self):
        logger.info(f"Running `close` method (presumably called by parent: - closing SkellySnapshotMainWidget....")
        self.camera_menu.close()
