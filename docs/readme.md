# Information


# NHC2 Niko Home Control2
## MQTT
### Broker
- payloads: JSON
- port: 8884
- ssl: TLSv1.2
- cert: delivered by Niko  (Not Use)
- user: "hobby"
- password: The JWT is delivered by the Niko programming software

### API
#### Topic
- hobby/control/devices/cmd
- hobby/control/devices/rsp
- hobby/control/devices/evt
- hobby/control/devices/err

#### Device management
- [ ] List all devices
- [ ] Device added event
- [ ] Device removed event
- [ ] Device Display name changed
- [ ] Device Parameter Changed event
#### Device Control
- [ ] Control device, `Method: devices.control`
- [x] Device status changed event, `Method: devices.status`
#### Locations
- [ ] List locations
- [ ] List devices in location
#### System information
- [ ] Time information event
- [ ] System information request
- [ ] System information event
#### Notification
- [ ] List Notifications
- [ ] Update Notification
- [ ] Notification raised event


#### Control Devices

## Requirements
#### Raspberry pi
L'image influxdb pour rasberrypi `arm32v7/influxdb:latest` 
