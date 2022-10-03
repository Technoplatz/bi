## Technoplatz BI Community Edition
*It's time to get data-driven with your inner-cycle!*

Technoplatz BI is a low-code data application and data sharing solution that empowers those who manage data-driven business processes. Community Edition is free to use under the circumstances of [AGPL-3.0 license terms](https://github.com/Technoplatz/bi/blob/main/LICENSE).

- [Highlights](#what-is-technoplatz-bi)
- [How to install](#how-to-install)
- [Management](#management)
- [About](#about)

## Highlights

- Data Application\
Basic data operations and end-to-end process management on a self-service platform that supports flexible data structure.

- BI-directional data sharing\
Secure data sharing with business partners via live data connections and messaging.

- Visualization\
Basic statistics and real-time visualization on business data without the need to be a data expert.

- Integration\
Get responses to your data requests via your own API instead of Spreadsheets.

## How to install
Thanks to its multi-container structure built on Docker, the system can be run on the cloud, on-preimses and personal computers. Installation consists of four stages. A certain level of command line knowledge is required and it is assumed that you have [GiT](https://git-scm.com) installed on your computer. Please follow the steps below to start working more data-driven;

**STEP 1**\
<sup>SETTING UP A MULTI-CONTAINER PLATFORM</sup>\
In the first stage, the selection and installation of a Docker based system infrastructure is required. You can install Docker on your computer for free or choose a paid, ready-to-use platform from any of the leading cloud service providers. The links below will help you to install Docker environment on the cloud or on-premises;

- On the Cloud: [Microsoft Azure](https://azure.microsoft.com/en-us/services/kubernetes-service/docker/), [Google Cloud](https://cloud.google.com/marketplace/docs/container-images), [AWS](https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa), [DigitalOcean](https://marketplace.digitalocean.com/apps/docker), [IBM Cloud](https://www.ibm.com/de-de/cloud/learn/docker)
- On-premises: [Windows](https://docs.docker.com/desktop/install/windows-install), [Linux](https://docs.docker.com/desktop/install/linux-install), [Mac OS](https://docs.docker.com/desktop/install/mac-install)

**STEP 2**\
<sup>CLONNING THE OFFICIAL REPOSITORY</sup>\
The community edition is a set of applications that running as services. Unlike desktop apps, there is no any traditional installer. The BI tool uses Docker Compose technology to load, run or stop the services as needed. In the second stage, please enter the following command to clone the system folder from the official Github repository.

```bash
git clone https://github.com/technoplatz/bi.git
```

A folder which named `bi` is going to be created in the directory you are in. Please jump into this folder;

```bash
cd bi
```

**STEP 3**\
<sup>SETTING ENVIRONMENT VARIABLES</sup>\
The core parameters which required for the system to work are in the `.env` file. Initially user parameters has been filled with sample values. Before proceeding to the next step, edit `.env` file, replace the sample values in the user parameters section with the actual values according to below instructions and save the file.

```bash
# USER_PARAMETERS
# Change the parameters to actual values before installation.
# --------------------------------
TZ="Europe/Berlin"
DOMAIN="localhost"
USER_EMAIL="bi@company.com"
USER_NAME="John Doe"
COMPANY_NAME="Acme Company Inc."
FROM_EMAIL="bi@company.com"
SENDGRID_API_KEY="SG.********.********"
```

<sub>**TZ:** Time zone of your platform's location must be entered according to the official TZ format (eg. America/New_York). https://en.wikipedia.org/wiki/List_of_tz_database_time_zones is the link for more info about TZ.\
**DOMAIN:** Leave it as "localhost" to test or personal use.\
**USER_EMAIL:** E-mail address of Administrator user.\
**USER_NAME:** First and last names of Administartor user (eg. John Doe).\
**COMPANY_NAME:** Enter legal business name of your organization.\
**FROM_EMAIL:** This address appears as "From" in automatic e-mails sent by the system. Necessary SPF and DMARC settings should be made so that posts are not rejected as junk.\
**FROM_NAME:** A name or nickname that appears next to the sender e-mail address.\
**SENDGRID_API_KEY:** An API key used for sending automated emails over Sendgrid. Please find the detailed information about how to obtain an API key for Technoplatz BI. https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key</sub>

\
**STEP 4**\
<sup>STARTING SERVICES</sup>\
From this point on, `bi` is the system folder and all commands should be run in it.

#### Commands
To start or restart the system and keep it running in the background;

```bash
docker-compose up --build --detach --remove-orphans
```

## Management

To start or restart the system by receiving the latest updates and keep it running in the background;

```bash
docker-compose pull && docker-compose up --build --detach --remove-orphans
```

To stop the system;

```bash
docker-compose down
```

Free up space by cleaning all dangling images and cache;

```bash
docker system prune
```

## About

Official Web Site\
[https://bi.technoplatz.com](https://bi.technoplatz.com)

#### Author
Mustafa Mat [@mustafamat](https://www.github.com/mustafamat)\
Founder, Technoplatz IT Solutions GmbH\
<sub>Senior System Analist Developer\
Data Sciences, Statistics B.Sc.</sub>