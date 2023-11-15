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

Technoplatz BI works on [Docker](#https://www.docker.com) platform which is the leading virtualisation technology for developing, shipping and running business grade applications. Creating a Docker instance on the Cloud is the first step prior to getting started with the installation. We recommend [Debian](#https://www.debian.org) or Debian-based Linux as the main Operating System for the required Cloud instance.

**Debian Linux**

Debian is a complete, solid-rock and free Linux Operating System. The word "free" means here doesn't refer to money, instead, it refers to software freedom. In the IT world, there are a lot of reasons to choose Debian or Ubuntu as a user, as a developer and even in enterprise environments. Most Debian users appreciate the stability and the smooth upgrade processes of both packages and the entire distribution. Debian is also widely used by software and hardware developers because it runs on numerous architectures and devices. If you plan to use them in a professional environment there are additional benefits like LTS versions and cloud images.

### Creating an Instance on the Cloud

Pick your preferred cloud provider and follow the instructions in the links below to learn how to create a new Debian instance:

- [Microsoft Azure](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/cloud-infrastructure-services.debian-11?tab=overview)
- [Google Cloud Platform](https://console.cloud.google.com/marketplace/product/debian-cloud/debian-bullseye)
- [Amazon Web Services](https://aws.amazon.com/marketplace/pp/prodview-l5gv52ndg5q6i)
- [DigitalOcean](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-debian-11)

### The first touches to the Instance

Many Debian instances provided in the marketplaces may not be up-to-date in terms of the latest version of the operating system or some initial resources. As soon as the instance is created it is highly recommended that the following steps should be taken immediately;

#### Performing an initial update

Upgrade the packages that already installed and reboot the instance. Reconnect to the instance after rebooting is completed.

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

```bash
sudo reboot
```

#### Setting the Time zone

Check the current date and time zone;

```bash
timedatectl
```

List available time zones to find your location;

```bash
timedatectl list-timezones
```

Set the time zone. Please note that the selected location should be the country where internal users get connected or the preferred data center is located at;

```bash
timedatectl set-timezone Europe/Berlin
```

#### Installing Docker Engine

Install required packages to allow apt to use the offical repository securely;

```bash
sudo apt-get install ca-certificates curl gnupg
```

Install the official Docker gpg key;

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | \
sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

Set up the Docker repository;

```bash
echo "deb [arch="$(dpkg --print-architecture)" \
signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Update the apt package index again and start the installation of the latest version of Docker platform.

```bash
sudo apt-get update \
&& sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
docker-buildx-plugin docker-compose-plugin
```

Verify that the installation completed successfully by running the following hello-world image. The command below downloads a test image, runs it in a container, prints a confirmation message and exits.

```bash
sudo docker run hello-world
```

#### Unistalling Docker Engine

The below command uninstalls Docker Engine, command line interfaces, container service and Docker Compose packages.

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

## Installation

Run the following command to get the platform script from the official repository and start containers by keeping them up and running in the background. Technoplatz BI restarts automatically when the platform is rebooted.

```bash
curl -Lso ~/technoplatz-bi/bi-sh --create-dirs \
"https://raw.githubusercontent.com/Technoplatz/bi/main/bi-sh" \
&& sudo chmod +x ~/technoplatz-bi/bi-sh \
&& cd ~/technoplatz-bi
```

```bash
./bi-sh start
```

## Schema Structure

```json
{
  "properties": {},
  "required": [],
  "index": [],
  "unique": [],
  "sort": {},
  "parents": [],
  "actions": [],
  "links": [],
  "triggers": [],
  "views": {},
  "fetchers": [],
  "import": {}
}
```

#### properties

Properties is the part of the Collection schema where data fields are defined. Multiple fields can be provided within a single JSON cluster. [Click](#properties) for details.

#### triggers

Triggers are secondary update processes that are automatically activated after entry, update or deletion processes in collections. It is used to update the same collection or a different target collection in case of any update in the specified data fields of a source collection. [Click](#triggers-1) for details.

### Properties

Standard fields of a property;

**bsonType**: Data type (string, number, date, bool)\
**title**: The form title of the data field.\
**description**: A short description of the data field.\
**placeholder**: Description that appears in the data entry box in forms.\
**default**: The default value to use when no value is given.\
**permanent**: Once entered, it cannot be changed (true|false).

#### String Properties

```json
{
  "ord_no": {
    "bsonType": "string",
    "title": "Order No",
    "description": "Customer order number",
    "placeholder": "Please enter an order number",
    "minWidth": 8,
    "maxWidth": 16,
    "pattern": "^[A-Za-z0-9-]{8,16}$",
    "default": null,
    "permanent": true
  }
}
```

Enumerates are certain type of string properties with predefined values which allow data entry via selectable options. They provide automatic validation and don't allow to enter any value rather than specified enums.

```json
{
  "shp_type": {
    "bsonType": "string",
    "title": "Ship Type",
    "description": "The default shipping type of the carrier",
    "placeholder": "The goods arrived at customs by",
    "minWidth": 3,
    "maxWidth": 4,
    "enum": ["Sea", "Air", "Truck"],
    "default": "Truck",
    "permanent": false
  }
}
```

#### Numeric Properties

```json
{
  "foo_serial": {
    "bsonType": "number | int | decimal | float",
    "title": "Amount",
    "description": "Order Amount",
    "placeholder": "Please enter the order amount in USD",
    "minimum": 1,
    "maximum": 999,
    "default": 1,
    "counter": false
  }
}
```

#### Boolean Properties

Sample boolean field;

```json
{
  "usr_enabled": {
    "bsonType": "bool",
    "title": "Enabled",
    "description": "User enabled or not",
    "default": false,
    "trueText": "Enabled",
    "falseText": "Disabled"
  }
}
```

### Actions

```json
[
  {
    "id": "change",
    "title": "DN Split",
    "enabled": true,
    "match": [{ "key": "dnn_status", "op": "in", "value": "40-ClearanceCompleted,50-OnTheTouchpoint" }],
    "set": [
      { "key": "dnn_acc_no", "value": null },
      { "key": "dnn_acc_name", "value": null },
      { "key": "dnn_qty", "value": null }
    ],
    "one_click": false,
    "icon": "git-branch",
    "uniqueness": true,
    "unique": ["dnn_no"],
    "split": true,
    "split_key_field": "dnn_no",
    "split_key_suffix": "-20",
    "split_num_field": "dnn_qty",
    "notification": {
      "notify": true,
      "subject": "Operations [Delivery Split]",
      "body": "Hi,<br /><br />We would like to let you know that the attached DN has been split.",
      "attachment": true,
      "fields": "dnn_no,dnn_line_no,dnn_status,dnn_acc_no,dnn_acc_name,dnn_prd_no,dnn_qty",
      "filter": [{ "key": "dnn_status", "op": "in", "value": "40-ClearanceCompleted,50-OnTheTouchpoint" }]
    },
    "_tags": ["#Managers", "#Administrators", "#Logistics", "#Operations"]
  }
]
```

### Links

```json
[
  {
    "collection": "delivery",
    "get": "dnn_no",
    "match": [{ "key": "dnn_status", "op": "eq", "value": "00-Open" }],
    "set": [
      { "key": "dnn_odi_no", "value": "odi_no" },
      { "key": "dnn_odi_sub_no", "value": "odi_sub_no" },
      { "key": "dnn_status", "value": "10-OnTheWay" }
    ],
    "autofill": true,
    "btntext": "Add DNs",
    "_tags": ["#Managers", "#Technoplatz", "#Operation"],
    "notification": {
      "notify": true,
      "subject": "Ordino Attached",
      "body": "Email body in HTML",
      "attachment": true,
      "fields": "dnn_no,dnn_line_no,dnn_odi_no,dnn_odi_sub_no,dnn_acc_no,dnn_acc_name"
    }
  }
]
```

### Triggers

```json
[
  {
    "name": "Amount updater",
    "enabled": true,
    "operations": ["update", "insert"],
    "changes": [
      { "key": "dnn_qty", "op": "gte", "value": 0 },
      { "key": "dnn_unit_price", "op": "gte", "value": 0 }
    ],
    "targets": [
      {
        "collection": "delivery",
        "match": [{ "key": "_id", "value": "_id", "prefixes": ["16K"] }],
        "filter": [{ "key": "dnn_status", "op": "ne", "value": "70-Delivered" }],
        "set": [{ "key": "dnn_amount", "value": "dnn_qty * dnn_unit_price" }],
        "upsert": false
      },
      {
        "collection": "manifest",
        "match": [{ "key": "man_no", "value": "dnn_man_no" }],
        "filter": [{ "key": "man_status", "op": "eq", "value": "10-OnCustomsProcess" }],
        "set": [{ "key": "man_amount", "value": "sum(dnn_amount)" }],
        "upsert": false
      }
    ]
  }
]
```

```json
[
  {
    "name": "Closed",
    "enabled": true,
    "operations": ["update"],
    "changes": [{ "key": "man_closed", "op": "eq", "value": true }],
    "targets": [
      {
        "collection": "delivery",
        "match": [{ "key": "dnn_man_no", "value": "man_no" }],
        "filter": [{ "key": "dnn_status", "op": "in", "value": "30-OnCustomsProcess,40-ClearanceCompleted" }],
        "set": [{ "key": "dnn_status", "value": "40-ClearanceCompleted" }],
        "upsert": false,
        "notification": {
          "notify": true,
          "subject": "Customs clearance completed",
          "body": "Hi,<br /><br />Manifest has been closed.",
          "collection": "delivery",
          "key": "man_no",
          "fields": "dnn_no,dnn_line_no,dnn_man_no",
          "filter": [{ "key": "dnn_man_no", "op": "eq", "value": "man_no" }],
          "attachment": true
        }
      }
    ]
  }
]
```

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
