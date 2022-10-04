## Technoplatz BI Community Edition
*It's time to get data-driven with your inner-cycle!*

- [What is Technoplatz BI](#what-is-technoplatz-bi)
- [Product Highlights](#product-highlights)
- [Installation](#installation)
- [Management](#management)
- [License](#license)
- [About](#about)

## What is Technoplatz BI
Technoplatz BI is a low-code, multi-container business software and data sharing platform that provides many beneficial features to empower those trying to manage data-driven processes;

- Self-service application to manage basic data operations.
- BI-directional data sharing methods between user and business partners.
- Descriptive statistics and real-time data visualization.
- API for making data requests and retrieving responses.

## Product Highlights
This section is in progress.

## Installation
Please complete the following steps in order. You must have [GiT](https://git-scm.com) installed on your computer and a certain level of command line knowledge is required.

#### STEP 1
<sup>SETTING A DOCKER PLATFORM</sup>\
Docker is an open platform for developing, shipping, and running applications. You can install it on your computer for free or buy a managed service from any of the leading providers. The links below will help you about how to establish a Docker environment on the cloud and on-premises;

- [Microsoft Azure](https://azure.microsoft.com/en-us/services/kubernetes-service/docker/), [Google Cloud](https://cloud.google.com/marketplace/docs/container-images), [AWS](https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa), [DigitalOcean](https://marketplace.digitalocean.com/apps/docker), [IBM Cloud](https://www.ibm.com/de-de/cloud/learn/docker)
- [Windows](https://docs.docker.com/desktop/install/windows-install), [Linux](https://docs.docker.com/desktop/install/linux-install), [Mac OS](https://docs.docker.com/desktop/install/mac-install)

#### STEP 2
<sup>CLONING THE OFFICIAL BI REPOSITORY</sup>\
The system uses Docker Compose technology to load, start, restart or stop services as well as the installation of required components. Download the official repository from Github;

```bash
git clone https://github.com/technoplatz/bi.git
```

Then go to `bi` folder which is going to be downloaded;

```bash
cd bi
```

#### STEP 3
<sup>SETTING ENVIRONMENT VARIABLES</sup>\
Before proceeding to the next steps, user parameters should be entered once. Please edit the `.env` file, replace the sample values with your own data and save the file.

```bash
# USER_PARAMETERS
# Replace sample values with yours before installation.
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
**DOMAIN:** Leave it "localhost" for testing or personal use.\
**USER_EMAIL:** E-mail address of Administrator user.\
**USER_NAME:** Name of Administrator user (eg. John Doe).\
**COMPANY_NAME:** Enter legal business name of your organization.\
**FROM_EMAIL:** This address appears as "From" in automatic e-mails sent by the system.\
**FROM_NAME:** A name or nickname that appears next to the sender e-mail address.\
**SENDGRID_API_KEY:** An API key used for sending automated emails over Sendgrid. Please find the detailed information about how to obtain an API key for Technoplatz BI. https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key</sub>

#### STEP 4
<sup>KICK-OFF</sup>\
Start the services and keep them up and running in the background. Installation may take 1-2 minutes depending on your internet speed;

```bash
docker-compose up --detach --remove-orphans
```

To open your first session go to the following address in your web browser, click the "Sign in" button and enter your email and password provided in the `.env` file.

```bash
http://localhost:8100
```

## Management
To start or restart the system by keeping it up and running in the background;

```bash
docker-compose up --detach --remove-orphans
```

To start or restart the system by receiving the latest software updates and keep it up and running in the background;

```bash
docker-compose pull && docker-compose up --detach --remove-orphans
```

To stop the system;

```bash
docker-compose down
```

In order to make room for resources when needed;

```bash
docker system prune
```

To take a look at the logs;

```bash
# To display all, except db and only api logs.
docker-compose logs -f
docker-compose logs -f | grep -v 'mongo'
docker-compose logs -f | grep 'api'
```

## Production
Community Edition's default settings are provided for testing and local use. In case the system is used in a real business environment under your subdomain, e.g. **bi.company.com**, there is no stopper for this however the there are crucial security and system requirements recommended (including but not limited to) below must be fulfilled before making the system public. All responsibilities in this regard belongs to the user.
- Define **bi**.company.com and **api.bi**.company.com subdomains in your name server and forward them to the IP address of your [Docker platform](#step-1) by adding an "A" record for each.
- Change DOMAIN parameter to **bi**.company.com in .env file.
- Get your Docker platform behind the cloud firewall and configure the access settings according to your corporate security policy.
- Get subdomains behind a web application firewall (WAF) and make the required security settings in accordance with your corporate policy.
- Enable HTTPS access.
- Activate a "health check" procedure for the public ports of the Docker platform.
- Check for system updates of the Docker platform regularly.
- Schedule a regular backup procedure and keep the files in safe place.
- Complete the necessary SPF authorization and DMARC policy settings for FROM_EMAIL address defined in .env file so that posts are not rejected as Junk by recipients.

## License
Community Edition is free under the [GNU Affero General Public License v3.0](https://github.com/Technoplatz/bi/blob/main/LICENSE) terms.

## About
Official Web Site\
[https://bi.technoplatz.com](https://bi.technoplatz.com)

#### Author
Mustafa Mat [@mustafamat](https://www.github.com/mustafamat)\
Founder, Technoplatz IT Solutions GmbH\
<sup>Senior Developer - Data Sciences, Statistics B.Sc.</sup>