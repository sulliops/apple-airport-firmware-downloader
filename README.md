# Apple AirPort Firmware Downloader

### Version 1.0.0

*Created by Owen Sullivan, [sulliops.co](https://sulliops.co)*

----

#### What does this script do?

`airport-firmware-downloader.py` fetches a list of available AirPort firmware update files according to model (Base Station, Express, Extreme, Time Capsule, etc.) and generation, then lists the available firmware based on the selected model and allows the user to specify which to download.

The idea for this script was inspired by [gibMacOS](https://github.com/corpnewt/gibMacOS) after I found myself in posession of a handful of AirPort Extreme routers that I'm considering reverse-engineering, if such a thing is possible. [This blog post](https://www.sallonoroff.co.uk/blog/2015/07/apple-airport-firmware-updates/) was a huge help in finding the AirPort firmware catalog.

----

#### Is this script safe?:

In short, it damn well should be.

The script pulls the list of available firmware files from Apple's server directly by default, and will do so as long as Apple leaves the AirPort firmware catalog accessible to the public. The link to the catalog is: [https://apsu.apple.com/version.xml](https://apsu.apple.com/version.xml)

In the event that Apple removes access to this catalog, a backup of the catalog file taken on July 6th, 2023, is hosted within this script's repository as `apsu_catalog.plist` and the script will fall back to it. The link to the hosted catalog backup is: [https://raw.githubusercontent.com/sulliops/apple-airport-firmware-downloader/main/apsu_catalog.plist](https://raw.githubusercontent.com/sulliops/apple-airport-firmware-downloader/main/apsu_catalog.plist)

Should the official catalog go offline, there is no guarantee that the links available in the hosted catalog backup will continue to resolve. The script will display an error in this case.

----

#### Running the script

The script requires two dependencies, which can be installed using Python's `pip` package manager:

```
python3 -m pip install requests
python3 -m pip install tqdm
```

Then, run the script like so:

```
cd apple-airport-firmware-downloader/
python3 airport-firmware-downloader.py
```