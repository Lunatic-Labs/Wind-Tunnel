import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QComboBox, QFormLayout, QGroupBox, QScrollArea, QSpacerItem, QSizePolicy, QDialog

class ConfigGeneratorDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('DAQ970 Configuration Generator')
        self.setGeometry(100, 100, 500, 600)

        # Main layout
        main_layout = QVBoxLayout()

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a container widget for the scroll area
        container_widget = QWidget()
        container_layout = QVBoxLayout()

        # Measurement types
        self.velocity_group = self.create_measurement_group("Velocity", 4)
        self.pressure_group = self.create_measurement_group("Pressure", 9)
        self.temperature_group = self.create_measurement_group("Temperature", 1)
        self.sting_group = self.create_measurement_group("STING", 3)

        # Add all groups to the container layout
        container_layout.addWidget(self.velocity_group)
        container_layout.addWidget(self.pressure_group)
        container_layout.addWidget(self.temperature_group)
        container_layout.addWidget(self.sting_group)

        # Add a spacer item to push the save button to the bottom
        container_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add the save button at the bottom
        self.save_button = QPushButton("Save Configuration")
        self.save_button.clicked.connect(self.save_configuration)
        container_layout.addWidget(self.save_button)

        # Set the container layout
        container_widget.setLayout(container_layout)

        # Set the container widget as the scroll area's widget
        scroll_area.setWidget(container_widget)

        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)

        # Set the layout for the main window
        self.setLayout(main_layout)

    def create_measurement_group(self, name, max_channels):
        group_box = QGroupBox(f"{name} Configuration")
        form_layout = QFormLayout()

        # Dropdown to select the number of channels
        num_channels_label = QLabel(f"Select number of {name} channels:")
        num_channels_combo = QComboBox()
        num_channels_combo.addItems([str(i) for i in range(1, max_channels + 1)])
        num_channels_combo.currentIndexChanged.connect(lambda: self.update_channels(form_layout, name, int(num_channels_combo.currentText()), max_channels))

        form_layout.addRow(num_channels_label, num_channels_combo)

        group_box.setLayout(form_layout)
        return group_box

    def update_channels(self, form_layout, name, num_channels, max_channels):
        # Clear existing channels input fields
        for i in reversed(range(form_layout.rowCount())):
            widget = form_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add the dynamic channel inputs
        for i in range(1, num_channels + 1):
            channel_name = QLineEdit(f"{name} Channel {i}")
            unit = "m/s" if name == "Velocity" else "Pa" if name == "Pressure" else "C" if name == "Temperature" else "N"
            unit_label = QLabel(unit)
            enabled_checkbox = QCheckBox("Enabled")
            enabled_checkbox.setChecked(True)

            form_layout.addRow(f"{name} Channel {i}:", channel_name)
            form_layout.addRow(f"Unit ({name}):", unit_label)
            form_layout.addRow("Enabled", enabled_checkbox)

            channel_data = {
                'name': channel_name,
                'unit': unit,
                'enabled': enabled_checkbox
            }

            # Save the channel data into the widget for later access
            channel_name.setProperty("channel_data", channel_data)

    def save_configuration(self):
        config = {}

        # Collect data from each measurement group
        config['velocity'] = self.collect_data_from_group(self.velocity_group)
        config['pressure'] = self.collect_data_from_group(self.pressure_group)
        config['temperature'] = self.collect_data_from_group(self.temperature_group)
        config['sting'] = self.collect_data_from_group(self.sting_group)

        # Write to a JSON file
        with open("daq970_config.json", "w") as f:
            json.dump(config, f, indent=4)
        
        print("Configuration saved to daq970_config.json")
        self.accept()  # Close the dialog after saving

    def collect_data_from_group(self, group_box):
        channels = []
        for child in group_box.findChildren(QLineEdit):
            channel_data = child.property("channel_data")
            channels.append({
                'id': len(channels) + 1,
                'name': channel_data['name'].text(),
                'unit': channel_data['unit'],
                'enabled': channel_data['enabled'].isChecked()
            })
        return {'channels': channels}


