# Fund Referential System

A system for managing and visualizing fund hierarchies, relationships, and associated data.

## Architecture

- **Backend**: FastAPI + Neo4j
- **Frontend**: React + D3.js
- **Deployment**: Docker & Docker Compose

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── data_ingestion.py    # Data ingestion script
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/                 # React application source
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile
└── docker-compose.yml       # Docker Compose configuration
```

## Setup & Running

1. Clone the repository
2. Place your CSV data files in the `backend/data` directory:

   - management_entities.csv
   - master_funds.csv
   - subfunds.csv
   - legal_entities.csv
   - share_classes.csv

3. Start the services using Docker Compose:

```bash
docker-compose up --build
```

The services will be available at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Neo4j Browser: http://localhost:7474

## API Endpoints

- `GET /funds/{fund_id}` - Get fund details
- `GET /funds/{fund_id}/hierarchy` - Get fund hierarchy (children or parents)
- `GET /funds/management/{mgmt_id}` - Get funds by management entity

## Features

1. Data Storage & Management

   - Graph database for efficient relationship querying
   - Support for all fund types and relationships
   - Extensible data model

2. Visualization

   - Interactive fund hierarchy visualization
   - Zoom and pan capabilities
   - Node and edge highlighting

3. API
   - RESTful endpoints for data retrieval
   - Low-latency responses
   - Paginated results

## Development

### Backend (Local)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (Local)

```bash
cd frontend
npm install
npm start
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

[MIT License](LICENSE)
