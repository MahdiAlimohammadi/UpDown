# UpDown

A simple, lightweight file server for easy uploads, downloads, and file management.

## Setting Up a Python File Server with Systemd

Follow these steps to configure and run a Python-based file server using Systemd.

## 1. Prepare the File Server Directory

```bash
# Create the directory for file storage
mkdir -p /home/fileserver/

# Set appropriate ownership and permissions
chown -R nobody:nogroup /home/fileserver/
chmod 777 /home/fileserver/
```

## 2. Create the Systemd Service File

```bash
# Edit the systemd service file for the file server
vim /etc/systemd/system/file_server.service
```

Add the following content to the file:

```ini
[Unit]
Description=Python File Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/fileserver/file_server.py
WorkingDirectory=/home/fileserver
Restart=always
User=nobody
Group=nogroup

[Install]
WantedBy=multi-user.target
```

This configuration sets the file server to run as the `nobody` user and `nogroup`, ensuring minimal privileges for security. The service will start after the network is available and will automatically restart if it crashes.

## 3. Reload Systemd and Start the Service

```bash
# Reload systemd to recognize the new service
systemctl daemon-reload

# Enable and start the file server service
systemctl enable file_server.service --now

# Check the status of the service to ensure it is running
systemctl status file_server.service
```

## 4. Verify the File Server

To verify the file server is running, check that it is accessible via the appropriate port or by checking the service status.

---
You can now access the file server by navigating to http://<server-ip>:8888 in your web browser.
