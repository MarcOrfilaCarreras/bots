# Bots

A collection of bots designed to fetch, process, and distribute data from external APIs into messaging platforms and other services.

---

## Getting Started

This project includes a `Dockerfile` and a `docker-compose.yml` to run the application in a container.

- Build and start in the background
  ```bash
  docker-compose up -d --build
  ```

- Stop and remove containers
  ```bash
  docker compose down
  ```

> Notes: `db.json` and `logs/` are mounted into the container so data and logs persist on the host.

## Contributing

Contributions are welcome! To set up your development environment:

1. Clone the repository and enter the folder:
   ```bash
   git clone https://github.com/MarcOrfilaCarreras/bots.git
   cd bots
   ```
2. Create a virtual environment and install Python dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the app locally:
   ```bash
   python run.py
   ```

## License

See the [LICENSE.md](LICENSE.md) file for details.
