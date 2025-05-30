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
│   ├── messages.py      # Format i typy komunikatów JSON
│   └── utils.py         # Funkcje pomocnicze (kolizje, konwersje współrzędnych)
│
├── server/              # Kod serwera WebSocket
│   ├── server.py        # Punkt wejścia serwera
│   ├── game_state.py    # Logika gry i stan świata
│   └── handlers.py      # Handlery websocket (connect, message)
│
├── client/              # Kod klienta Pygame
│   ├── client.py        # Punkt wejścia klienta i główna pętla
│   ├── network.py       # Komunikacja z serwerem przez WebSocket
│   └── renderer.py      # Renderowanie stanu gry w Pygame
│
└── assets/              # Zasoby (czcionki, obrazy)
    ├── fonts/
    │   └── arcade.ttf
    └── images/
        └── logo.png
```

_(Poniższe sekcje opisują dalsze kroki instalacji, uruchomienia i rozbudowy projektu.)_

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

2. Utwórz i aktywuj wirtualne środowisko:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Zainstaluj zależności:

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
python server/server.py
```

### Klient

```bash
python client/client.py
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
4. Jedz mniejsze kulki, unikaj większych!

## Rozszerzenia

- Autoryzacja i nazwy graczy
- Power-upy (przyspieszenie, niewidzialność)
- Różne mapy i tryby gry
- Ranking high-score na serwerze
