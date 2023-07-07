### Apple AirPort Firmware Downloader
### Created by: Owen Sullivan | https://sulliops.co | https://github.com/sulliops
### Official script repo: https://github.com/sulliops/apple-airport-firmware-downloader
### Version: 1.0.0

import requests # for HTTP requests
import plistlib # for parsing the APSU catalog
import os # for clearing screen
import sys # for exiting program
from tqdm import tqdm # for download progress bar

# Define dictionary of AirPort Product IDs from https://www.sallonoroff.co.uk/blog/2015/07/apple-airport-firmware-updates/
airPortProductIDs = {
    0: "AirPort Base Station (1999)",
    1: "AirPort Base Station (2001)",
    102: "AirPort Express 802.11g",
    104: "AirPort Extreme 802.11n (1st Generation)",
    105: "AirPort Extreme 802.11n (2nd Generation)",
    106: "AirPort Time Capsule 802.11n (1st Generation)",
    107: "AirPort Express 802.11n (1st Generation)",
    108: "AirPort Extreme 802.11n (3rd Generation)",
    109: "AirPort Time Capsule 802.11n (2nd Generation)",
    113: "AirPort Time Capsule 802.11n (3rd Generation)",
    114: "AirPort Extreme 802.11n (4th Generation)",
    115: "AirPort Express 802.11n (2nd Generation)",
    116: "AirPort Time Capsule 802.11n (4th Generation)",
    117: "AirPort Extreme 802.11n (5th Generation)",
    119: "AirPort Time Capsule 802.11ac",
    120: "AirPort Extreme 802.11ac",
    3: "AirPort Extreme 802.11g"
}

# Function that returns the URL that should be used for the APSU catalog
def getAPSUCatalogURL():
    apsuCatalogURL = None
    # Check if the official APSU catalog is still available from Apple's website
    if requests.head("https://apsu.apple.com/version.xml").status_code == 200:
        # If so, use it
        apsuCatalogURL = "https://apsu.apple.com/version.xml"
    else:
        # Otherwise, use the backup catalog available within this project's repository
        apsuCatalogURL = "https://raw.githubusercontent.com/sulliops/apple-airport-firmware-downloader/main/apsu_catalog.plist"
    
    return apsuCatalogURL

# Function that gets and parses the APSU catalog, then returns a dictionary of firmware update information keyed by AirPort device product ID
def parseAPSUCatalog(catalogURL):
    # Parse the catalog plist (which is apparently just a spicy XML file, in this case)
    apsuCatalogTree = plistlib.loads(requests.get(catalogURL).content)

    # Create a new dictionary
    firmwareUpdatesByProductID = dict()
    # Loop through each product ID
    for airPortProductID in airPortProductIDs:
        # Loop through each firmware update entry in the APSU catalog
        for firmwareUpdate in apsuCatalogTree["firmwareUpdates"]:
            # If the firmware update's product ID matches the current outer loop product ID
            if firmwareUpdate["productID"] == str(airPortProductID):
                # Add the firmware update's model, version, size, and location information to the dictionary
                firmwareUpdatesByProductID.setdefault(airPortProductID, []).append({
                    "model": airPortProductIDs[airPortProductID],
                    "version": firmwareUpdate["version"],
                    "size": firmwareUpdate["sizeInBytes"],
                    "URL": firmwareUpdate["location"]
                })
                
    return firmwareUpdatesByProductID

# Function that prints the script's main menu (incl. list of AirPort devices) and gets/returns user input
def mainMenu(catalog):
    # Loop until the loop is broken
    while True:
        # Clear the terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print a list of all available AirPort devices
        print("Available AirPort devices by product ID:")
        for index, airPortProductID in enumerate(catalog):
            print("\t" + str(index + 1) + ". " + airPortProductIDs[airPortProductID])
        
        # Loop forever again (I hate this)
        while True:
            # Get user input for menu selection
            selection = input("\nInput desired product by number (e.g., 1, 2...) or 'q' to quit: ")
            
            # If the selection is a digit and is within the valid range
            if selection.isdigit() and 1 <= int(selection) <= len(catalog):
                # Pass the corresponding dict key to submenu function
                getFirmwareUpdatesByProductID(catalog, list(catalog.keys())[int(selection) - 1])
                # Break the infinite loop (phew)
                break
            # If the selection is 'q' or 'Q', exit the program
            elif selection.lower() == "q" or selection.lower() == "Q":
                sys.exit(0)
            # Otherwise, print an error message
            else:
                print("Invalid choice, try again...")

