# Data Collection Tool

## Running on AWS
First, make sure your AWS instance has NVIDIA drivers installed. In my case, I have:
```
$ nvidia-smi
Thu May 13 15:44:10 2021
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 465.19.01    Driver Version: 465.19.01    CUDA Version: 11.3     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA Tesla T4     On   | 00000000:00:1E.0 Off |                    0 |
| N/A   28C    P8     9W /  70W |      9MiB / 15109MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|    0   N/A  N/A      5848      G   /usr/lib/xorg/Xorg                  8MiB |
+-----------------------------------------------------------------------------+
```

Create a file called `xorg_conf` with this content
```
Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BusID          "PCI:0:30:0"
EndSection


Section "Screen"
    Identifier     "Screen0"
    Device         "Device0"
    DefaultDepth    24
    Option         "AllowEmptyInitialConfiguration" "True"
    SubSection     "Display"
        Depth       24
        Virtual 1024 768
    EndSubSection
EndSection


Section "ServerLayout"
    Identifier     "Layout0"
    Screen 0 "Screen0" 0 0
EndSection
```
Then, run the following command
```
sudo Xorg -noreset +extension GLX +extension RANDR +extension RENDER -config ~/xorg_conf :0
```

### More detailed steps

1. Go to aws.amazon.com
2. Log in with h2r.tellex.lab@gmail.com with password BaxterFriends1! as Root User
3. Go to EC2 -> Instances
4. If you see "x running instances", click the 'x' so that stopped instances will be listed too
5. Right click on the row "ai2thor-exp7" -> "Start instance"
6. Wait for about half a minute, then Refresh.
7. When you see "2/2 checks passed", the instance is successfully started.
8. Now, download the h2r_g4dm.pem file. Place it under $HOME/.aws/ . Change its permission to 400.
9. Then, go back to the console, right click on the instance 'ai2thor-exp7' again, select "Connect".
10. It will show a page that has an ssh command, something like ssh -i h2r_g4dm.gem ubuntu@.... Run that command. SSH into the instance

Now that you are in the instance, run
11. screen  Press Enter if it shows a welcome page. It should show a blank screen with status at the bottom.
12. Now, run  the following to start the X server
```
sudo Xorg -noreset +extension GLX +extension RANDR +extension RENDER -config ~/xorg_conf :0
```
13. Then press `Ctrl+o c` (first press control and o together, then press c). this creates a new window.
14. The run
cd ~/repo/dialogue-object-search/dls/data/collection/tool
./run.ssh
15. Now you should be able to visit the <ec2 instance IP>:5000/ and see the webapp (assuming you have added your IP to the security group. See instructions here for adding rule to security group)
16. Now you can proceed to collect data.
17. After the session finishes, go to `
~/repo/dialogue-object-search/dls/data/collection/sessions
You should see Session_<Session_ID>_<timestamp> folder.
18. Compress that folder.
19. Download the compressed folder to your local machine using scp -i h2r_g4dm.pem ubuntu@...:<path_to_session_compressed_file>   <local path>
20. Upload the downloaded compressed file to Google Drive.
Good luck, my friend
