# DaDashbar

collected trello scrapings

## dev setup

1. Make sure you have python3, `pip`, and `pyenv`
2. init your python virtual environment
  ```bash
  virtualenv -p python3.10 env
  source ./env/bin/activate
  pip install -r requirements.txt
  ```
3. export your trello API keys (from [trello.com/app-key](https://trello.com/app-key))
  
  ```bash
  export TRELLO_API_KEY="..."
  export TRELLO_API_SECRET="..."
  export TRELLO_TOKEN="..."
  ```

## run

Start the server

```bash
python app.py
```

then take a pull from flask at [localhost:8080](http://localhost:8080)
