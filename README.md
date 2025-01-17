I. Strategia

Projekt został napisany w Pythonie 2.7. Program implementuje prostą strategię arbitrażu, tak jak w  opisie zadania:

1. Znajdujemy pierwsze dwa rynki których międzyrynkowy spread przeracza założony wcześniej, stały
próg.
2. Jednocześnie otwieramy krótką i długą pozycję na odpowiednich rynkach.
3. Czekamy na odpowiednią okazję do zamknięcia (tzn. kiedy kursy odpowiednio zbliżą się do siebie)
4. Jeśli kursy przekroczyły próg zamknięcia, bądź minął określony czas od momentu otwarcia pozycji, zamykamy wcześniej otwarte pozycje.
5. Czekamy na następne okazje.

Przy transakcjach kapitał dzielony jest po równo na tylko dwa rynki. Bardziej szczegółową implementację można odczytać z komentarzy zawartych w kodzie źródłowym. 

II. Pliki

1. Plik "exploration.ipynb" to jupyterowy notebook zawierający podstawowe sprawdzanie danych.
2. Plik "main.ipynb" zawiera funkcję implementujące założoną strategię arbitrażu korzystającą ze wszystkich dostępnych danych.
3. Plik "test.py" umożliwia uruchomienie zaimplementowanej strategii na dostępnych danych.

III. Test

Aby uruchomić plik testowy należy:
1. Otworzyć plik "test.py" w edytorze.
2. W linii 220 wprowadzić pożądane wartości parametróœ.
3. Uruchomić plik korzystając z interpretera Pythona lub wpisać w terminalu: 
python "sciezka_do_repozytorium/test.py"



