# Impf-Termin-Tester

This repository provides a tool to automatically query the website of the German vaccination program.

With a given registration code, this tool detects if appointments for vaccinations become available.

Different notification channels (e.g. e-mail or push notification) are provided to notify the user.

## Contributors

Andreas Doerr (andreasdoerr@gmx.net)

## Installation

Setup and activate a conda environment with the required dependencies with
the following command.
```
conda env create -f environment.yml
conda activate impf_termin_tester
```
The `impf_termin_tester` package can be installed by running
```
pip install -e .
```

## Running

A example script for running the impf-termin-tester is available in [example.py](example.py).

### Vaccination Website URLs

A list of URLs with the registration code can be given to the tool. These URLs
should be in the format 
```
"https://XXX-iz.impfterminservice.de/impftermine/suche/XXXX-XXXX-XXXX/YYYYY/"
```
The tool will iteratively query each individual vaccination side to check for
available appointments.

### Setup Browser Automation

The tool is currently based on the selenium browser automation package to control
the Chrome browser. The paths to the browser executable and the corresponding
browser driver need to be set in the [example.py](example.py).

More information on the installation of Selenium and the required executables can be found in
[Selenium installation](https://selenium-python.readthedocs.io/installation.html#drivers)).

### Setup Notification Channels

The tool can take a list of notification channels. Currently this includes

 * Push notifications (via the https://www.pushsafer.com/ service)
 * E-Mail notifications (via SMTP or Windows Outlook API)
 * Disk export (writing screenshot and website to the hard-disk)
 
For each channel, specific details (e.g. target e-mail address, output-folder, etc.)
are required to be filled into the [example.py](example.py).

For further information about the push notification channel check out the
https://www.pushsafer.com/ service.

#### Outlook E-Mail Notification (Windows ONLY)

Notifications can be send via Outlook e-mails. This currently requires the
`pywin32` package for the Windows OS. This package can be installed via
```
conda install pywin32
```
An example for instantiating the `OutlookNotification` can be found in the [example.py](example.py).

## References

 * German vaccination program: https://www.impfterminservice.de/impftermine
 * Selenium browser automation: https://selenium-python.readthedocs.io/installation.html
 * Push notifications: https://www.pushsafer.com/
