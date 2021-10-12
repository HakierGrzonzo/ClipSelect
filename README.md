# ClipSelect

A website that generates gifs based on quotes found in subtitles.

Currently hosted [here](https://grzegorzkoperwas.site) on a **docker swarm** cluster in my basement. Because overengineering is my jam.

---------------

Made with flask and materializecss.

## How it works:

Before starting the application, run `ffmpegScripts/videoConverter.py` to convert your directory of video files to a format that this application uses. By default it outputs that to `/gluster/ClipSelectDB/`

After doing that you can run `./build.sh` to build docker images and upload them to repository at `localhost:5000`. Then run `docker-compose up` (and change volume binds to something you like).

What will happen next:

- MySQL will initialize a database.
- `ffmpegScripts/Importer.py` will import generated files into MySQL.
- A flask application will be started.
- A worker script will be started and will check for jobs.

### Operation:

User navigates to a show of their choosing and searches for quotes. When the user
hovers their pointing device of choice over a quote, previous and nex subtitle will
be showed for more context.

When user requests a gif, webserver checks in table `jobs` if it is available. If it
is not, then it adds it with a `status = 0`. `ffmpegScripts/worker.py` than fetches
this request and uses ImageMagick to turn jpegs into a gif and stores it in
`ClipSelectDB/gifs`.

Meanwhile the webserver serves a waiting page that automatically reloads, thus eventually
loading the gif.
