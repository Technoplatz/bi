# Technoplatz BI

It's time to get data-driven with your [inner-cycle!](#highlights)

Technoplatz BI is a [low-code](#what-is-no-code), multi-container data application and data sharing platform designed to manage business processes without developing software from scratch. 

- [How to Get Started](#get-started)
- [Installation](#installation)
- [Maintenance](#maintenance)
- [Licensing Options](#license)
- [Impressum](#impressum)

## Highlights

It provides optimized and pragmatic solutions for the main requirements of many data-driven process by considering that each business has its own unique conditions;

- [Data Application](#data-application)
- [BI-Directional Data Sharing](#bi-directional-data-sharing)
- [Internal API](#api)

Technoplatz BI is being developed for those whose strategy is to make their business **data-driven**.

- **Cloud Platform on Solution Basis**\
It works for the companies want to build a new system to move their mission critical processes currently being managed on spreadsheets or legacy software to a sustainable, secure and cost-effective Cloud platform without investing in hardware infrastructure and software development services.

- **Sharing within an Inner-Cycle**\
It allows organizations to share data within the circle that surrounds customers, suppliers, business partners and internal departments. It can also be used as an "interface" by Enterprises that can not open their online global systems to local suppliers due to company policies.

- **No-code Platform Empowers Its Users**\
Technoplatz BI essentially designed for business users, not developers. Even though no coding skills required for the platform to use, users learn basics of JSON structure easily and naturally without having to study to become a data expert. This approach also creates a data culture within the company.

## What is No-code?

The widely accepted meaning of no-code term is an application development approach that does not require computer programming skills. No-code platforms use some visual interfaces to allow users to develop their own "App" without knowledge of any programming language. Unlike many no-code platforms, Technoplatz BI empowers users to create and publish their own "solution" run on their own platform.

| No-code Platforms | Technoplatz BI |
| :--- | :--- |
|  Designed for business users | Designed for business professionals |
|  For developing simple or medium Apps | For building solutions to be data-driven |
|  Very easy to use | Very beneficial to use |
|  Provide limited capabilities | Provide required capabilities |
|  Customized by built-in cosmetic components | Customized by JSON structures |

## Benefits

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

Docker platforms which are sold on marketplaces might be a couple of weeks or months behind of the latest system updates as of the date you purchase. It is highly recommended to make the operating system up-to-date immediately and reboot the platform afterwards.

```bash
apt update && apt upgrade -y
```

```bash
reboot
```

This step is not required for the Docker Desktop platform. What you need to do is to keep the application itself up-to-date.

### 2. Download and Install

To get the installation started please follow the messages on the console for the actions to be taken and the result of the process.

#### Linux and Mac OS

Open a [Linux Console](https://en.wikipedia.org/wiki/Linux_console) or [Mac OS Terminal](https://en.wikipedia.org/wiki/Terminal_(macOS)) session, copy paste and run the command below to create the system directory and download the required files from the official GitHub repository.

```bash
curl -Lso technoplatz/bi.sh --create-dirs \
"https://raw.githubusercontent.com/Technoplatz/bi/main/bi-sh" \
&& chmod +x technoplatz/bi.sh \
&& cd technoplatz
```

Run the service script with installation option.

```bash
./bi.sh install
```

#### Windows

In order for the Platform to run on Windows, the Docker Desktop and the WSL2 infrastructure (Windows Subsystem for Linux) must be installed. Please follow [this article](https://docs.docker.com/desktop/install/windows-install/) contains detailed instructions about how to install and run Docker Desktop by getting integrated with the WSL2. After the installation is complete, [Linux commands](#linux-and-mac-os) given above can be run on the WSL2 infrastructure in the same way.

### 3. Setting Parameters

Edit `.env` file, replace the sample values with your own and save the file.

```bash
...
TZ=#time-zone
DOMAIN=#localhost-or-ip-address-of-the-platform
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

- Domain must be `localhost` or IP address for local use.
- Time zone must be entered according to the official format (eg. America/New_York)\
<https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>
- Community edition generates self signed TLS certificates with the company information to be provided above for the internal communication of the database cluster to be encrypted.
- It is recommended to use [Sendgrid](https://www.sendgrid.com) email services for SMTP server.

A sample configuration;

```bash
...
TZ=Europe/Berlin
DOMAIN=localhost
ADMIN_EMAIL=john@yourcompany.com
ADMIN_USER_NAME=John Doe
COMPANY_NAME=Acme Inc.
DEPARTMENT_NAME=Finance
COUNTRY_CODE=DE
STATE_NAME=Nordrhein-Westfalen
CITY_NAME=Düsseldorf
SMTP_PORT=465
SMTP_SERVER=smtp.sendgrid.net
SMTP_USERID=apikey
SMTP_PASSWORD=SG.****.****
FROM_EMAIL=bi@yourcompany.com
API_KEY=61c09da62f1f9ca9357796c9
...
```

### 4. Starting Containers

Enter the command below to start the containers by keeping them up and running in the background. It can take up to 20 seconds till after containers creation for Technoplatz BI to be fully functional. You can log out and exit the platform safely after the installation is complete. Technoplatz BI continues to run at the background and restarts automatically as the platform is rebooted.

```bash
./bi.sh start
```

### 5. Signing in

In order to open your first session go to the following address in your web browser, click the "Sign in" button, enter your email and password which you provided in the .env file.

```bash
http://localhost:8100
```

## Maintenance

Unlike the enterprise edition the community edition doesn't provide any official support about maintenance and troubleshooting issues. As long as the system resources are not exceeded you are not expected to encounter a serious problem however the actions to be taken for certain situations are explained in below topics.

| Platform Operation | Script Command |
| :--- | :--- |
| Installing the system from scratch | `./bi.sh install` |
| Starting the containers | `./bi.sh start` |
| Stopping the running containers | `./bi.sh stop` |
| Restarting the running containers | `./bi.sh restart` |
| Cleaning dangling system sources | `./bi.sh prune` |
| Receiving the latest updates | `./bi.sh update` |
| Tracking system logs | `./bi.sh logs [service]` |
| **Operating System** | **Command** |
| Updating packages and upgrading OS | `apt update && apt upgrade -y` |
| Reboot the platform | `reboot` |

## License

Technoplatz BI Community Edition is an open source platform available under the GNU Affero GPL-v3 license. The platform is also provided as a service for companies want to get prefessional support in terms of managed hosting, custom development and integration services.

| | Community Edition | SaaS Edition |
| :--- | :---: | :---: |
|  Hosting | Self Hosted | Managed Hosted |
|  Database | MongoDB 6 | MongoDB 6 |
|  Database Clustering | 3 internal nodes | 3 internal/regional nodes |
|  Two-Factor Authentication | ✔ | ✔ |
|  WebApp Firewall | ✘ | ✔ |
|  Technical Support | ✘ | ✔ |
|  Custom Development Services | ✘ | ✔ |
|  Custom Domain | ✘ | ✔ |
|  License | GNU AGPL v3 | GNU AGPL v3 + SLA |
|  Pricing | Free | [Contact Us](https://bi.technoplatz.de/start) |

## Impressum

Angaben gemäß § 5 TMG\
Technoplatz IT Solutions GmbH\
Berliner Allee 59 40212 Düsseldorf Deutschland

### Handelsregister

HRB 8337\
Registergericht: Amtsgericht Düsseldorf

### Vertreten durch die Geschäftsführer

Mustafa Mat [@mustafamat](https://www.github.com/mustafamat)\
Senior System Analist, Developer\
Data Sciences & Statistics B. Sc.

### Umsatzsteuer-ID

Umsatzsteuer-Identifikationsnummer gemäß §27 a Umsatzsteuergesetz:\
DE318821373

### Kontakt

E-Mail: support@technoplatz.de\
Web: [https://bi.technoplatz.com/contact](https://bi.technoplatz.com)

Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV\
Technoplatz IT Solutions GmbH

### EU-Streitschlichtung

Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <https://ec.europa.eu/consumers/odr>.

Unsere E-Mail-Adresse finden Sie oben im [Abschnitt Kontakt](#kontakt).\
Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.

### Haftung für Inhalte

Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.

Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.

### Haftung für Links

Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar.

Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.

### Urheberrecht

Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind nur für den privaten, nicht kommerziellen Gebrauch gestattet.

Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die Urheberrechte Dritter beachtet. Insbesondere werden Inhalte Dritter als solche gekennzeichnet. Sollten Sie trotzdem auf eine Urheberrechtsverletzung aufmerksam werden, bitten wir um einen entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Inhalte umgehend entfernen.

--