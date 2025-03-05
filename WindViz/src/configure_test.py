import sys, json
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QFormLayout, QGroupBox, QScrollArea, QPushButton, 
    QSpacerItem, QSizePolicy, QWidget, QMessageBox
)

class ChannelDialog(QDialog):
    def __init__(self, App):
        super().__init__()
        self.db = App.db  # Store database reference

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
        self.scroll_area_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_layout = QVBoxLayout(self.scroll_area_widget)

        # Create sections with their own update handlers
        self.pressure_group = self.create_group_box(
            "Pressure Channels", 9, self.pressure_input_fields,
            lambda: self.update_section_fields('pressure')
        )
        self.velocity_group = self.create_group_box(
            "Velocity Channels", 4, self.velocity_input_fields,
            lambda: self.update_section_fields('velocity')
        )
        self.temperature_group = self.create_group_box(
            "Temperature Channel", 1, self.temperature_input_fields, 
            single=True
        )
        self.sting_group = self.create_group_box(
            "STING Channels", 3, self.sting_input_fields,
            lambda: self.update_section_fields('sting')
        )

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

    def create_group_box(self, title, max_channels, field_list, update_handler=None, single=False):
        """Creates a group box for each section with its own update handler"""
        group_box = QGroupBox(title)
        group_layout = QVBoxLayout()

        if not single:
            combo_box = QComboBox()
            combo_box.addItems([str(i) for i in range(1, max_channels + 1)])
            if update_handler:
                combo_box.currentIndexChanged.connect(update_handler)
            group_layout.addWidget(combo_box)
            group_layout.addSpacing(10)

        self.create_input_fields(group_layout, 1, field_list)
        group_box.setLayout(group_layout)
        return group_box

    def create_input_fields(self, layout, num_channels, field_list):
        """Create input fields while preserving existing values"""
        # Store existing values
        existing_values = [field.text() for field in field_list]
        
        # Clear existing fields
        self.clear_input_fields(field_list)
        
        # Create new fields and restore values where possible
        for i in range(num_channels):
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Channel {i + 1}")
            
            # Restore value if it exists
            if i < len(existing_values) and existing_values[i]:
                input_field.setText(existing_values[i])
                
            layout.addWidget(input_field)
            field_list.append(input_field)

    def update_section_fields(self, section):
        """Update fields for a specific section only"""
        if section == 'pressure':
            num_channels = int(self.pressure_group.findChild(QComboBox).currentText())
            self.create_input_fields(self.pressure_group.layout(), num_channels, self.pressure_input_fields)
        elif section == 'velocity':
            num_channels = int(self.velocity_group.findChild(QComboBox).currentText())
            self.create_input_fields(self.velocity_group.layout(), num_channels, self.velocity_input_fields)
        elif section == 'sting':
            num_channels = int(self.sting_group.findChild(QComboBox).currentText())
            self.create_input_fields(self.sting_group.layout(), num_channels, self.sting_input_fields)

    def clear_input_fields(self, field_list):
        """Clear input fields from layout"""
        for field in field_list:
            field.deleteLater()
        field_list.clear()

    def show_success(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Success")
        msg.setText("Configuration successfully loaded!")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def submit(self):
        """Handle the submit action and save data to both JSON and database"""
        try:
            # Get values from input fields
            pressure_values = [field.text() for field in self.pressure_input_fields]
            velocity_values = [field.text() for field in self.velocity_input_fields]
            temperature_value = [field.text() for field in self.temperature_input_fields]
            sting_values = [field.text() for field in self.sting_input_fields]
            sting_config = self.sting_config_combo.currentText()

            # Save to database using set_channel_data
            self.db.set_channel_data("pressure", pressure_values)
            self.db.set_channel_data("velocity", velocity_values)
            self.db.set_channel_data("temperature", temperature_value)
            self.db.set_channel_data("sting", sting_values, config=sting_config)

            # Create JSON format (keeping this for compatibility)
            config_data = {
                "velocity": {
                    "channels": [{"id": i + 1, "name": channel or f"Velocity Channel {i + 1}"} 
                               for i, channel in enumerate(velocity_values)]
                },
                "pressure": {
                    "channels": [{"id": i + 1, "name": channel or f"Pressure Channel {i + 1}"} 
                               for i, channel in enumerate(pressure_values)]
                },
                "temperature": {
                    "channels": [{"id": 1, "name": temperature_value[0] if temperature_value else "Temperature Channel 1"}]
                },
                "sting": {
                    "configuration": sting_config,
                    "channels": [{"id": i + 1, "name": channel or f"STING Channel {i + 1}"} 
                               for i, channel in enumerate(sting_values)]
                }
            }

            # Save to JSON file
            file_path = "channel_configuration.json"
            with open(file_path, "w") as json_file:
                json.dump(config_data, json_file, indent=4)
        
            self.show_success()
        
            self.accept()
            
        except ValueError as e:
            print(f"Error saving configuration: {str(e)}")
            # error dialog?
            
if __name__ == "__main__":
    print("Okay but why you running this by itself tho..\n")
    app = QApplication(sys.argv)
    dialog = ChannelDialog(app)
    dialog.exec_()