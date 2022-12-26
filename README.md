## Technoplatz BI - Community Edition

It's time to get data-driven with your [Inner-Cycle](#the-inner-cycle)!

- [What is Technoplatz BI](#what-is-technoplatz-bi)
- [How to Get Started](#how-to-get-started)
- [Maintenance](#maintenance)
- [Licensing Options](#licensing-options)
- [About](#about)

## What is Technoplatz BI

Technoplatz BI is a no-code, multi-container data application and sharing platform designed to manage data-driven business processes without the need to develop software from scratch. Considering each business has its own unique conditions it provides an optimized and pragmatic solution for the main requirements explained below;

- [**Data Application**](#data-application)\
<sup>CRUD, ACTIONS AND AUTOMATION</sup>
- [**BI-Directional Data Sharing**](#bi-directional-data-sharing)\
<sup>ANNOUNCEMENTS AND LIVE CONNECTIONS</sup>
- [**Internal API**](#api)\
<sup>WEB SERVICES & INTEGRATION</sup>

### The Inner-Cycle

Technoplatz BI is being developed for those whose strategy is to make their business **data-driven**. For this reason, it uses an appropriate approach to establish a data culture within a circle surrounds customers, suppliers, business partners and internal departments of an organisation.

- It works for the organizations want to move critical business process currently managed on spreadsheets to a sustainable business tool without developing software from scratch.

- It's a powerful alternative for those who are looking for a secure and cost-effective solution to manage and share business data easily.

- It provides a cloud based solution for companies to create their own API platform to get integrated with outer systems.

- In many areas it can be used as an "Interface" for enterprises who are not allowed to open their global systems to local business partners, providers and suppliers due to some company policies.

### Highlights

The tool is designed as a self-service and containerized business application that can be managed by companies of various sizes and users with different skills. Containerization means that applications run in isolated runtime environment called containers with their dependencies, configuration files and operating system. This approach provides advantage of sustainability and significant cost reduction in the management of mission critical business processes;

- **Dedicated**\
<sup>Runs on your own cloud. Not shared.</sup>
- **Self Service**\
<sup>Management of your data-driven processes is now totally under your control.</sup>
- **Platform Independent**\
<sup>It can be installed on Windows, Linux or Mac.</sup>
- **Open Source**\
<sup>Everyone can review the codes at GitHub and learn from them a lot.</sup>
- **Flexible**\
<sup>It has the sweet smell of flexible JSON data structure.</sup>
- **Cloud Native**\
<sup>Containerized scalable hybrid app developed with modern CI/CD methods.</sup>
- **Data Sciences Ready**\
<sup>Enables data transfer into other BI tools and Microsoft Excel.</sup>

### Data Application

Technoplatz BI's internal progressive web application module allows you to manage data-driven processes in a unique cross-platform interface. It is a powerful alternative for those who are trying to handle their data operations on spreadsheets or legacy software.

- **CRUD+**\
<sup>Performing basic data operations.</sup>
- **Actions**\
<sup>One-click conditional bulk data update.</sup>
- **Automation**\
<sup>Scheduled smart tasks executed on data collections.</sup>
- **Data Visualization**\
<sup>Shareable charts, pivots and descriptive statistics.</sup>
- **System Administration**\
<sup>Management of administrative components.</sup>

### BI-Directional Data Sharing

The product is designed to provide complementary methods for bi-directional data sharing especially for cases where business partners are the integral part of a processes in terms of the latest situation that keeping them to be informed about, the data they are expected to share and the actions they need to take.

- **Data Announcements**\
Sending an instant message is one of the most efficient ways to share the latest status of data-driven process so that business partners can be informed about the required actions to take. Announcements can be scheduled and powered by attaching data files and pivot tables.

- **Data Links**\
Sharing a secure data URL instead of sending data itself can be more useful method for some cases and allows subscribers to establish live data connections from Microsoft Excel or other BI tools.

### API

The internal Application Programming Interface has been developed in Python programming language. Its object-oriented structure allows multiple background services to run simultaneously and asynchronously.

- **Internal Functions**\
<sup>Runs core modules and allow data sharing.</sup>
- **Web Services**\
Web services allow users to perform data operations remotely. Permissions can be assigned on operation basis and restricted by special filters.

#### ISO 27001
Technoplatz BI empowers [ISO](#iso-27001) certification processes. The open source structure of the system, the codes published on GitHub, the security policy and the using of modern CI/CD methods provide advantages in ISO 27001 audits in terms of the following topics;\
Appendix A-8, A-9, A-10, A-11, A-12, A-13, A-17

### Used Technologies

Technoplatz BI is powered by the leading open source information technologies;

- [Docker Compose](https://docs.docker.com/compose)
- [MongoDB Replicaset](https://www.mongodb.com)
- [Python](https://www.python.org)
- [Pandas](https://pandas.pydata.org)
- [Angular Typescript](https://ionicframework.com)
- [GitHub](https://github.com)

## How to Get Started

Technoplatz BI runs on Docker platform which is the leading open source virtualization technology for developing, shipping and running business grade applications. You can install Docker on your personal computer for free or buy a hosted service from many cloud providers.

Guides for installing Docker Platform on;

- [Microsoft Azure](https://azure.microsoft.com/en-us/services/kubernetes-service/docker/), [Google Cloud](https://cloud.google.com/marketplace/docs/container-images), [AWS](https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa), [DigitalOcean](https://marketplace.digitalocean.com/apps/docker), [IBM Cloud](https://www.ibm.com/de-de/cloud/learn/docker)
- [Windows](https://docs.docker.com/desktop/install/windows-install), [Linux](https://docs.docker.com/desktop/install/linux-install), [Mac OSX](https://docs.docker.com/desktop/install/mac-install)

<div style="font-size: 13px; line-height: normal;">
System Requirements:<br />
The minimum configuration for Technoplatz BI to work properly on the Docker platform is 2 CPU, 4GB Ram, 20GB Hard Disk. This configuration can be increased in proportion to the number of connections to be established, instant CPU load and the amount of data to be processed.</div>

### Installation

The installation of the product consists of steps must follow each other. In order to run the necessary commands [GiT](https://git-scm.com) must be installed on your computer and a certain level of command line experience is required.

#### 1. The First Touch
Docker platforms available in the ISP marketplaces may not be up-to-date initially. It is recommended to establish an SSH connection to the platform and perform a system update immediately. The platform should be rebooted after the updates are complete.

```bash
apt update && apt upgrade -y
```

```bash
reboot
```

#### 2. Downloading the Application
Reconnect to the platform again to clone the official BI repository from GitHub.

```bash
git clone https://github.com/technoplatz/bi.git
```

Go to **bi** folder created.

```bash
cd bi
```

#### 3. Setting the Environment Parameters
Edit the ".env" file, replace the sample values with your own data and save the file. Changes should only be made in the user parameters section at the top of the file.

```bash
TZ=Europe/Berlin
DOMAIN=localhost
USER_EMAIL=bi@company.com
USER_NAME=John Doe
COMPANY_NAME=Acme Company Inc.
FROM_EMAIL=bi@company.com
```

<sup>**TZ:** Time zone of your platform's location.\
**DOMAIN:** Leave it "localhost" for testing or personal use.\
**USER_EMAIL:** E-mail address of Administrator user.\
**USER_NAME:** Name and surname of Administrator user (eg. John Doe).\
**COMPANY_NAME:** Legal business name of your organization.\
**FROM_EMAIL:** Sender address (From) of the e-mails sent by the system.</sup>

<sup>TZ must be entered according to the official TZ format (eg. America/New_York)\
https://en.wikipedia.org/wiki/List_of_tz_database_time_zones</sup>

#### 4. Setting the Secrets

There are three parameters that must be included in certain files in terms of system security. You can create the necessary parameters and files in accordance with the rules by using the commands below.

| Secret Name | File Name |
| :--- | :--- |
|  BI API Key | .secret-bi-apikey |
|  Database Password | .secret-mongo-password |
|  Sendgrid API Key | .secret-sendgrid-apikey |

- BI API Key\
It is the internal API key that must be generated if the system is used in a real internet environment. The following command will generate a new random key and write it into the related file. The API key can be changed later but this operation requires [restarting the containers](#restarting-containers).

    ```bash
    echo $(date | sha256sum | base64 | head -c 24) > .secret-bi-apikey
    ```

- Database Password\
It is the password of the authorized database user. The following command will generate a new random password and write it into the related file. Database password can be changed later but this operation requires [restarting the containers](#restarting-containers).

    ```bash
    echo $(date | sha256sum | base64 | head -c 10) > .secret-mongo-password
    ```

- Sendgrid API Key\
It is used for sending automated emails over the [Sendgrid](#https://sendgrid.com) which is the leading e-mail sender provider. Please find the further information about how to obtain an API key on Sendgrid at https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key. After creating an API key in the Sendgrid, copy this key, paste it into the starred area below and run the command.

    ```bash
    echo -n "********" > .secret-sendgrid-apikey
    ```

#### 5. Starting Containers

Enter the command below to start the containers by keeping them up and running in the background. It can take up to 30 seconds till after containers creation for Technoplatz BI to be functional. You can log out and exit the platform safely after the installation is complete. Technoplatz BI continues to run at the background and restarts automatically as the platform is rebooted.

```bash
docker-compose up --detach --remove-orphans
```

#### 6. Signing In

In order to open your first session go to the following address in your web browser, click the "Sign in" button, enter your email and password which you provided in the .env file.

```bash
http://localhost:8100
```

## Maintenance

Unlike the enterprise edition the community edition doesn't provide any official support about maintenance and troubleshooting issues. As long as the system resources are not exceeded you are not expected to encounter a serious problem however the actions to be taken for certain situations are explained in below topics.

#### Getting the Latest Updates

```bash
docker-compose pull && docker-compose up --detach --remove-orphans
```

#### Starting Containers

```bash
docker-compose up --detach --remove-orphans
```

#### Stopping Containers

```bash
docker-compose down
```

#### Cleaning

Performing the system updates and restarting of containers frequently can create unnecessary files that may fill up your disk space. The command below helps you to remove all unused resources to make more room for the BI;

```bash
docker system prune
```

#### Log Tracking

- To track the container logs;

    ```bash
    docker-compose logs -f
    ```

- To track the logs of a certain container;

    ```bash
    docker-compose logs -f | grep 'api'
    ```

#### Operationg System Updates

To perform operating system updates and reboot regularly.

```bash
apt update && apt upgrade -y
```
```bash
reboot
```

## Production

Even though the Community Edition is provided for testing and local use, there is no stopper to using the system in a live business environment in terms of licensing. However, before starting to use the system in a real business environment, some recommended actions should be taken in terms of performance and security issues. You can access the electronic document prepared on this subject [here](#).

## Licensing Options

Technoplatz BI is provided in two licensing options;

- Community Edition
- Enterprise Edition (Brezel)

<div class="licensing">

| | Community Edition | Enterprise Edition |
| :--- | :---: | :---: |
|  Hosting | Self Hosted | SaaS |
|  Integration | No | Yes |
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
Senior System Analist & Developer\
Data Sciences, Statistics B.Sc.

--