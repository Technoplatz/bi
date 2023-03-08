# Technoplatz BI

It's time to get data-driven with your [inner-cycle!](#business-highlights)

- [What is Technoplatz BI](#what-is-technoplatz-bi)
- [How to Get Started](#get-started)
- [Installation](#installation)
- [Maintenance](#maintenance)
- [Licensing Options](#licensing)
- [About](#about)

## What is Technoplatz BI

Technoplatz BI is a [no-code](#what-is-no-code), multi-container data application and data sharing platform designed to manage business processes without developing software from scratch. It provides optimized and pragmatic solutions for the main requirements of many data-driven process by considering that each business has its own unique conditions;

- [Data Application](#data-application)
- [BI-Directional Data Sharing](#bi-directional-data-sharing)
- [Internal API](#api)

## Business Highlights

Technoplatz BI is being developed for those whose strategy is to make their business **data-driven**.

- **Cloud Platform on Solution Basis**\
It works for the companies want to build a new system to move their mission critical processes currently being managed on spreadsheets or legacy software to a sustainable, secure and cost-effective Cloud platform without investing in hardware infrastructure and software development services.

- **Sharing within an Inner-Cycle**\
It allows organizations to share data within the circle that surrounds customers, suppliers, business partners and internal departments. It can also be used as an "interface" by Enterprises that can not open their online global systems to local suppliers due to company policies.

- **No-code Platform Empowers Its Users**\
Technoplatz BI essentially designed for business users, not developers. Even though no coding skills required for the platform to use, users learn basics of JSON structure easily and naturally without having to study to become a data expert. This approach also creates a data culture within the company.

### What is No-code?

The widely accepted meaning of no-code term is an application development approach that does not require computer programming skills. No-code platforms use some visual interfaces to allow users to develop their own "App" without knowledge of any programming language. Unlike many no-code platforms, Technoplatz BI empowers users to create and publish their own "solution" run on their own platform.

| No-code Platforms | Technoplatz BI |
| :--- | :--- |
|  Designed for business users | Designed for business professionals |
|  For developing simple or medium Apps | For building solutions to be data-driven |
|  Very easy to use | Very beneficial to use |
|  Provide limited capabilities | Provide required capabilities |
|  Customized by built-in cosmetic components | Customized by JSON structures |

## Highlights

The main approach is to combine sustainability with quality and low cost;

- **Open Source**\
Everyone can review the codes on GitHub and learn from them a lot.
- **Containerized**\
Applications and OS run in an isolated environment together.
- **Dedicated**\
Runs in your own cloud, on-premise servers and even on your laptop.
- **Platform Independent**\
It can be installed on Windows, Linux or Mac.
- **Scalable**\
You can start small and grow as needed.
- **Flexible Data Structure**\
It has the sweet smell of flexible JSON data structure.
- **Cloud Native**\
Scalable hybrid application is being developed with modern CI/CD methods.
- **Data Sciences Ready**\
Enables data transfer into BI tools and Microsoft Excel.

### ISO 27001

Technoplatz BI contributes positively to the certification processes of company information systems. Open source availability of codes and security policy on GitHub, user privileges, access rights, backup policy, logging features and the using of modern CI/CD methods in the development process provide advantages especially in ISO 27001 audits.

## Data Application

Technoplatz BI includes an internal progressive web application that allows you to manage data-driven processes in a unique cross-platform interface. It is a powerful alternative for those who are trying to handle their data operations on spreadsheets or legacy software.

- **CRUD+**\
Performing basic data operations.
- **Actions**\
One-click conditional bulk data update.
- **Automations**\
Scheduled smart tasks executed on data collections.
- **Data Visualization**\
Shareable charts, pivots and descriptive statistics.
- **System Administration**\
Management of administrative components.

## BI-Directional Data Sharing

The product is designed to provide complementary methods for bi-directional data sharing especially for cases where business partners are the integral part of a processes in terms of the latest situation that keeping them to be informed about, the data they are expected to share and the actions they need to take.

- DATA ANNOUNCEMENTS
Sending an instant message is one of the most efficient ways to share the latest status of data-driven process so that business partners can be informed about the required actions to take. Announcements can be scheduled and powered by attaching data files and pivot tables.

- LIVE DATA LINKS
Sharing a secure data URL instead of sending data itself can be more useful method for some cases and allows subscribers to establish live data connections from Microsoft Excel or other BI tools.

## API

It provides a solution for those who are planning to create their own [API](#api) platform to get integrated with outer world. The internal API has been developed in Python programming language with object-oriented approach allows multiple background services to run simultaneously and asynchronously.

- **Internal Functions**\
Runs core modules and allow data sharing.

- **Web Services**\
Web services allow users to perform data operations remotely. Permissions can be assigned on operation basis and restricted by special filters.

## Used Technologies

Technoplatz BI Community Edition is powered by the leading open source information technologies;

- [Docker Engine](https://docs.docker.com)
- [Docker Compose](https://docs.docker.com/compose)
- [MongoDB v6 Cluster](https://www.mongodb.com)
- [Python](https://www.python.org)
- [Pandas](https://pandas.pydata.org)
- [Angular Typescript](https://ionicframework.com)
- [GitHub](https://github.com)

## Get Started

Technoplatz BI runs on Docker Platform which is the leading open source virtualization technology for developing, shipping and running business grade applications. Before getting started what you need to do is to install Docker Platform for free or buy a hosted service provided by one of the leading Cloud Providers.

Installing Guides for Cloud Environment:
[Microsoft Azure](https://azure.microsoft.com/en-us/services/kubernetes-service/docker/) [Google Cloud](https://cloud.google.com/marketplace/docs/container-images), [AWS](https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa), [DigitalOcean](https://marketplace.digitalocean.com/apps/docker), [IBM Cloud](https://www.ibm.com/de-de/cloud/learn/docker)

Installing Guides for On-premises:
[Windows](https://docs.docker.com/desktop/install/windows-install), [Linux](https://docs.docker.com/desktop/install/linux-install), [Mac OS](https://docs.docker.com/desktop/install/mac-install)

System Requirements:
The minimum configuration for the system to work properly on the Docker platform is 2 CPU, 4GB Ram, 20GB Hard Disk. This configuration should be increased in proportion to workload and the number of connections to be established.

## Installation

The installation steps described below must be performed in the order given. Please consider that a certain level of command line skill is required and it may be necessary to add `sudo` in case connected user does not have root privileges.

### 1. The First Touch

Docker platforms sold on ISP marketplaces might be a couple of updates behind in terms of the operating system as of the date you purchase. Therefore, it is highly recommended to run a system update initially and reboot the system. Please reconnect to the platform after the system reboots.

```bash
apt update && apt upgrade -y && reboot
```

### 2. Download and Install

Open a Terminal session, copy paste and run the first command below to download the service script from the official [GitHub](https://github.com/technoplatz/bi.git) repository and get the installation started with the second command afterwards. Follow the messages coming to the console for the required actions and the result of the operation.

#### Linux and Mac OS

```bash
curl -Lso technoplatz/bi.sh --create-dirs \
"https://raw.githubusercontent.com/Technoplatz/bi/main/bi-sh" \
&& chmod +x technoplatz/bi.sh \
&& cd technoplatz
```

```bash
./bi.sh install
```

### 3. Setting Parameters

Edit `.env` file, replace the sample values with your own and save the file.

```bash
...
TZ=#time-zone
DOMAIN=#localhost
ADMIN_EMAIL=#admin-user-business-email
ADMIN_USER_NAME=#admin-user-fullname
COMPANY_NAME=#company-legal-name-for-ssl
DEPARTMENT_NAME=#department-name-for-ssl
COUNTRY_CODE=#country-code-for-ssl
STATE_NAME=#state-or-province-name-for-ssl
CITY_NAME=#city-name-for-ssl
SMTP_PORT=#email-server-port-eg-465-or-587
SMTP_SERVER=#email-server-address
SMTP_USERID=#email-user-id-or-email
SMTP_PASSWORD=#email-password-of-smtp-user-id
FROM_EMAIL=#email-sender-email-adress-for-auto-messages
API_KEY=#platform-apikey
...
```

- Domain must be `localhost` for local use.
- Time zone must be entered according to the official format (eg. America/New_York)\
<https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>
- Community edition generates self signed TLS certificates with the company information to be provided above for the internal communication of the database cluster to be encrypted.
- It is recommended to use [Sendgrid](https://www.sendgrid.com) email services for SMTP server.

A sample configuration;

```bash
TZ=Europe/Berlin
DOMAIN=localhost
ADMIN_EMAIL=john@yourcompany.com
ADMIN_USER_NAME=John Doe
COMPANY_NAME=Acme Inc.
DEPARTMENT_NAME=Finance
COUNTRY_CODE=DE
STATE_NAME=North-Rhein-Westfalen
CITY_NAME=Berlin
SMTP_PORT=465
SMTP_SERVER=smtp.sendgrid.net
SMTP_USERID=apikey
SMTP_PASSWORD=SG.****.****
FROM_EMAIL=bi@yourcompany.com
API_KEY=61c09da62f1f9ca9357796c9
```

### 4. Starting Containers

Enter the command below to start the containers by keeping them up and running in the background. It can take up to 20 seconds till after containers creation for Technoplatz BI to be fully functional. You can log out and exit the platform safely after the installation is complete. Technoplatz BI continues to run at the background and restarts automatically as the platform is rebooted.

```bash
./bi.sh start
```

### 5. Sign in

In order to open your first session go to the following address in your web browser, click the "Sign in" button, enter your email and password which you provided in the .env file.

```bash
http://localhost:8100
```

## Maintenance

Unlike the enterprise edition the community edition doesn't provide any official support about maintenance and troubleshooting issues. As long as the system resources are not exceeded you are not expected to encounter a serious problem however the actions to be taken for certain situations are explained in below topics.

### BI Maintenance

You can take over your system by controlling the Docker containers.

Getting the latest updates;

```bash
./bi.sh update
```

Starting or restarting the containers;

```bash
./bi.sh start
```

Stopping containers;

```bash
./bi.sh stop
```

Cleaning dangling system resources;

```bash
./bi.sh prune
```

Log Tracking

```bash
./bi.sh logs api
```

### Operating System Maintenance

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


| | Community Edition | aPaaS Edition |
| :--- | :---: | :---: |
|  Hosting | Self Hosted | Managed Hosted |
|  DB Cluster | Yes [3 internal nodes] | Yes [3 nodes] |
|  WebApp Firewall | No | Yes |
|  Two-Factor Authentication | Yes | Yes |
|  Technical Support | No | Yes |
|  Custom Development Service | No | Yes (Paid) |
|  Custom Domain | No | Yes |
|  License | AGPL v3 | AGPL v3 + SLA |
|  Pricing | Free | [Paid](https://bi.technoplatz.de/start) |

## About

Official Web Site
[https://bi.technoplatz.com](https://bi.technoplatz.com)

## Author

Mustafa Mat [@mustafamat](https://www.github.com/mustafamat)
Founder, Technoplatz IT Solutions GmbH
Senior System Analist, Developer
Data Sciences & Statistics B. Sc.

--
