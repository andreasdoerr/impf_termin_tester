# Impf-Termin-Tester

This repository provides a tool to support and (partially) automatize the search for available Corona/COVID-19 vaccination appointments.
Currently, this tool only supports the platform [https://www.impfterminservice.de](https://www.impfterminservice.de).
With this platform, appointments can be queried for the following states of Germany:
* Baden-Württemberg
* Brandenburg
* Hamburg
* Hessen
* Nordrhein-Westfalen
* Sachsen-Anhalt

The process for getting an appointment currently comprises several steps
1. Vaccination Center: Select one or multiple vaccination center in your area
2. Registration Code: Obtain a unique registration code for each vaccination center
3. Appointment Search: Search and book available vaccination appointments.
 
With this tool, you can automatize the registration code and appointment search step.
Per default, you would need to manually query your vaccination center and the available appointments over and over.
Instead, the provided tool automatically notifies you once a registration code or appointment becomes available.
Different notification channels (e.g. e-mail or push notification) are provided to notify you, e.g. on your mobile phone.

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

To run the impf-termin-tester, you'll need to set up two main files
1. Your personal start-up script (e.g. `my_impf_termin.py`). An example is available in [example.py](example.py).
2. Your personal configuration file (e.g. `my_impf_termin.toml`). An example is available in [example.toml](example.toml).

To set up the impf-termin-tester for your needs, you'll need to configure
1. Website URLs
2. Browser Automation
3. Notification Channels
Each of these steps is explained in the following sections.

One these steps are completed and your software is set up, you can run the impf-termin-tester via
```
python my_impf_termin.py
```

### Setup Website URLs

The impf-termin-tester can be configured to query
1. Vaccination centers: Check available registration codes for a given vaccination center
2. Appointments: Check available appointments for a given registration code/vaccination center

For both steps, the specific URLs need to be set up in a TOML configuration file.
An example is given in [example.toml](example.toml).
This file provides a list of URLs for both tasks.

#### Vaccination Center URLs

The vaccination center URLs can be obtained by selecting a desired state and vaccination center
from the drop-down list on [https://www.impfterminservice.de](https://www.impfterminservice.de).
After clicking on the "ZUM IMPFZENTRUM" button, one is forwarded to the main site of the specific vaccination center.
The URL of the site should be in the format
```
https://XXX-iz.impfterminservice.de/impftermine/service?plz=XXXXX
```
(replace **X** by the details for the specific vaccination center).

One or multiple vaccination center URLs can be provided in your configuration file `my_impf_termin.toml` (example in [example.toml](example.toml)).
To obtain a registration code from the vaccination center, the tool automatically fills in the required personal information (e.g. age, e-mail, phone-number).
You'll need to provide your personal data in your start-up script `my_impf_termin.py` (example in [example.py](example.py)).

As soon as a registration code has been retreived, you'll be prompted to enter a PIN, which you received via SMS on your mobile-phone.
Once this step is completed, you'll receive an e-mail with the registration code/the link to check for appointments.
This link is needed for the next/last step.

#### Appointment URLs

As soon as you completed the previous step, you'll receive an e-mail with a registration code/a link to a website.
This link contains your registration code and the vaccination center in the following format
```
"https://XXX-iz.impfterminservice.de/impftermine/suche/YYYY-YYYY-YYYY/XXXXX/"
```
where `YYYY-YYYY-YYYY` is your registration code and `XXX` is information about the vaccination center.
A list of one or multiple of these URLs can be provided to the tool in your `my_impf_termin.toml` configuration file.

### Setup Browser Automation

The tool is currently based on the selenium browser automation package to control
the Chrome browser. The paths to the browser executable and the corresponding
browser driver need to be set in the [example.py](example.py).

More information on the installation of Selenium and the required executables can be found in
[Selenium installation](https://selenium-python.readthedocs.io/installation.html#drivers)).

### Setup Notification Channels

The tool can take a list of notification channels. Currently this includes

 * Push notifications
    * via [PushSafer](https://www.pushsafer.com/) service. ATTENTION: only test version is free.
    * via [notify.run](https://notify.run/) service. ATTENTION: not for iOS devices.
 * E-Mail notifications
    * via SMTP email server. ATTENTION: not operational with two factor authentification (e.g. gmail).
    * via Windows Outlook API
 * Disk export (writing screenshot and website to the hard-disk)
 * MQTT broker
 
For each channel, specific details (e.g. target e-mail address, output-folder, etc.)
are required to be filled into the [example.py](example.py).

#### Outlook E-Mail Notification (Windows ONLY)

Notifications can be send via Outlook e-mails. This currently requires the
`pywin32` package for the Windows OS. This package can be installed via
```
conda install pywin32
```
An example for instantiating the `OutlookNotification` can be found in the [example.py](example.py).

#### Push-Notifications via notify-run

One option for sending push-notifications to your mobile phone or computer is 
offered by the [notify.run](https://notify.run/) service. 
This requires the `notify-run` package, which can be installed via
```
pip install notify-run
```
To use the android notification service run the command 
``` 
notify-run register
```
as described [here](https://pypi.org/project/notify-run/) to set up your mobile device for push notifications.

## References

 * German vaccination program: https://www.impfterminservice.de/impftermine
 * Selenium browser automation: https://selenium-python.readthedocs.io/installation.html
 * Push notifications via PushSafer: https://www.pushsafer.com/
 * Push notifications via notify.run: https://notify.run/
