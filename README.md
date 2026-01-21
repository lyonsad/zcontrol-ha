# Z-Control Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant custom integration for [Zoeller Z-Control](https://www.zoeller.com/) sump pump alarm systems.

This integration connects to the Z-Control cloud service (zcontrolcloud.com) to monitor your sump pump alarm status.

## Features

- **Binary Sensors**: Monitor alarm states
  - Online status (device connectivity)
  - Input 1 (water detection)
  - Input 2
  - AC Power fault
  - Battery fault

- **Sensors**: Device information
  - WiFi signal strength
  - Alarm count
  - Last heartbeat timestamp
  - Firmware version

- **Buttons**: Device controls
  - Silence Alarm
  - Reset Device

## Requirements

- A Zoeller Z-Control compatible device (e.g., APak alarm system)
- An account at [zcontrolcloud.com](https://account.zcontrolcloud.com)
- Home Assistant 2024.1 or newer

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL and select "Integration" as the category
5. Click "Add"
6. Search for "Z-Control" and install it
7. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/zcontrol` folder from this repository
2. Copy it to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Z-Control"
4. Enter your zcontrolcloud.com email and password
5. Your device(s) will be automatically discovered

## Entities

After setup, the following entities are created for each device:

| Entity | Type | Description |
|--------|------|-------------|
| `binary_sensor.*_online` | Binary Sensor | Device connectivity status |
| `binary_sensor.*_input_1` | Binary Sensor | Input 1 alarm (water detected) |
| `binary_sensor.*_input_2` | Binary Sensor | Input 2 alarm |
| `binary_sensor.*_ac_power` | Binary Sensor | AC power fault |
| `binary_sensor.*_battery` | Binary Sensor | Battery fault |
| `sensor.*_wifi_signal` | Sensor | WiFi signal strength (dBm) |
| `sensor.*_alarm_count` | Sensor | Number of active alarms |
| `sensor.*_last_heartbeat` | Sensor | Last device check-in time |
| `sensor.*_firmware` | Sensor | Firmware version (disabled by default) |
| `button.*_silence_alarm` | Button | Silence the active alarm |
| `button.*_reset_device` | Button | Reset the device |

## Troubleshooting

### Check Logs
Go to **Settings** → **System** → **Logs** and search for "zcontrol" to see any error messages.

### Enable Debug Logging
Add this to your `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.zcontrol: debug
```

### Authentication Issues
If you get authentication errors, verify:
1. Your email and password work at [zcontrolcloud.com](https://account.zcontrolcloud.com)
2. Your account is active and not locked

## Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.

## Disclaimer

This integration is not affiliated with or endorsed by Zoeller Company. Use at your own risk.

## License

MIT License - see [LICENSE](LICENSE) file for details.