# Function that gets a list of firmware updates by product ID and gets/returns user input
def getFirmwareUpdatesByProductID(catalog, ID):
    keepLooping = True
    # Loop until the submenu is exited
    while keepLooping:
        # Clear the terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Get all dict values with associated key
        firmwareUpdates = catalog.get(int(ID), [])
        
        # Print the firmware updates for the associated product ID
        print("Firmware updates for " + airPortProductIDs[int(ID)] + ":")
        for index, firmwareUpdate in enumerate(firmwareUpdates):
            print("\t" + str(index + 1) + ". Version: " + firmwareUpdate["version"] + ", Size (in bytes): " + str(firmwareUpdate["size"]) + ", URL: " + firmwareUpdate["URL"])
        
        # Loop forever again (I hate this)
        while True:
            # Get user input for menu selection
            selection = input("\nInput desired firmware by number (e.g., 1, 2...), 'b' to go back, or 'q' to quit: ")
            
            # If the selection is a digit and is within the valid range
            if selection.isdigit() and 1 <= int(selection) <= len(firmwareUpdates):
                # Call download function
                downloadFirmwareUpdate(firmwareUpdates[int(selection) - 1])
            # If the selection is 'b' or 'B', exit the submenu
            elif selection.lower() == "b" or selection.lower() == "B":
                # Update loop control variable for outer loop
                keepLooping = False
                
                break
            # If the selection is 'q' or 'Q', exit the program
            elif selection.lower() == "q" or selection.lower() == "Q":
                sys.exit(0)
            # Otherwise, print an error message
            else:
                print("Invalid choice, try again...")

# Function to download and save a selected firmware update
def downloadFirmwareUpdate(firmwareUpdate):
    # Check if the provided download link is valid
    if requests.head(firmwareUpdate["URL"]).status_code == 200:
        # Check if downloads folder exists and create it if not
        if not os.path.isdir("firmwareDownloads"):
            os.mkdir("firmwareDownloads")
            
        # Check if sub-folder for model exists in downloads folder and create it if not
        if not os.path.isdir("firmwareDownloads/" + firmwareUpdate["model"].replace(" ", "-")):
            os.mkdir("firmwareDownloads/" + firmwareUpdate["model"].replace(" ", "-"))
        
        # Create full filename by combining the folder structure, the model name (replacing spaces with hyphens), and the version number (plus the existing extension)
        filename = "firmwareDownloads/" + firmwareUpdate["model"].replace(" ", "-") + "/" + firmwareUpdate["model"].replace(" ", "-") + "-" + firmwareUpdate["URL"].rsplit('/', 1)[-1]
        
        # Get the download URL
        response = requests.get(firmwareUpdate["URL"], stream=True)
        # Use a block size of 1 KB for downloading
        blockSize = 1024
        # Get the total file size
        totalSize = int(response.headers.get("content-length", 0))
        
        # Display a message with the filename
        print("\nDownloading firmware update as " + filename)
        # Create a progress bar for the download
        progressBar = tqdm(total=totalSize, unit="B", unit_scale=True)
        
        # Download the file
        with open(filename, "wb") as downloadedFirmware:
            for data in response.iter_content(blockSize):
                progressBar.update(len(data))
                downloadedFirmware.write(data)
                
        # Close the downloaded file
        progressBar.close()
    else:
        print("\nERROR: The requested firmware is not available for download from " + firmwareUpdate["URL"])

# Main function
if __name__ == "__main__":
    # Clear the terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print program intro block
    print("Apple AirPort Firmware Downloader Utility")
    print("Created by: Owen Sullivan | https://sulliops.co | https://github.com/sulliops")
    print("Official script repo: https://github.com/sulliops/apple-airport-firmware-downloader\n")
    
    # Print program notes/warnings
    print("WARNING: Make sure you downloaded this script from the official script repo. Always inspect a script's code before running it.")
    print("WARNING: The developer of this script is not liable for any damage caused to your computer.")
    print("NOTE: All firmware downloads obtained through this script come from Apple directly. Read the script's README for more information.\n")
    
    # Get APSU catalog URL and print it
    catalogURL = getAPSUCatalogURL()
    print("Using APSU catalog URL: " + catalogURL + "\n")
    
    # Require user interaction to continue (just to make things look a bit cleaner in the terminal)
    input("Press Enter to continue...")
    
    # Get the APSU catalog dictionary
    apsuCatalog = parseAPSUCatalog(catalogURL)
    
    # Call the main menu function
    mainMenu(apsuCatalog)