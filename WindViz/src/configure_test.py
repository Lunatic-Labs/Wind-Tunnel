import sys, json
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QFormLayout, QGroupBox, QScrollArea, QPushButton, 
    QSpacerItem, QSizePolicy, QWidget  # Ensure QWidget is imported
)

class ChannelDialog(QDialog):
    def __init__(self, App):
        super().__init__()

        self.setWindowTitle("Channel Configuration")
        self.setGeometry(100, 100, 500, 500)

        # Initialize input fields for each section
        self.pressure_input_fields = []
        self.velocity_input_fields = []
        self.temperature_input_fields = []
        self.sting_input_fields = []

        self.layout = QVBoxLayout()

        # Create scrollable area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget = QWidget()  # This needs QWidget to work
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_layout = QVBoxLayout(self.scroll_area_widget)

        # Create sections (Pressure, Velocity, Temperature, STING)
        self.pressure_group = self.create_group_box("Pressure Channels", 9, self.pressure_input_fields)
        self.velocity_group = self.create_group_box("Velocity Channels", 4, self.velocity_input_fields)
        self.temperature_group = self.create_group_box("Temperature Channel", 1, self.temperature_input_fields, single=True)
        self.sting_group = self.create_group_box("STING Channels", 3, self.sting_input_fields)

        # Add STING Configuration dropdown
        self.sting_config_combo = QComboBox()
        self.sting_config_combo.addItems(["Side", "Normal"])
        self.sting_group.layout().addWidget(QLabel("STING Configuration"))
        self.sting_group.layout().addWidget(self.sting_config_combo)

        # Add group boxes to scroll layout
        self.scroll_layout.addWidget(self.pressure_group)
        self.scroll_layout.addWidget(self.velocity_group)
        self.scroll_layout.addWidget(self.temperature_group)
        self.scroll_layout.addWidget(self.sting_group)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)
        self.layout.addWidget(self.submit_button)

        # Set main layout
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

    def create_group_box(self, title, max_channels, field_list, single=False):
        """Creates a group box for each section (Pressure, Velocity, etc.)"""
        group_box = QGroupBox(title)
        group_layout = QVBoxLayout()

        if not single:
            # Create a drop-down for number of channels
            combo_box = QComboBox()
            combo_box.addItems([str(i) for i in range(1, max_channels + 1)])
            combo_box.currentIndexChanged.connect(self.update_input_fields)
            group_layout.addWidget(combo_box)
            group_layout.addSpacing(10)  # Space between dropdown and fields, looks really bad without

        self.create_input_fields(group_layout, 1, field_list)  # Temporary, to clear inputs
        group_box.setLayout(group_layout)

        return group_box

    def create_input_fields(self, layout, num_channels, field_list):
        """Dynamically create input fields based on the selected number of channels."""
        for i in range(num_channels):
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Channel {i + 1}")
            layout.addWidget(input_field)
            field_list.append(input_field)

    def update_input_fields(self):
        """Update the input fields based on the dropdown selection."""
        # Clear existing input fields before adding new ones
        self.clear_input_fields(self.pressure_input_fields)
        self.clear_input_fields(self.velocity_input_fields)
        self.clear_input_fields(self.sting_input_fields)
        
        # Get the number of channels selected
        pressure_channels = int(self.pressure_group.findChild(QComboBox).currentText())
        velocity_channels = int(self.velocity_group.findChild(QComboBox).currentText())
        sting_channels = int(self.sting_group.findChild(QComboBox).currentText())

        # Create new input fields based on the selected values
        self.create_input_fields(self.pressure_group.layout(), pressure_channels, self.pressure_input_fields)
        self.create_input_fields(self.velocity_group.layout(), velocity_channels, self.velocity_input_fields)
        self.create_input_fields(self.sting_group.layout(), sting_channels, self.sting_input_fields)

    def clear_input_fields(self, field_list):
        """Clear the input fields list and remove the input fields from the layout."""
        for field in field_list:
            field.deleteLater()  # Remove the field from the layout
        field_list.clear()  # Clear the list of field references


    def submit(self):
        """Handle the submit action and save data to a JSON file."""
        pressure_channels = [field.text() for field in self.pressure_input_fields]
        velocity_channels = [field.text() for field in self.velocity_input_fields]
        sting_channels = [field.text() for field in self.sting_input_fields]
        sting_config = self.sting_config_combo.currentText()
    
        config_data = {
            "velocity": {
                "channels": [{"id": i + 1, "name": f"Velocity Channel {i + 1}"} for i in range(len(velocity_channels))]
            },
            "pressure": {
                "channels": [{"id": i + 1, "name": f"Pressure Channel {i + 1}"} for i in range(len(pressure_channels))]
            },
            "temperature": {
                "channels": [{"id": 1, "name": "Temperature Channel 1"}]  # Always 1 channel
            },
            "sting": {
                "configuration": sting_config,
                "channels": [{"id": i + 1, "name": f"STING Channel {i + 1}"} for i in range(len(sting_channels))]
            }
        }

        # Save the dictionary to a JSON file
        file_path = "channel_configuration.json"
        with open(file_path, "w") as json_file:
            json.dump(config_data, json_file, indent=4)
    
        # Print a success message and the collected data (optional)
        print(f"Configuration saved to {file_path}")
        print(json.dumps(config_data, indent=4))
    
        # Close the dialog
        self.accept()



if __name__ == "__main__":
    print("Okay but why you running this by itself tho..\n")
    app = QApplication(sys.argv)
    dialog = ChannelDialog()
    dialog.exec_()
