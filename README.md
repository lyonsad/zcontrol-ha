# Z-Control Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant custom integration for [Zoeller Z-Control](https://www.zoeller.com/) sump pump alarm systems.

This integration connects to the Z-Control cloud service (zcontrolcloud.com) to monitor your sump pump alarm status.

## Features

- **Binary Sensors**: Monitor alarm states
  - Online status (device connectivity)
  - APak: Input 1, Input 2, AC Power fault, and Battery fault
  - Aquanot 508: System Ready, DC Pump, Float Status alarms, and Battery fault

- **Sensors**: Device information
  - WiFi signal strength
  - Alarm count
  - Last heartbeat timestamp
  - Firmware version

- **Buttons**: Device controls
  - Silence Alarm
  - Reset Device

## Requirements

- A Z-Control cloud-connected device (for example, an APak alarm or Aquanot 508 Fit controller)
- An account at [zcontrolcloud.com](https://account.zcontrolcloud.com)
- Home Assistant 2024.11 or newer

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

Devices added to your Z-Control account later are discovered during normal
polling, without reloading the integration. Entity unique IDs are unchanged;
devices that temporarily disappear become unavailable and reuse their existing
entities when they return.

### Account timezone

Heartbeat timestamps may include an explicit UTC offset, which is preserved.
Timestamps without an offset use Home Assistant's timezone by default. If your
Z-Control account uses a different timezone, open the integration's **Configure**
options and enter the account's IANA timezone (for example, `America/Chicago`).
Saving a changed timezone reloads the integration. This changes timestamp
interpretation in Home Assistant; it does not change settings on Z-Control or
the physical device. A timestamp without an offset remains ambiguous during a
repeated hour at the end of daylight saving time.

## Entities

Entity IDs below are examples. Home Assistant derives them from the device and
entity names; verify the actual IDs in **Developer Tools → States** before using
an automation. Existing entity unique IDs are preserved when upgrading.

### Common entities

| Entity suffix | Meaning |
|---------------|---------|
| `binary_sensor.*_online` | `on` means the device is connected to Z-Control; `off` means the cloud reports it offline. |
| `sensor.*_alarm_count` | Cloud-reported active alarm count; unknown when the field is missing. This is not a lifetime pump-cycle count. A nonzero count does not identify the cause or severity. |
| `sensor.*_wifi_signal` | WiFi signal strength in dBm; a more negative number indicates weaker reception. |
| `sensor.*_last_heartbeat` | Last device check-in. Explicit timestamp offsets are preserved. Timestamps without an offset use the configured account timezone, or the Home Assistant timezone by default. |
| `sensor.*_firmware_version` | Firmware version (disabled by default; enable it on the device page). |
| `button.*_silence_alarm` | Sends the cloud silence command. Silencing an alarm does not fix its cause. |
| `button.*_reset_device` | Sends the cloud reset command. Use deliberately after checking the device; do not automate resets as a response to faults. |

### APak alarm statuses

| Entity suffix | Z-Control status | Meaning |
|---------------|------------------|---------|
| `binary_sensor.*_input_1` | Input 1 | Alarm on the first wired input. High water only if a water/float switch is connected there. |
| `binary_sensor.*_input_2` | Input 2 | Alarm on the second wired input; the connected function depends on the installation. |
| `binary_sensor.*_ac_power` | AC Power | AC power fault reported by the alarm controller. |
| `binary_sensor.*_battery` | Battery | Battery fault reported by the alarm controller. |

### Aquanot 508 statuses

The 508 Fit cloud dashboard uses **System Ready**, **Battery**, **DC Pump**, and
**Float Status** rather than APak's input labels. The integration adds these
status sensors when their exact names appear in `deviceStatusList`, without
assuming that the API's `family` field is a product model number.

| New entity suffix | Z-Control status | Meaning |
|-------------------|------------------|---------|
| `binary_sensor.*_system_ready_alarm` | System Ready | A reported readiness fault/alarm. This is a problem sensor: `on` means a problem, not that the system is ready. It is not an AC-power-only sensor. |
| `binary_sensor.*_dc_pump_alarm` | DC Pump | A reported DC pump fault/alarm, not a pump-running or cycle-count sensor. |
| `binary_sensor.*_float_status_alarm` | Float Status | A reported float fault/alarm; do not assume every float fault means high water. Check Z-Control for details. |

The existing Battery entity also applies to the 508. These statuses describe the
backup controller and DC pump; they do not independently prove the primary AC
pump is working. See the manufacturer's [Aquanot Fit information](https://zoellerpumps.com/wp-content/uploads/sites/3/2023/10/FM0532-sm-1.pdf)
for the system's capabilities.

#### Physical floats and interpreting alarms

Zoeller's [508 Fit installation instructions (FM3120)](https://zoellerpumps.com/wp-content/uploads/sites/3/2026/03/Installation-Instructions-Aquanot-508-Fit-FM3120-155744-G.pdf),
pages 4–6, describe an operational float and a high-water reed sensor (marked
optional in the installation diagram). The high-water sensor can activate the
backup pump. Both switches are supervised; a disconnected switch can cause an
alarm, and disconnecting the high-water switch can also run the pump. They are
not APak-style general-purpose Input 1/Input 2 alarm terminals.

The manufacturer's indicator table distinguishes these conditions:

- **System Ready:** normal readiness and AC loss have different indications.
- **Battery:** charged, charging, low battery, and bad battery are distinct.
- **DC Pump:** running, previously ran, and pump fault are distinct. A pump-run
  alarm does not by itself prove the pump has failed.
- **Float Status:** high water and a float/switch fault are distinct.

These Home Assistant binary sensors expose the existing cloud fault/alarm flags,
not the complete indicator table. The manual documents controller behavior,
not numeric cloud API values. Separate high-water, pump-running, AC-loss, or
battery-level entities need verified cloud payload fields and value mappings;
they cannot safely be inferred from LED colors or the two unknown Input entities.

For compatibility, the original Online, Input 1, Input 2, AC Power, and Battery
entities are still created. On a device that does not report a corresponding
status (for example, the 508's APak-style inputs), that entity remains `unknown`.
You can disable those unsupported entities on the device page. They are not
silently reassigned to a different status, so existing automations keep their
meaning. Other models keep their existing entities and status interpretation;
the additional sensors are created only for statuses actually reported.

All problem sensors use the existing integration rule: `on` if `isFault` or
`alarmActiveValue` is truthy, otherwise `off` for a present status. `unknown`
means the expected device or status entry is missing. `unavailable` means an update
failed or the device disappeared from the cloud response. Neither means healthy.
Newly reported additional statuses are discovered at setup; reload the integration
if a firmware update changes the list.

## Usage examples

See [generic Home Assistant examples](examples/README.md) for:

- A 508 fault notification using Home Assistant persistent notifications.
- An APak input alarm notification.
- An optional delayed offline notification.
- A simple 508 dashboard card.

Examples use placeholders and never send silence/reset commands. Review the
cloud status details to decide which alarms need immediate attention. Polling
runs every 60 seconds, so alerts may lag the physical device and depend on the
cloud, internet connection, and Home Assistant. Keep the controller's own alarm
and manufacturer notifications enabled as appropriate.
