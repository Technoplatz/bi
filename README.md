### Technoplatz BI Community Edition
*It's time to get data-driven with your inner-cycle!*

- [What is Technoplatz BI](#what-is-technoplatz-bi)
- [How to install](#how-to-install)
- [About](#about)

## What is Technoplatz BI
Technoplatz BI is a low-code data application and sharing solution that empowers those who manage data-driven business processes.

#### Highlights;

- Data Application\
Basic data operations and end-to-end process management on a self-service platform that supports flexible data structure.

- BI-directional data sharing\
Secure data sharing with business partners via live data connections and messaging.

- Visualization\
Basic statistics and real-time visualization on business data without the need to be a data expert.

- Integration\
Get responses to your data requests via your own API instead of Spreadsheets.

## How to install
Thanks to its multi-container structure built on Docker, the system can be run on all cloud service providers, embedded servers and even personal computers.

#### STEP 1
You can install Docker on your computer for free or choose a paid ready-to-use Docker platform from one of the leading cloud service providers. You can find the necessary instruction for cloud or on-premise installation in the links below;

- [Microsoft Azure](https://azure.microsoft.com/en-us/services/kubernetes-service/docker/), [Google Cloud](https://cloud.google.com/marketplace/docs/container-images), [AWS](https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa), [DigitalOcean](https://marketplace.digitalocean.com/apps/docker)
- [Windows](https://docs.docker.com/desktop/install/windows-install), [Linux](https://docs.docker.com/desktop/install/linux-install), [Mac OS](https://docs.docker.com/desktop/install/mac-install)

#### STEP 2
Clone the repository from GitHub.

```bash
git clone https://github.com/technoplatz/bi.git
```

After running this command, a folder named `bi` is going to be created in the directory you are already in. Please change your directory into this folder before following the next steps.

```bash
cd bi
```

#### STEP 3
Edit `.env` file and change the user parameters to the actual values.

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

<sub>**TZ:** Time zone of your platform's location must be entered in accordance to the official TZ format (eg. America/New_York). https://en.wikipedia.org/wiki/List_of_tz_database_time_zones is the link for more info about TZ.\
**DOMAIN:** Leave it as "localhost" for local access or testing use.\
**USER_EMAIL:** Company e-mail address of Administrator user.\
**USER_NAME:** First and last names of Administartor user (eg. John Doe).\
**COMPANY_NAME:** Enter legal name of your organization.\
**FROM_EMAIL:** Sender e-mail address of all automatic e-mails.\
**FROM_NAME:** A name or nickname that appears next to the sender e-mail address.\
**SENDGRID_API_KEY:** An API key used for sending automated emails over Sendgrid. Please find the detailed information about how to obtain an API key for Technoplatz BI. https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key</sub>


#### STEP 4
Set the containers up and running;

```bash
docker-compose up --build --detach --remove-orphans
```

## About

Official Web Site\
[https://bi.technoplatz.com](https://bi.technoplatz.com)

#### Author
Mustafa Mat [@mustafamat](https://www.github.com/mustafamat)\
Founder, Technoplatz IT Solutions GmbH\
<sub>Senior System Analist Developer\
Data Sciences, Statistics B.Sc.</sub>