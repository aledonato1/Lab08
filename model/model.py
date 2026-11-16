from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):

        risultato = []

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            somma = 0.0
            conteggio = 0

            for p in prezzi:
                if p.data.month == mese:
                    somma += p.prezzo_litro
                    conteggio += 1

            if conteggio > 0:
                media = somma / conteggio
                risultato.append((distributore.nome, media))
            else:
                risultato.append((distributore.nome, 0.0))

        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente

                nuova_sequenza = []
                for s in sequenza_parziale:
                    nuova_sequenza.append(s)
                self.__sequenza_ottima = nuova_sequenza
            return


        for distributore in self._distributori:
            id_dist = distributore.id

            prezzo_al_litro = prezzi_settimana[id_dist][giorno - 1]
            costo_carburante = prezzo_al_litro * 100

            costo_spostamento = 0
            if ultimo_distributore is not None:
                if ultimo_distributore != id_dist:
                    costo_spostamento = 5

            costo_totale_step = costo_carburante + costo_spostamento

            if self.__costo_ottimo != -1 and (costo_corrente + costo_totale_step) >= self.__costo_ottimo:
                continue

            sequenza_parziale.append(id_dist)

            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                id_dist,
                costo_corrente + costo_totale_step,
                prezzi_settimana
            )

            sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        prezzi_dizionario = {}

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()

            prezzi_settimana = []
            for p in prezzi:
                if p.data.month == mese and p.data.day <= 7:
                    prezzi_settimana.append(p)

            prezzi_settimana.sort(key=lambda x: x.data.day)

            valori_prezzo = []
            for p in prezzi_settimana:
                valori_prezzo.append(p.prezzo_litro)

            prezzi_dizionario[distributore.id] = valori_prezzo

        return prezzi_dizionario
