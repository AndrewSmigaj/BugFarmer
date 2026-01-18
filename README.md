# BugFarmer

## Development Setup

### Prerequisites
- Docker and Docker Compose

### Running the Server

Start all services:
```bash
docker compose up -d
```

### After Changing Go Code

The Go backend is compiled by a separate `builder` container. After modifying any Go files in `nakama/modules/`, you must rebuild:

```bash
docker compose build builder && docker compose down && docker compose up -d
```

### Useful Commands

```bash
# View server logs
docker compose logs nakama --tail 50

# View logs and follow
docker compose logs -f nakama

# Check for errors
docker compose logs nakama | grep -i error

# Stop everything
docker compose down

# Full restart with rebuild
docker compose build builder && docker compose down && docker compose up -d

# Delete stored world data (from Nakama console storage)
curl -X DELETE "http://localhost:7351/v2/console/storage/worlds/<world-id>/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"
```

### Ports
- 7350: Nakama HTTP API
- 7351: Nakama Console (admin:password)
- 5432: PostgreSQL