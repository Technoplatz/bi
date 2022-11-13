## Technoplatz BI Community Edition

*It's time to get data-driven with your inner-cycle!*

- [What is Technoplatz BI](#what-is-technoplatz-bi)
- [Highlights](#highlights)
- [Installation](#installation)
- [Management](#management)
- [Licensing Options](#licensing-options)
- [About](#about)

## What is Technoplatz BI

Technoplatz BI is a low-code multi-container Data Application platform designed to manage mission critical business processes without the need to develop software from scratch. Considering that each business has its own unique conditions a pragmatic solution which combined under three main topics is provided.

- [Data Application](#data-application)
- [BI-directional Data Sharing](#bi-directional-data-sharing)
- [API](#application-programming-interface-api)

### Data Application

It is a cross-platform progressive web application contains the following basic functions required to manage a business process.

- Administration\
<sup>Self-service management of key system components.</sup>
- Basic Data Operations and Actions (CRUD+)\
<sup>Performing the basic data operations as well as search, import and Actions.</sup>
- Automation\
<sup>Scheduled or one-click tasks executed on data blocks.</sup>
- Data Visualization\
<sup>Descriptive statistics and chart definitions.</sup>
- Log Tracking\
<sup>Transaction history tracking on a record basis.</sup>

### BI-directional Data Sharing

Technoplatz BI is designed for situation where business partners are the integral part of a process in terms of the data source and the actions they need to take. For this reason, it provides two beneficial solutions about bi-directional data sharing by addressing the issues in the [Inner-Cycle](bi-directional-data-sharing) consisting of customers, suppliers, distributors, service providers and other internal company departments;

- Data Announcements\
<sup>Making data request to business partners and get responses.</sup>

- Live Data Connectors\
<sup>Secure and read-only access to shared data through Excel.</sup>

### API

The internal Application Programming Interface has been developed in a monolithic structure with the Python programming language. With its object-oriented structure it runs multiple background services asynchronously.

- Internal Functions\
<sup>Core modules and remote data access.</sup>
- External Functions (Web Services)\
<sup>Secure remote access ability.</sup>
- CronJobs\
<sup>Runs scheduled Automation tasks.</sup>

## Highlights

#### Advantageous

- Your data is now totally under your control with Its **self service** approach.
- Platform independent. Runs on the cloud, on-premises or PCs.
- It has the sweet smell of **flexible** JSON data structure.
- Scalable. Starts small and grows as needed.
- It is **open source** so everyone can review codes and learn from them a lot.
- Data Sciences Ready Accessible from other BI tools and Excel.
- Empowers the **ISO27001** certification process, not a stopper.

#### Technologies

Technoplatz BI is built on open source information technologies with proven power and reliability. This approach provides sustainability and significant cost advantages in the management of critical business processes.

- [Docker Compose](#https://docs.docker.com/compose/) \
<sup>A tool developed to help define and share multi-container applications.</sup>
- [MongoDB](#https://www.mongodb.com) \
<sup>A document database used to build highly available and scalable internet applications.</sup>
- [Python](#https://www.python.org) \
<sup>A high-level programming language supports multiple paradigms.</sup>
- [Pandas Library](#https://pandas.pydata.org) \
<sup>An open source data analysis and manipulation tool built on top of the Python language.</sup>
- [Ionic Angular TS](#https://ionicframework.com) \
<sup>A framework for building cross-platform client applications using HTML and TypeScript.</sup>
- [GitHub](#https://github.com) \
<sup>The leading version control system designed to handle CI/CD.</sup>

## Installation

The installation of the system consists of three steps that must follow each other. In order to perform these steps [GiT](https://git-scm.com) must be installed on your computer and a certain level of command line experience on Terminal is required.

1. Docker Environment\
Technoplatz BI runs on the Docker which is an open platform for developing, shipping, and running applications. You can buy a hosted system from the leading cloud providers or install Docker Desktop on your computer for free by following the instructions at the links below;

    - [Microsoft Azure](https://azure.microsoft.com/en-us/services/kubernetes-service/docker/), [Google Cloud](https://cloud.google.com/marketplace/docs/container-images), [AWS](https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa), [DigitalOcean](https://marketplace.digitalocean.com/apps/docker), [IBM Cloud](https://www.ibm.com/de-de/cloud/learn/docker)
    - [Windows](https://docs.docker.com/desktop/install/windows-install), [Linux](https://docs.docker.com/desktop/install/linux-install), [Mac OS](https://docs.docker.com/desktop/install/mac-install)

2. Connect to the platform via SSH and perform the recent OS updates immediately.

    ```bash
    apt update && apt upgrade -y
    ```

3. Reboot the platform after the update is complete.

    ```bash
    reboot
    ```

4. Reconnect to the platform and clone the official BI repository from Github.

    ```bash
    git clone https://github.com/technoplatz/bi.git
    ```

5. Go to "bi" folder which is going to be created.

    ```bash
    cd bi
    ```

6. Edit the ".env" file, replace the sample values in user parameters section with your own data and save the file.

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


7. Uygulamanın güvenliğini sağlayan API anahtarını set ediniz. Lokal kullanım için anahtar belirlemeniz gerekmez, sistem jenerik bir anahtar kullanır ancak internet ortamında 24 karaktere kadar harf ve sayıdan oluşan bir API anahtarı kullanılmalıdır. Güvenlik açısından [Production, Madde 10](#production) 'da belirtilen şekilde bir anahtar tanımlayarak aşağıdaki komut ile kaydediniz.

    ```bash
    echo -n "your-bi-apikey" > .secret-bi-apikey
    ```

8. Set a database password.

    ```bash
    echo -n "your-database-password" > .secret-mongo-password
    ```

9. It is used for sending automated emails over the Twilio [Sendgrid](#https://sendgrid.com) which is one of the leading e-mail API service providers. Please find the detailed information about how to obtain an API key on Sendgrid. https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key

    ```bash
    echo -n "your-sendgrid-apikey" > .secret-sendgrid-apikey
    ```

10. Start the containers by keeping them up and running at the background. This step may take 2-3 minutes depending on your bandwidth;

    ```bash
    docker-compose up --detach --remove-orphans
    ```

11. To open your first session go to the following address in your web browser, click the "Sign in" button and enter your email and password provided in the .env file.

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

### Author
Mustafa Mat [@mustafamat](https://www.github.com/mustafamat)\
Founder, Technoplatz IT Solutions GmbH\
<sup>Senior Developer - Data Sciences, Statistics B.Sc.</sup>

--
<link rel="stylesheet" href="https://raw.githubusercontent.com/Technoplatz/bi/dev0/.github/md.css">