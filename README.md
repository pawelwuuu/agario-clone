# Klon Agar.io w Pythonie

## Tech Stack

Projekt w całości napisany w Pythonie, wykorzystujący:

- **Python 3.8+**: podstawowy język i środowisko wykonawcze.
- **asyncio**: asynchroniczna pętla zdarzeń i korutyny, zapewniające wydajną obsługę wielu graczy.
- **websockets**: komunikacja w czasie rzeczywistym przez protokół WebSocket.
- **pygame**: renderowanie grafiki, obsługa wejścia użytkownika i pętla gry.

## Struktura projektu

```
agario_clone/
├── README.md            # Ten plik
├── requirements.txt     # Lista zależności (websockets, pygame)
├── config.py            # Konfiguracja gry (port, rozmiar okna, FPS)
├── common/              # Wspólne moduły klient–serwer
│   ├── messages.py      # Format i typy komunikatów JSON (JOIN, MOVE, UPDATE)
│   └── utils.py         # Funkcje pomocnicze (np. kolizje, konwersje współrzędnych)
│
├── server/              # Kod serwera WebSocket
│   ├── server.py        # Uruchomienie serwera i obsługa połączeń
│   ├── game_state.py    # Klasa GameState: zarządza stanem gry (pozycje, kolizje)
│   └── handlers.py      # Handlery websocket (JOIN, MOVE, broadcast UPDATE)
│
├── client/              # Kod klienta Pygame — separacja logiki
│   ├── client.py        # Punkt wejścia: pętla Pygame i obsługa inputu
│   ├── network.py       # Moduł network: wsparcie WebSocket (JOIN, MOVE, UPDATE)
│   └── renderer.py      # Moduł renderer: funkcja rysująca stan gry w Pygame
│
└── assets/              # Zasoby (czcionki, obrazy)
    ├── fonts/
    │   └── arcade.ttf
    └── images/
        └── logo.png
```

### Podział modułów klienta

- **client.py**: uruchamia wątek sieciowy (`network.start_network_thread()`), obsługuje pętlę Pygame, przetwarza input (WSAD) i aktualizuje `local_pos`.
- **network.py**: odpowiada za komunikację z serwerem:

  1. Łączy się przez WebSocket (`JOIN`).
  2. Wysyła cyklicznie (`1/FPS`) aktualną pozycję (`MOVE`).
  3. Odbiera stany gry (`UPDATE`) i zapisuje je w `shared_state`.

- **renderer.py**: funkcja `render(screen, shared_state)`, która rysuje wszystkie kulki na podstawie danych z `shared_state`.

_(Dzięki takiej architekturze łatwo testować i rozbudowywać każdy element niezależnie.)_

---

## Wymagania

- Python 3.8 lub nowszy
- Pakiety z `requirements.txt`:

  ```text
  websockets>=10.0
  pygame>=2.0
  ```

## Instalacja

1. Sklonuj repozytorium:

   ```bash
   git clone https://github.com/użytkownik/agario_clone.git
   cd agario_clone
   ```

2. Zainstaluj zależności:

   ```bash
   pip install -r requirements.txt
   ```

## Konfiguracja

W `config.py` dostosuj:

```python
PORT = 8765        # Port serwera
WIDTH = 800        # Szerokość okna gry
HEIGHT = 600       # Wysokość okna gry
FPS = 60           # Klient FPS
```

## Uruchomienie

### Serwer

```bash
python -m server.server
```

### Klient

```bash
python -m client.client
```

## Protokół wiadomości

Komunikaty JSON definiowane w `common/messages.py`:

- `join` – dołączenie gracza
- `move` – przesłanie pozycji i rozmiaru
- `update` – serwer przesyła stan wszystkich graczy

## Jak grać

1. Uruchom serwer.
2. Otwórz jeden lub więcej klientów.
3. Poruszaj się klawiszami **W**, **S**, **A**, **D**.
4. Zobacz, jak Twoja kulka jest kontrolowana przez serwer.

## Rozszerzenia

- Automatyczna logika zjadania (kolizje) w `GameState`.
- Power-upy, ranking i dodatkowe tryby gry.
