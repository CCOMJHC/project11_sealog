# project11_sealog

Tools to inteface ROS with <https://github.com/OceanDataTools/sealog-server>.

## Nodes

### sealog_telemetry_sender

Listens to Odometry and tf and sends position data to sealog server as a comma delimited string via UDP. The string is terminated with a linefeed.

The fields are:

timestamp, lat, lon, heading, cog, sog

Units are degrees for angles, m/s for sog and ISO 8601 for the timestamp.
  
#### Parameters

- host: Target hostname or IPaddress
- port: Target UDP port
- period: Minimum time in seconds between data reports. Default is 1s.
