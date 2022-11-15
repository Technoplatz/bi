## Technoplatz BI

*It's time to get data-driven with your inner-cycle!*

Technoplatz BI is a low-code, multi-container data application and sharing platform designed to establish and manage a mission critical, data-driven business process without the need to develop software from scratch.

- [Community Edition](#community-edition)
- [Highlights](#highlights)
- [Installation](#installation)
- [Troubleshooting](#troubleshooting)
- [Licensing Options](#licensing-options)
- [About](#about)

## Community Edition

 Considering that each business has its own unique conditions, it offers an optimized and pragmatic solution for three main requirements;

- Self-Service Data Management\
<span style="font-size: small; font-weight: bold;">[DATA APPLICATION](#data-application)</span>
- Complete a process with Business partner data\
<span style="font-size: small; font-weight: bold;">[BI-DIRECTIONAL DATA SHARING](#bi-directional-data-sharing)</span>
- Data Connections and Automation\
<span style="font-size: small; font-weight: bold;">[INTERNAL API](#api)</span>

### Data Application

Technoplatz BI has a cross-platform progressive internal web application with the following modules to manage data-driven business processes in a unique interface instead of spreadsheets and legacy software.

- System Administration\
<sup>Management of the administrative components.</sup>
- CRUD+\
<sup>Performing basic data operations on a unique interface.</sup>
- Actions\
<sup>Running bulk data updates with one-click.</sup>
- Automation\
<sup>Scheduled tasks executed on data blocks.</sup>
- Data Visualization\
<sup>Easy charts, pivot tables and descriptive statistics.</sup>
- Log Tracking\
<sup>Transaction history can be tracked on record basis.</sup>

### BI-directional Data Sharing

The product is designed to provide solutions especially for cases where business partners are the integral part of business processes in terms of the data they need to share and the actions they need to take. For this reason, it provides complementary methods to share data bi-directionally within the **inner-cycle** of customers, suppliers, distributors and other internal departments;

- Data Announcements\
Auto-generated email messages supported with data files and pivot tables that inform business partners and internal departments regarding the data requested from them and the actions they need to take in order to complete a business process.

- Data Connectors\
Live and read-only links allow business partners to securely access and download raw data associated with them through Microsoft Excel or other business intelligence tools.

- Web Services\
BI backend enables business partners to securely perform basic data entry and updates over internal API connections to reply data requests announced to them.

### API

The internal Application Programming Interface has been developed in a monolithic structure with the Python programming language. With its object-oriented structure it runs multiple background services asynchronously.

- Internal Functions\
<sup>Core modules and remote data access.</sup>
- External Functions (Web Services)\
<sup>İş ortaklarının erişimi için Secure remote access ability.</sup>
- CronJobs\
<sup>Runs scheduled Automation tasks.</sup>

## Highlights

Technoplatz BI is designed as a self-service and containerized business application to be managed by companies of various sizes and users of all levels. Containerization means that an application runs in isolated runtime environments called containers with its dependencies, configuration files and operating system. This approach provides sustainability and significant cost advantages in the management of mission critical business processes;

- **Dedicated**. Runs on your own cloud. Not shared.
- **Self Service**. Management of your data is now totally under your control.
- **Platform Independent**. It can be installed on Windows, Linux or Mac.
- **Open Source**. Everyone can review the codes and learn from them a lot.
- **Flexible**. It has the sweet smell of JSON data structure.
- **Scalable**. Starts small and grows as needed.
- **Data Sciences Ready**. Accessible from other BI tools and Excel.
- **ISO Friendly**. Empowers the **ISO 27001** certification process, not a stopper.

### Used Technologies

Technoplatz BI is powered by the leading open source information technologies;

- [Docker Compose](#https://docs.docker.com/compose/)
- [MongoDB](#https://www.mongodb.com)
- [Python](#https://www.python.org)
- [Pandas](#https://pandas.pydata.org)
- [Ionic Angular TS](#https://ionicframework.com)
- [GitHub](#https://github.com)

## Installation

The installation of the product consists of steps must follow each other. In order to run the required commands [GiT](https://git-scm.com) must be installed on your computer and a certain level of command line experience is required.

#### Setting up a Docker Environment
Technoplatz BI runs on the Docker which is an open platform for developing, shipping, and running applications. You can install Docker Desktop on your computer for free or buy a hosted service from the leading cloud providers by following below instructions.

- [Microsoft Azure](https://azure.microsoft.com/en-us/services/kubernetes-service/docker/), [Google Cloud](https://cloud.google.com/marketplace/docs/container-images), [AWS](https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa), [DigitalOcean](https://marketplace.digitalocean.com/apps/docker), [IBM Cloud](https://www.ibm.com/de-de/cloud/learn/docker)
- [Windows](https://docs.docker.com/desktop/install/windows-install), [Linux](https://docs.docker.com/desktop/install/linux-install), [Mac OS](https://docs.docker.com/desktop/install/mac-install)

As your platform is ready, you can start to perform the installation steps;

1. Establish an SSH connection to the platform to perform the latest OS updates.\
Don't forget to reboot the system after the updates are complete.

    ```bash
    apt update && apt upgrade -y
    ```

    ```bash
    reboot
    ```

2. Reconnect to the platform to clone the official product repository from Github. Then go to **bi** folder which is going to be clonned.

    ```bash
    git clone https://github.com/technoplatz/bi.git
    ```
    ```bash
    cd bi
    ```

3. Edit the ".env" file, replace the sample values with your own data and save the file. Changes should only be made in the "user parameters" section. It is recommended that changes in system parameters be made only by advanced users.

    ```bash
    TZ=Europe/Berlin
    DOMAIN=localhost
    USER_EMAIL=bi@company.com
    USER_NAME=John Doe
    COMPANY_NAME=Acme Company Inc.
    FROM_EMAIL=bi@company.com
    FROM_NAME=Technoplatz
    ```

    <sup>**TZ:** Time zone of your platform's location.\
    **DOMAIN:** Leave it "localhost" for testing or personal use.\
    **USER_EMAIL:** E-mail address of Administrator user.\
    **USER_NAME:** Name and surname of Administrator user (eg. John Doe).\
    **COMPANY_NAME:** Legal business name of your organization.\
    **FROM_EMAIL:** Sender address (From) of the e-mails sent by the system.\
    **FROM_NAME:** Name or nickname appears next to the sender address.</sup>

    <sup>TZ must be entered according to the official TZ format (eg. America/New_York)\
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones</sup>

4. Uygulamanın güvenliğini sağlayan anahtarları set ediniz.\
\
**API KEY (secret-bi-apikey)**\
Lokal kullanım için anahtar belirlemeniz gerekmez, sistem jenerik bir anahtar kullanır ancak internet ortamında 24 karaktere kadar harf ve sayıdan oluşan bir API anahtarı kullanılmalıdır. Güvenlik açısından [Production, Madde 10](#production) 'da belirtilen şekilde bir anahtar tanımlayarak aşağıdaki komut ile kaydediniz.\
\
**Database Password (secret-mongo-password)**\
\
**Sendgrid Api Key (secret-sendgrid-apikey)**\
It is used for sending automated emails over the Twilio [Sendgrid](#https://sendgrid.com) which is one of the leading e-mail API service providers. Please find the detailed information about how to obtain an API key on Sendgrid. https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key\
\
--

    ```bash
    echo -n "********" > .secret-bi-apikey
    ```
    ```bash
    echo -n "********" > .secret-mongo-password
    ```
    ```bash
    echo -n "********" > .secret-sendgrid-apikey
    ```

5. Start the containers by keeping them up and running at the background. This step may take a couple of minutes depending on your internet bandwidth;

    ```bash
    docker-compose up --detach --remove-orphans
    ```

#### Kick-off

In order to open your first session go to the following address in your web browser, click the "Sign in" button, enter your email and password which you provided in the .env file.

```bash
http://localhost:8100
```

You can log out and exit the platform safely after the installation is complete. Technoplatz BI will continue to run in the background and restart automatically when the platform is rebooted.

## Troubleshooting

Unlike the Enterprise Edition the Community Edition does not provide any official support for platform maintenance and troubleshooting. As long as the system resources are not exceeded you are not expected to encounter a serious problem but the actions to be taken for certain situations are explained below;

- To restart BI by receiving the latest software updates;

    ```bash
    docker-compose pull && docker-compose up --detach --remove-orphans
    ```

- To stop the system;

    ```bash
    docker-compose down
    ```

- To make room for resources when needed;

    ```bash
    docker system prune
    ```

- To track the system logs of a certain service;

    ```bash
    docker-compose logs -f | grep 'api'
    ```

- To perform operating system updates and reboot regularly;

    ```bash
    apt update && apt upgrade -y
    ```
    ```bash
    reboot
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

<div class="licensing">

| | Community Edition | Enterprise Edition |
| :--- | :---: | :---: |
|  Hosting | Self Hosted | SaaS |
|  Database | MongoDB 6 | MongoDB 6 |
|  DB Replication | Yes [3 internal nodes] | Yes [3 nodes] |
|  DB Transactions | Yes | Yes |
|  Web App Firewall | No | Yes |
|  <span style="white-space: nowrap;">Two-Factor Authentication</span> | Yes | Yes |
|  Support | No | Yes |
|  Custom Domain | Yes | Yes |
|  Custom Branding | Not Allowed | Yes |
|  Licensing | GNU AGPL v3.0 | GNU AGPL v3.0 + SLA |
|  Pricing | Free | [Get a Quote](#) |

</div>

## About
Official Web Site\
[https://bi.technoplatz.com](https://bi.technoplatz.com)

### Author
Mustafa Mat [@mustafamat](https://www.github.com/mustafamat)\
Founder, Technoplatz IT Solutions GmbH\
<sup>Senior Developer - Data Sciences, Statistics B.Sc.</sup>

--
<link rel="stylesheet" href="https://raw.githubusercontent.com/Technoplatz/bi/dev0/.github/md.css">