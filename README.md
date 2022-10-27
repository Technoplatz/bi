## Technoplatz BI Community Edition

*It's time to get data-driven with your inner-cycle!*

- [What is Technoplatz BI](#what-is-technoplatz-bi)
- [Highlights](#highlights)
- [Installation](#installation)
- [Management](#management)
- [Licensing Options](#licensing-options)
- [About](#about)

## What is Technoplatz BI

Technoplatz BI is a data application and sharing platform that provides many useful features to empower those who try to manage critical business processes on spreadsheets or legacy software. The system's flexible and pragmatic solution is under three main topics, considering that each business process has its own specific conditions;

- [Self-service Database](#self-service-database)
- [Data Application](#data-application)
- [API](#api)

### Self-service Database

BI is an excellent choice for those who want to build a new system to manage a data-driven business process. With professional-grade features you can easily handle critical and intense tasks without needing to be a data expert;

- JSON based flexible structure
- Unlimited data collections
- Unique, indexed and mandatory fields
- Parent-child relations
- Three nodes replication
- Transactions support
- Scalability
- Automated backups

### Data Application

It is a web-based application that contains key functions to help complete a business process end-to-end. Considering that every job has its own special conditions, it is equipped with features that offer optimal and pragmatic solutions;

Main Features
- Create and manage data collections
- Data import from files
- Basic data operations (CRUD)
- Actions
- Visualization
- Data annoucements
- Live data connectors

Administration
- Collection and field management
- Inner-cycle management
- Action management
- Firewall and permission management
- Backup and restore
- API access management
- Log tracking

### API

- skjhfglsdhfglskdfg

## Highlights

- Self service. Your data is now under your control, completely.
- Platform independent. Containerized. Runs on any cloud, on-premises or PCs.
- Flexible. It has the sweet smell of JSON data structure.
- Scalable. Starts small, grows when needed.
- Open source. Everyone can review codes, learn from them a lot.
- Data sciences. Accessibility from other BI tools, AI processes and Excel.
- ISO27001 Support. Empowers the certification process, not a stopper.

## Installation

There are four steps you need to complete to start using BI. In order to run the commands you must have [GiT](https://git-scm.com) installed on your computer and also have a certain level of experience with Terminal.

### Step 1

#### Setting a Docker Platform

Docker is an open platform for developing, shipping, and running applications. You can install it on your computer for free or buy a managed service from any of the leading providers. The links below will help you about how to establish a Docker environment on the cloud and on-premises;

- [Microsoft Azure](https://azure.microsoft.com/en-us/services/kubernetes-service/docker/), [Google Cloud](https://cloud.google.com/marketplace/docs/container-images), [AWS](https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa), [DigitalOcean](https://marketplace.digitalocean.com/apps/docker), [IBM Cloud](https://www.ibm.com/de-de/cloud/learn/docker)
- [Windows](https://docs.docker.com/desktop/install/windows-install), [Linux](https://docs.docker.com/desktop/install/linux-install), [Mac OS](https://docs.docker.com/desktop/install/mac-install)

#### The first touch
After the installation is complete, perform the recent updates and reboot. If you need an administrator right, add `sudo` to the beginning of the commands;

```bash
apt update && apt upgrade -y
```
```bash
reboot
```

### Step 2
#### Cloning the Official Repository
The system uses Docker Compose technology to load, start, restart or stop services as well as the installation of required components. Download the official BI repository from Github;

```bash
git clone https://github.com/technoplatz/bi.git
```

Then go to `bi` folder which is going to be downloaded;

```bash
cd bi
```

### Step 3
#### 3.1 Settings Required Parameters
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
FROM_NAME="Technoplatz BI"
```

<sub>**TZ:** Time zone of your platform's location must be entered according to the official TZ format (eg. America/New_York). https://en.wikipedia.org/wiki/List_of_tz_database_time_zones is the link for more info about TZ.\
**DOMAIN:** Leave it "localhost" for testing or personal use.\
**USER_EMAIL:** E-mail address of Administrator user.\
**USER_NAME:** Name of Administrator user (eg. John Doe).\
**COMPANY_NAME:** Enter legal business name of your organization.\
**FROM_EMAIL:** This address appears as "From" in automatic e-mails sent by the system.\
**FROM_NAME:** A name or nickname that appears next to the sender e-mail address.\
**SENDGRID_API_KEY:** An API key used for sending automated emails over Sendgrid. Please find the detailed information about how to obtain an API key for Technoplatz BI. https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key</sub>

#### 3.2 Settings Secrets

#### BI API Key
Uygulamanın güvenliğini sağlayan anahtardır. İnternete açık olmayan lokal kullanım için anahtar belirlemeniz gerekmez, sistem jenerik bir anahtar kullanır ancak internet ortamında 24 karaktere kadar harf ve sayıdan oluşan karışık bir API anahtarı kullanılmalıdır. Güvenlik açısından [Production, Madde 10](#production) 'da belirtilen şekilde bir anahtar tanımlayarak aşağıdaki komut ile kaydediniz;

```bash
echo -n "your-bi-apikey" > .secret-bi-apikey
```

#### Database Password

```bash
echo -n "your-database-password" > .secret-mongo-password
```

#### Sendgrid API key
It is used for sending automated emails over the Twilio [Sendgrid](#https://sendgrid.com) which is one of the leading e-mail API service providers. Please find the detailed information about how to obtain an API key on Sendgrid. https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key
```bash
echo -n "your-sendgrid-apikey" > .secret-sendgrid-apikey
```

### Step 4

#### Kick-Off
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

1. Define **bi**.company.com and **api.bi**.company.com subdomains in your name server and forward them to the IP address of your [Docker platform](#step-1) by adding an "A" record for each.
2. Change DOMAIN parameter to **bi**.company.com in .env file.
3. Get subdomains behind a web application firewall (WAF) and make the required security settings in accordance with your corporate policy.
4. Enable HTTPS access.
5. Activate a "health check" procedure for the public ports of the Docker platform.
6. Check for system updates of the Docker platform regularly.
7. Schedule a regular backup procedure and keep the files in safe place.
8. Complete the necessary SPF authorization and DMARC policy settings for FROM_EMAIL address defined in .env file so that posts are not rejected as Junk by recipients.
9. Get your Docker platform behind a cloud firewall and configure the access settings according to your corporate security policy.

## Licensing Options
The system is provided in two licensing options;

- Community Edition
- Enterprise Edition

#### COMPARISON

<div class="licensing">

| | Community Edition | Enterprise Edition |
| :--- | :--- | :--- |
|  Hosting | Self hosted | SaaS on Azure, GCP, DigitalOcean|
|  Database | MongoDB 6 | MongoDB 6 |
|  DB Replication | Yes [3 internal nodes] | Yes [3 nodes] |
|  DB Transactions | Yes | Yes |
|  External Security | No | Cloudflare |
|  2FA | Yes | Yes |
|  Support | No | Yes |
|  Custom Domain | Yes | Yes |
|  Custom Branding | Not Allowed | Yes |
|  Licensing | GNU Affero General Public License v3.0 | GNU Affero General Public License v3.0 + SLA |
|  Pricing | Free | [Get a Quote](#) |

</div>

## About
Official Web Site\
[https://bi.technoplatz.com](https://bi.technoplatz.com)

#### Author
Mustafa Mat [@mustafamat](https://www.github.com/mustafamat)\
Founder, Technoplatz IT Solutions GmbH\
<sup>Senior Developer - Data Sciences, Statistics B.Sc.</sup>

<link rel="stylesheet" href=".github/md.css">