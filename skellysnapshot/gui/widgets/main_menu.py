from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QGroupBox, QLabel, QWidget, QVBoxLayout, QSizePolicy, QSpacerItem, QSpinBox

from skellysnapshot.backend.constants import Colors


class HoverableClickableGroupBox(QGroupBox):
    clicked = Signal()

    def __init__(self, title):
        super().__init__(title)
        self.setMouseTracking(True)  # Enable mouse tracking

    def mousePressEvent(self, event):
        self.clicked.emit()

    def enterEvent(self, event):
        # Change style when mouse enters the widget area
        self.setStyleSheet("HoverableClickableGroupBox { border: 2px solid white; background-color: rgb(55, 55, 55)}")
        for child in self.findChildren(QLabel):
            current_style = child.styleSheet()
            new_style = current_style + "; background-color: rgb(55, 55, 55);"
            child.setStyleSheet(new_style)

    def leaveEvent(self, event):
        # Revert style when mouse leaves the widget area
        self.setStyleSheet("HoverableClickableGroupBox { border: none; background-color:  rgb(40, 40, 40)}")
        for child in self.findChildren(QLabel):
            current_style = child.styleSheet()
            new_style = current_style + "; background-color: rgb(40, 40, 40);"
            child.setStyleSheet(new_style)


class MainMenu(QWidget):
    snapshot_timer_updated = Signal(int) 


    def __init__(self, app_state_manager):
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.app_state_manager = app_state_manager  # Reference to the AppStateManager


        # Add Welcome Label
        self.add_welcome_label(main_layout)

        # Add General Information GroupBox
        self.add_general_info_groupbox(main_layout)

        # Add Calibration Status GroupBox
        self.add_calibration_status_groupbox(main_layout)

        self.add_process_snapshot_ready_groupbox(main_layout)

        self.add_snapshot_timer_groupbox(main_layout)

        # Add Spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_layout.addItem(spacer)

    def add_welcome_label(self, layout):
        welcome_label = QLabel("Welcome to SkellySnapshot!")
        welcome_label.setObjectName("WelcomeLabel")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(welcome_label)

    def add_general_info_groupbox(self, layout):
        group_box = QGroupBox("SkellySnapshot: Instantaneous Motion Capture Feedback")
        group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        group_layout = QVBoxLayout()

        intro_label = QLabel()
        intro_label.setObjectName('ExplanationLabel')
        intro_text = """
        <p>SkellySnapshot provides immediate, single-frame motion capture using standard webcams. 
        It's designed for quick setup and rapid feedback, as a precursor to a full FreeMoCap recording. </p>
        """
        intro_label.setText(intro_text)
        intro_label.setWordWrap(True)
        intro_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        group_layout.addWidget(intro_label)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

    def add_calibration_status_groupbox(self, layout):
        self.calibration_groupbox = HoverableClickableGroupBox("Calibration Status")
        self.calibration_groupbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.calibration_groupbox.setMinimumHeight(100)
        calibration_layout = QVBoxLayout()

        self.not_loaded_text = 'Not Loaded'
        self.not_loaded_additional_info = 'Click here to load calibration'

        self.calibration_status_label = QLabel(self.not_loaded_text)
        self.calibration_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.calibration_additional_info_label = QLabel(self.not_loaded_additional_info)
        self.calibration_additional_info_label.setObjectName("CalibrationAdditionalInfoLabel")

        calibration_layout.addWidget(self.calibration_status_label)
        calibration_layout.addWidget(self.calibration_additional_info_label)
        self.calibration_groupbox.setLayout(calibration_layout)

        layout.addWidget(self.calibration_groupbox)

    def update_calibration_status(self, is_loaded):
        if is_loaded:
            self.calibration_status_label.setText("Loaded")
            self.calibration_status_label.setStyleSheet(f"color: {Colors.READY_COLOR.value};")
            self.calibration_additional_info_label.setText('Loaded from .toml file')
        else:
            self.calibration_status_label.setText(self.not_loaded_text)
            self.calibration_status_label.setStyleSheet(f"color: {Colors.NOT_READY_COLOR.value};")
            self.calibration_additional_info_label.setText(self.not_loaded_additional_info)

    def add_process_snapshot_ready_groupbox(self, layout):
        self.process_snapshot_ready_group_box = HoverableClickableGroupBox("Process Snapshot Status")
        self.process_snapshot_ready_group_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.process_snapshot_ready_group_box.setMinimumHeight(100)
        group_layout = QVBoxLayout()

        self.not_ready_text = 'Not Ready'
        self.process_ready_status_label = QLabel(self.not_ready_text)
        self.process_ready_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        group_layout.addWidget(self.process_ready_status_label)
        self.process_snapshot_ready_group_box.setLayout(group_layout)

        layout.addWidget(self.process_snapshot_ready_group_box)

    def add_snapshot_timer_groupbox(self, layout):
        group_box = QGroupBox("Snapshot Timer")
        group_layout = QVBoxLayout()
        group_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.timer_spinbox = QSpinBox()
        self.timer_spinbox.setRange(0, 60)  # Set a reasonable range for the timer
        self.timer_spinbox.setValue(self.app_state_manager.snapshot_state.countdown_timer)
        self.timer_spinbox.valueChanged.connect(self.on_timer_value_changed)

        group_layout.addWidget(self.timer_spinbox)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

    def on_timer_value_changed(self, new_value):
        self.app_state_manager.update_snapshot_timer(new_value)
        self.snapshot_timer_updated.emit(new_value)

    def update_process_snapshot_ready_status(self, is_ready):
        if is_ready:
            self.process_ready_status_label.setText("Ready")
            self.process_ready_status_label.setStyleSheet(f"color: {Colors.READY_COLOR.value};")
        else:
            self.process_ready_status_label.setText(self.not_ready_text)
            self.process_ready_status_label.setStyleSheet(f"color: {Colors.NOT_READY_COLOR.value};")
