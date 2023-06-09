# Technoplatz BI

Table of contents;

- [Platform](#platform)
- [How to get started](#how-to-get-started)
- [Installation](#installation)
- [Impressum](#impressum)
- [Author](#author)

## Platform

Technoplatz BI community edition is an open source, multi-container, JSON-driven no-code data application and data sharing platform designed to empower business professionals build their own unique solution. It offers a pragmatic and optimised way to meet the key requirements of critical business processes by considering that each company has its own unique conditions;

- Data Application
- BI-Directional Data Sharing
- API

The further information can be found at the [official web site](https://bi.technoplatz.com).

## How to get started

### The importance of the containerization

Technoplatz BI community edition works on [Docker](#https://www.docker.com/) platform which is the leading virtualisation technology for developing, shipping and running business grade applications. Before getting started with the installation steps, the first phase you need to complete is creating a standalone Docker instance on the Cloud. We recommend Debian or Debian-based Ubuntu as the main Operating Systems for the Cloud instances required.

#### Why you should choose Debian Platform

Debian is a complete, solid-rock and free Operating System. The word "free" means here doesn't refer to money, instead, it refers to software freedom. In the IT world there are a lot of reasons to choose Debian or Ubuntu as a user, as a developer and even in enterprise environments. Most Debian users appreciate the stability and the smooth upgrade processes of both packages and the entire distribution. Debian is also widely used by software and hardware developers because it runs on numerous architectures and devices. If you plan to use them in a professional environment there are additional benefits like LTS versions and cloud images.

## Creating an Instance on the Cloud

Pick your preferred cloud provider and follow the instructions in the links below:\
[Microsoft Azure](#https://azure.microsoft.com/en-us/services/kubernetes-service/docker) | ‍[Google Cloud](#https://cloud.google.com/marketplace/docs/container-images) | ‍[Amazon WS](#https://aws.amazon.com/marketplace/pp/prodview-2jrv4ti3v2r3e?sr=0-1&ref_=beagle&applicationId=AWSMPContessa) | ‍[DigitalOcean](#https://marketplace.digitalocean.com/apps/docker)
‍

## Installation

### The first touches on the Instance

Many cloud instances provided in the marketplaces may not be up-to-date in terms of the latest version of the operating system or some initial resources. That's why, as soon as the instance is created it is strongly recommended the following steps should be taken before getting started with Docker.

#### Initial Update

Start an SSH session on the instance, perform an initial update then reboot the instance immediately.

```bash
ssh username@ip-address-of-the-instance
```

```bash
sudo apt-get update && sudo apt-get upgrade -y && sudo reboot
```

#### Setting the Timezone

Check the current date and time zone, list available zones to select the right one. Please consider the country which most BI users get connected from and where the preferred data center is located at.

```bash
timedatectl
```

```bash
timedatectl list-timezones
```

```bash
timedatectl set-timezone Europe/Berlin
```

### Install Docker Engine

Install required packages to allow apt to use a repository securely.

```bash
sudo apt-get install ca-certificates curl gnupg
```

Install the official Docker gpg key.

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | \
sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

Set up the Docker repository.

```bash
echo "deb [arch="$(dpkg --print-architecture)" \
signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Update the apt package index again.

```bash
sudo apt-get update
```

Start the installation of the latest version of Docker.

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io \
docker-buildx-plugin docker-compose-plugin
```

Verify that the installation is successful by running the following hello-world image. The command below downloads a test image, runs it in a container, prints a confirmation message and exits.

```bash
sudo docker run hello-world
```

### Unistall Docker Engine

Uninstall the Docker Engine, command line interfaces, container service and Docker Compose packages.

```bash
sudo apt-get purge docker-ce docker-ce-cli containerd.io \
docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
```

Images, containers, volumes or custom configuration files on your host aren’t automatically removed. To delete them all;

```bash
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
```

You have to delete any edited configuration files manually.

<sup>To get help about error handling you can follow the instructions on the [official web page](#https://docs.docker.com/engine/install/debian/).</sup>

## Impressum

Angaben gemäß § 5 TMG\
Technoplatz IT Solutions GmbH\
Berliner Allee 59 40212 Düsseldorf Deutschland

### Handelsregister

HRB 83371\
Registergericht: Amtsgericht Düsseldorf

### Vertreten durch die Geschäftsführer

Mustafa Mat

### Umsatzsteuer-ID

Umsatzsteuer-Identifikationsnummer gemäß §27 a Umsatzsteuergesetz:\
DE318821373

### Kontakt

E-Mail: support@technoplatz.de\
Web: [https://www.technoplatz.de/contact](https://www.technoplatz.de/contact)

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

## Author

Mustafa Mat\
<sup>Geschäftsführer, MD</sup>\
Senior Analist Developer\
Data Sciences, Statistics B.Sc.\
[@mustafamat](https://www.github.com/mustafamat)

--
