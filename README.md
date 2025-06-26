# **TPMS**

## **Prerequisites**

1. ### Install nvidia drivers

   To intsall nvidia drivers run following command in terminal

   ```bash
   $ sudo ubuntu-drivers autoinstall
   ```

   Alternatively, install desired driver selectively using the `apt` command. For example:

   ```bash
   $ sudo apt install nvidia-driver-525
   ```

   Once the installation is concluded, reboot your system and you are done.

   ```bash
   $ sudo reboot
   ```

   After reboot check if drivers are installed correct by using following command

   ```bash
   $ nvidia-smi
   ```

   This command should show ouput as below

   ```
   Tue Sep  5 11:49:19 2023       
   +-----------------------------------------------------------------------------+
   | NVIDIA-SMI 525.125.06   Driver Version: 525.125.06   CUDA Version: 12.0     |
   |-------------------------------+----------------------+----------------------+
   | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
   | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
   |                               |                      |               MIG M. |
   |===============================+======================+======================|
   |   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0 Off |                  N/A |
   | N/A   45C    P8    N/A /  N/A |     11MiB /  4096MiB |      0%      Default |
   |                               |                      |                  N/A |
   +-------------------------------+----------------------+----------------------+
                                                                                  
   +-----------------------------------------------------------------------------+
   | Processes:                                                                  |
   |  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
   |        ID   ID                                                   Usage      |
   |=============================================================================|
   |    0   N/A  N/A      1206      G   /usr/lib/xorg/Xorg                  4MiB |
   |    0   N/A  N/A      2264      G   /usr/lib/xorg/Xorg                  4MiB |
   +-----------------------------------------------------------------------------+
   
   ```

   If you see such kind of ouput that means, nvidia drivers are installed correctly.

2. ### Install docker

   First, update your existing list of packages:

   ```bash
   $ sudo apt update
   ```

   Next, install a few prerequisite packages which let `apt` use packages over HTTPS:

   ```bash
   $ sudo apt install apt-transport-https ca-certificates curl software-properties-common
   ```

   Then add the GPG key for the official Docker repository to your system:

   ```bash
   $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   ```

   Add the Docker repository to APT sources:

   ```bash
   $ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
   ```

   This will also update our package database with the Docker packages from the newly added repo.

   Make sure you are about to install from the Docker repo instead of the default Ubuntu repo:

   ```bash
   $ apt-cache policy docker-ce
   ```

   You’ll see output like this, although the version number for Docker may be different:

   ```bash
   docker-ce:
     Installed: (none)
     Candidate: 5:19.03.9~3-0~ubuntu-focal
     Version table:
        5:19.03.9~3-0~ubuntu-focal 500
           500 https://download.docker.com/linux/ubuntu focal/stable amd64 Packages
   ```

   Notice that `docker-ce` is not installed, but the candidate for installation is from the Docker repository for Ubuntu 20.04 (`focal`).

   Finally, install Docker:

   ```bash
   $ sudo apt install docker-ce
   ```

   Docker should now be installed, the daemon started, and the process enabled to start on boot. Check that it’s running:

   ```bash
   $ sudo systemctl status docker
   ```

   The output should be similar to the following, showing that the service is active and running:

   ```bash
   Output
   ● docker.service - Docker Application Container Engine
        Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
        Active: active (running) since Tue 2020-05-19 17:00:41 UTC; 17s ago
   TriggeredBy: ● docker.socket
          Docs: https://docs.docker.com
      Main PID: 24321 (dockerd)
         Tasks: 8
        Memory: 46.4M
        CGroup: /system.slice/docker.service
                └─24321 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
   ```

3. ### install docker compose

   To install docker compose use following commands

   ```bash
   $ sudo curl -L "https://github.com/docker/compose/releases/download/2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   ```

   Next, set the correct permissions so that the `docker-compose` command is executable:

   ```bash
   $ sudo chmod +x /usr/local/bin/docker-compose
   ```

   To verify that the installation was successful, you can run:

   ```bash
   $ docker-compose --version
   ```

   You’ll see output similar to this:

   ```bash
   Output
   docker-compose version 1.29.2, build 5becea4c
   ```

4. ### install nvidia docker

   Install the `nvidia-docker2` package and reload the Docker daemon configuration:

   ```bash
   $ sudo apt-get install nvidia-docker2
   $ sudo pkill -SIGHUP dockerd
   ```

   

5. ### Deploy TPMS application

   To deploy TPMS application first clone the repository

   ```bash
   $ git clone https://github.com/GSuntecSolutions/TPMS.git
   ```

   ​	Checkout to respective branch

   ```bash
   $ git checkout Dev
   ```

   ​	Run docker compose command

   ```bash
   $ docker-compose up -d
   ```

6. API Document

​		To view the APIs open following link in browser

​		http://localhost:5000/docs