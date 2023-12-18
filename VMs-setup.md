# Virtual Machines Service Setup

This instructions and additional information aim to help setting up the environment containing the services used to simulate a network and create the NWDAF dataset

## Requirements

### Hardware

TODO
### Software
TODO

## Prerequisites

Before installing the services, clone 3 new virtual machines from the one used as base for the UERANSIM installation. Then to make sure the OS is updated:

### 1. Update the OS

```
sudo apt update && sudo apt upgrade -y
```

### 2. Change the hostname

```
sudo nano /etc/hostname
```
**NOTE:** As the VMs are clones, don't forget to change their hostnames to avoid confusion

### 3. Change the [FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name)

```
sudo nano /etc/hosts
```

Update the hostname (and/or domain) on the line that begins with the IP `127.0.1.1`. If unsure, use the same hostname as the used on the command above.

### 4. Install a player on UERANSIM

To load the video on UERANSIM's machine, install the MPV player

```
sudo apt install mpv
```

## VM Setup

### Ping machine

As the ping utility comes by default on the OS, this is the easiest machine to setup. Once the system is installed, just run the first three commands from the [prerequisites section](./VMs-setup.md#prerequisites).

### Webserver machine

For this machine we will use the free5GC website. After the OS is setup (and the three commands from the [prerequisites section](./VMs-setup.md#prerequisites) are executed), follow the instructions below which are based on [its repo README file](https://github.com/free5gc/free5gc.github.io#readme). 

**TIP:** To better compatibility, install the pip requirements inside a python venv and use this env to run the webserver

Clone the repo

```
git clone https://github.com/free5gc/free5gc.github.io.git
```
Enter its folder, create a python virtual environment and install the requirements

```
cd free5gc.github.io/
python -m venv pyvenv
source pyvenv/bin/activate
pip install -r requirements.txt
```

Now, to run the server

```
mkdocs serve -a 172.16.0.212:8000
```
**NOTE:** Use the command above to start the web server (change the IP if needed)

At this point, one should have a webservice running and serving a free5GC's website local instance

Download the page list using

```
cd # get back to the home folder
TODO: wget command
```

<!-- TODO: Create an autodeploy sript -->

### Video repository machine

The last one will have an example video file that will be streamed by the UE

1. Install the webserver

```
sudo apt install apache2
```
2. Download the video file to the machine

```
TODO: wget command
```

3. Copy it to the folder located in `/var/www/html/`

4. Change the file permissions to allow webserver users to view it
```
cd /var/www/html/
sudo chmod 644 example-clock.mp4
```

5. The file will be available at

```
http://172.16.0.211/example-clock.mp4
```

**NOTE:** Adjust the IP address if needed

## VM Usage

1. Run the free5GC and UERANSIM machines

2. Setup the UE connection with the core

3. Start capturing packets on the gtp-created interface `upfgtp`

4. Run the client applications on the UERANSIM machine

**Note:** Don't forget to connect using the tun interface `uesimtun0`

### Applications

#### Ping

ping -I uesimtun0 172.16.0.210

Capture command
```
tshark -i upfgtp -J "pfcp icmp gtp" -w /home/netlab/tshark/1ping-capture.pcap -c 1000
```

#### Webconsole

Route the packets using the tunnel

```
sudo ip route add 172.16.0.212/32 dev uesimtun0
```
**NOTE:** The configuration setup by the command above is deleted after a system reboot

```
wget -i pagelist.txt > /dev/null
```

Capture command

```
tshark -i upfgtp -J "pfcp http gtp" -w /home/netlab/tshark/3web-capture.pcap -c 1000
```
#### Video

Route the packets using the tunnel

```
sudo ip route add 172.16.0.211/32 dev uesimtun0
```
**NOTE:** The configuration setup by the command above is deleted after a system reboot

Then choose one of the commands below to start streaming the video
```
# If the VM has graphical interface
mpv http://172.16.0.211/example-clock.mp4
# If not, to run on console only mode use
mpv --vo=caca http://172.16.0.211/example-clock.mp4 
```
Source for the command above: [vitux.com](https://vitux.com/play-a-video-in-the-ubuntu-command-line-just-for-fun/)

Capture command
```
tshark -i upfgtp -J "pfcp http gtp" -w /home/netlab/tshark/2video-capture.pcap -c 1000
```
