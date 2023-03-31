The spider starts 2 browsers for dicscovery
## Try it out
1. create a virtualenv with python3 and activate it
2. install dependencies from requirements.txt. `pip install -r requirements.txt`
3. If running on a remote shell, the script needs a display to start the browsers (we'll be using headless browsers later). Install vnc4server with `apt-get install vnc4server`and run `vnc4server` to start a virtual display. note the name of the display (usually hostname:1) and set environment variable `DISPLAY` to that value.
4. Download Gecko Driver from [here](https://github-production-release-asset-2e65be.s3.amazonaws.com/25354393/113b5380-234f-11e9-8f1e-2eff36d0eff4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20190225%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20190225T081811Z&X-Amz-Expires=300&X-Amz-Signature=e29c7bbab1d56a0dda17cb285955df302c7dda193d669d0dbadfccec430ca171&X-Amz-SignedHeaders=host&actor_id=35478281&response-content-disposition=attachment%3B%20filename%3Dgeckodriver-v0.24.0-linux64.tar.gz&response-content-type=application%2Foctet-stream) and extract to /usr/bin
5. create folder with name "dl2"
6. run `python spider.py
7. If you would like to view the display from vncserver, install a vnc client/viewer like xvnc4viewer and run it with the ip of the server and display number as arguments. For example,`xvnc4viewer 192.168.1.123:1'
