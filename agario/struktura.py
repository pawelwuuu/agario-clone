import os

def wypisz_strukture(folder, wciecie="", plik=None):
    for element in sorted(os.listdir(folder)):
        sciezka = os.path.join(folder, element)
        if os.path.isdir(sciezka):
            plik.write(wciecie + "📁 " + element + "\n")
            wypisz_strukture(sciezka, wciecie + "    ", plik)
        else:
            plik.write(wciecie + "📄 " + element + "\n")

# Ścieżka do pliku wyjściowego
output_path = "struktura.txt"

with open(output_path, "w", encoding="utf-8") as f:
    f.write("Struktura folderów i plików:\n")
    wypisz_strukture(os.getcwd(), plik=f)

print(f"Struktura zapisana do: {output_path}")
