class Database:
    def __init__(self):
        self.data = {
            "channels": {
                "pressure": {"max_channels": 9, "values": []},
                "velocity": {"max_channels": 4, "values": []},
                "temperature": {"max_channels": 1, "values": []},
                "sting": {
                    "max_channels": 3, 
                    "values": [],
                    "configuration": "Side"  # default value
                }
            }
        }
    
    def set_channel_data(self, channel_type, values, config=None):
        if channel_type not in self.data["channels"]:
            raise ValueError(f"Invalid channel type: {channel_type}")
            
        channel_info = self.data["channels"][channel_type]
        if len(values) > channel_info["max_channels"]:
            raise ValueError(f"Too many channels for {channel_type}")
            
        channel_info["values"] = values
        if config is not None:
            if "configuration" in channel_info:
                channel_info["configuration"] = config
            else:
                raise ValueError(f"{channel_type} does not support configuration")
    
    def get_channel_data(self, channel_type):
        if channel_type not in self.data["channels"]:
            raise ValueError(f"Invalid channel type: {channel_type}")
        return self.data["channels"][channel_type]
    

if __name__ == "__main__":
    print("Dont do that\n\n>.>\n\n")
