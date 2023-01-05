## Technoplatz BI - Community Edition

It's time to get data-driven with your [Inner-Cycle](#business-highlights)!

- [What is Technoplatz BI](#what-is-technoplatz-bi)
- [How to Get Started](#how-to-get-started)
- [Maintenance](#maintenance)
- [Licensing Options](#licensing)
- [About](#about)

## What is Technoplatz BI

Technoplatz BI is a [no-code](#what-is-no-code), multi-container data application and data sharing platform designed to manage business processes without developing software from scratch. It provides optimized and pragmatic solutions for the main requirements of many data-driven process by considering that each business has its own unique conditions;

- [Data Application](#data-application)
- [BI-Directional Data Sharing](#bi-directional-data-sharing)
- [Internal API](#api)

### Business Highlights

Technoplatz BI is being developed for those whose strategy is to make their business **data-driven**.

- **Cloud Platform on Solution Basis**\
It works for the companies want to build a new system to move their mission critical processes currently being managed on spreadsheets or legacy software to a sustainable, secure and cost-effective Cloud platform without investing in hardware infrastructure and software development services.

- **Sharing within an Inner-Cycle**\
It allows organizations to share data within the circle that surrounds customers, suppliers, business partners and internal departments. It can also be used as an "interface" by Enterprises that can not open their online global systems to local suppliers due to company policies.

- **No-code Platform Empowers Its Users**\
Technoplatz BI essentially designed for business users, not developers. Even though no coding skills required for the platform to use, users learn basics of JSON structure easily and naturally without having to study to become a data expert. This approach also creates a data culture within the company.

#### What is No-code?

The widely accepted meaning of no-code term is an application development approach that does not require computer programming skills. No-code platforms use some visual interfaces to allow users to develop their own "App" without knowledge of any programming language. Unlike many no-code platforms, Technoplatz BI empowers users to create and publish their own "solution" run on their own platform.

| No-code Platforms | Technoplatz BI |
| :--- | :--- |
|  Designed for business users | Designed for business professionals |
|  For developing simple or medium Apps | For building solutions to be data-driven |
|  Very easy to use | Very beneficial to use |
|  Provide limited capabilities | Provide required capabilities |
|  Customized by built-in cosmetic components | Customized by JSON structures |

### Highlights

The main approach is to combine sustainability with quality and low cost;

- **Open Source**\
<sup>Everyone can review the codes on GitHub and learn from them a lot.</sup>
- **Containerized**\
<sup>Applications and OS run in an isolated environment together.</sup>
- **Dedicated**\
<sup>Runs in your own cloud, on-premise servers and even on your laptop.</sup>
- **Platform Independent**\
<sup>It can be installed on Windows, Linux or Mac.</sup>
- **Scalable**\
<sup>You can start small and grow as needed.</sup>
- **Flexible Data Structure**\
<sup>It has the sweet smell of flexible JSON data structure.</sup>
- **Cloud Native**\
<sup>Scalable hybrid application is being developed with modern CI/CD methods.</sup>
- **Data Sciences Ready**\
<sup>Enables data transfer into BI tools and Microsoft Excel.</sup>

#### ISO 27001

Technoplatz BI contributes positively to the certification processes of company information systems. Open source availability of codes and security policy on GitHub, user privileges, access rights, backup policy, logging features and the using of modern CI/CD methods in the development process provide advantages especially in ISO 27001 audits.

### Data Application

Technoplatz BI includes an internal progressive web application that allows you to manage data-driven processes in a unique cross-platform interface. It is a powerful alternative for those who are trying to handle their data operations on spreadsheets or legacy software.

- **CRUD+**\
<sup>Performing basic data operations.</sup>
- **Actions**\
<sup>One-click conditional bulk data update.</sup>
- **Automations**\
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

It provides a solution for those who are planning to create their own [API](#api) platform to get integrated with outer world. The internal API has been developed in Python programming language with object-oriented approach allows multiple background services to run simultaneously and asynchronously.

- **Internal Functions**\
Runs core modules and allow data sharing.

- **Web Services**\
Web services allow users to perform data operations remotely. Permissions can be assigned on operation basis and restricted by special filters.

### Used Technologies

Technoplatz BI Community Edition is powered by the leading open source information technologies;

- [Docker Compose](https://docs.docker.com/compose)
- [MongoDB Cluster](https://www.mongodb.com)
- [Python](https://www.python.org)
- [Pandas](https://pandas.pydata.org)
- [Angular Typescript](https://ionicframework.com)
- [GitHub](https://github.com)

## How to Get Started

The system runs on Docker platform which is the leading open source virtualization technology for developing, shipping and running business grade applications. Before to get started you can install Docker on your personal computer or server for free or buy a hosted service from many Cloud providers.

Guides for installing Docker on leading Platforms;

- [Microsoft Azure](https://azure.microsoft.com/en-us/services/kubernetes-service/docker/), [Google Cloud](https://cloud.google.com/marketplace/docs/container-images), [AWS](https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa), [DigitalOcean](https://marketplace.digitalocean.com/apps/docker), [IBM Cloud](https://www.ibm.com/de-de/cloud/learn/docker)
- [Windows](https://docs.docker.com/desktop/install/windows-install), [Linux](https://docs.docker.com/desktop/install/linux-install), [Mac OSX](https://docs.docker.com/desktop/install/mac-install)

<div style="font-size: 13px; line-height: normal;">
System Requirements:<br />
The minimum configuration for the system to work properly on the Docker platform is 2 CPU, 4GB Ram, 20GB Hard Disk. This configuration should be increased in proportion to workload and the number of connections to be established.</div>

### Installation

The installation of the product consists of steps must follow each other. In order to run the necessary commands [GiT](https://git-scm.com) must be installed on your computer and a certain level of command line experience is required.

<div style="font-size: 13px; line-height: normal;">
NOTE<br />Please consider that since the installation steps requires root privileges, it is necessary to add <strong>sudo</strong> in front of many commands below if the connected user does not have admin rights.
</div>

#### 1. The First Touch

Many Docker platforms provided in the ISP marketplaces may not be up-to-date in terms of the operationg system. It is recommended to run a system update initially and reboot afterwards.

```bash
apt update && apt upgrade -y
```

```bash
reboot
```

#### 2. Clonning the Repository

Reconnect to the platform to download the official Technoplatz BI repository from [GitHub](https://github.com/technoplatz/bi.git).

```bash
git clone https://github.com/technoplatz/bi.git
```

Go to **bi** folder created.

```bash
cd bi
```

#### 3. Setting Environment Parameters

Edit the **.env** file, replace the sample values with your own and save the file. Changes should only be made in the user parameters section at the top of the file.

```bash
TZ=Europe/Berlin
DOMAIN=localhost
ADMIN_EMAIL=bi@company.com
ADMIN_USER_NAME=John Doe
COMPANY_NAME=Acme Company Inc.
FROM_EMAIL=bi@company.com
```

<sup>**TZ:** Time zone of your platform's location.\
**DOMAIN:** Leave it "localhost" for testing or personal use.\
**ADMIN_EMAIL:** E-mail address of Administrator user.\
**ADMIN_USER_NAME:** Name and surname of Administrator user (eg. John Doe).\
**COMPANY_NAME:** Legal business name of your organization.\
**FROM_EMAIL:** Sender address (From) of the e-mails sent by the system.</sup>

<sup>TZ must be entered according to the official **TZ** format (eg. America/New_York)\
https://en.wikipedia.org/wiki/List_of_tz_database_time_zones</sup>

#### 4. Setting the Secrets

There are three parameters that must be included in certain files in terms of system security. You can create the necessary parameters and files in accordance with the rules by using the commands below.

| Secret Name | File Name |
| :--- | :--- |
|  BI API Key | .secret-bi-apikey |
|  Database Password | .secret-mongo-password |
|  Sendgrid API Key | .secret-sendgrid-apikey |

- API Key\
It is the internal API key that must be generated if the system is used in a real internet environment. The following command will generate a new random key and write it into the related file. The API key can be changed later but this operation requires to [restart the containers](#restarting-containers).

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

Although the Community Edition is provided for testing purposes or local use, it is also allowed to be published in a production environment as per the AGPL v3.0 license agreement. However, before getting started some actions should be taken in terms of performance and security issues. You can make a request for the free electronic document regarding this subject [here](#).

## Licensing

Technoplatz BI is an open source platform provided with two licensing options;

- **Community Edition**\
<sup>Free to use under AGPL v3.0 License terms.</sup>
- **Commercial SaaS Edition (Brezel)**\
<sup>Managed Hosted and Supported under SLA terms.</sup>

| | Community Edition | SaaS Edition |
| :--- | :---: | :---: |
|  Hosting | Self Hosted | Managed |
|  Database | MongoDB 6 | MongoDB 6 |
|  DB Cluster | Yes [3 internal nodes] | Yes [3 nodes] |
|  Web App Firewall | No | Yes |
|  Two-Factor Authentication | Yes | Yes |
|  Technical Support | No | Yes |
|  Custom Development Service | No | Paid |
|  Custom Domain | Not Recommended | Yes |
|  Sendgrid E-mail API | Self Subscribed | Yes |
|  License | Affero GPL v3.0 | Service Level Agreement |
|  Pricing | Free | [Request a Quote](#) |

## About

Official Web Site\
[https://bi.technoplatz.com](https://bi.technoplatz.com)

## Author

Mustafa Mat [@mustafamat](https://www.github.com/mustafamat)
<div style="font-size: 13px; line-height: normal;">
Founder, Technoplatz IT Solutions GmbH<br />
Senior System Analist Developer<br />
Data Sciences & Statistics B.Sc.
</div>
--