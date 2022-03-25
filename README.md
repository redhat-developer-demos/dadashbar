# da dashbar 📈

collected trello scrapings from my Dev Rel team

## Build

```bash
sudo podman build -t quay.io/rhdevelopers/dadashbar:latest .
```

## Config

Export your trello API keys (from [trello.com/app-key](https://trello.com/app-key))
  
```bash
export TRELLO_API_KEY="..."
export TRELLO_API_SECRET="..."
export TRELLO_TOKEN="..."
export ADMIN_USER="some@email.tld"
export ADMIN_PASS="..."
```

## Run

```bash
sudo podman run --rmi -p 8080:8080 -i -t quay.io/rhdevelopers/dadashbar:latest
```

## Development Setup

Init a python virtual environment and source your deps

```bash
python3 -m venv env
source ./env/bin/activate
python3 -m pip install -r requirements.txt
```

Boot the server

```bash
ADMIN_USER=test@email.tld ADMIN_PASS=test TRELLO_API_KEY=<some> TRELLO_API_SECRET=<some> TRELLO_TOKEN=<some> python3 app.py
```

Then, take a pull from flask at [localhost:8080](http://localhost:8080)
