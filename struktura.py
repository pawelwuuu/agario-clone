import os

def wypisz_strukture(folder, wciecie=""):
    for element in sorted(os.listdir(folder)):
        sciezka = os.path.join(folder, element)
        if os.path.isdir(sciezka):
            print(wciecie + "📁 " + element)
            wypisz_strukture(sciezka, wciecie + "    ")
        else:
            print(wciecie + "📄 " + element)

# Uruchom od bieżącego folderu
print("Struktura folderów i plików:")
wypisz_strukture(os.getcwd())
