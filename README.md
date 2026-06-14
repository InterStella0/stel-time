# stel-time

A Discord bot that lets users share and look up each other's local time.

## Self-hosting

### Requirements

- Docker + Docker Compose

### Setup

1. Clone the repo and copy the example env file:
   ```sh
   git clone https://github.com/InterStella0/stel-time
   cd stel-time
   cp .env.example .env
   ```

2. Edit `.env` and set your bot token:
   ```
   TOKEN=your_discord_bot_token
   ```

   - `TOKEN`: your bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
   - `DB_DIR`: where `data.db` is stored on the host (defaults to `./data`)

3. Start the bot:
   ```sh
   docker compose up -d
   ```

### Updates

```sh
git pull
docker compose up -d --build
```

### Logs

```sh
docker compose logs -f
```

### Stop

```sh
docker compose down
```
