# Tutorial #

Documentazione completa dei metodi: [`fpdf.FPDF` API doc](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF)

[TOC]

## Tuto 1 - Esempio base ##

Iniziamo con un esempio comune:

```python
{% include "../tutorial/tuto1.py" %}
```

[Risultato PDF](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto1.pdf)

Dopo aver incluso la libreria, creiamo un oggetto `FPDF`. Così facendo il costruttore 
[FPDF](fpdf/fpdf.html#fpdf.fpdf.FPDF) viene utilizzato con i suoi valori di default: 
le pagine sono in A4 verticale e l'unità di misura è millimetri.
Avremmo potuto specificarle esplicitamente facendo:

```python
pdf = FPDF(orientation="P", unit="mm", format="A4")
```
È possibile impostare il PDF in modalità orizzontale (`L`) o utilizzare altri formati
(come `Letter` e `Legal`) e unità di misura (`pt`, `cm`, `in`).

Non esiste una pagina al momento, quindi dobbiamo aggiungerne una con
[add_page](fpdf/fpdf.html#fpdf.fpdf.FPDF.add_page). L'origine è in alto a sinistra e la posizione corrente è a 1cm dai bordi; i margini possono essere cambiati con [set_margins](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_margins).

Prima di poter stampare del testo, è obbligatorio selezionare un font con 
[set_font](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_font), altrimenti il documento risulterebbe non valido.
Scegliamo Helvetica bold 16:

```python
pdf.set_font('helvetica', 'B', 16)
```

Avremmo potuto scegliere il corsivo con `I`, sottolineato con `U` o un font regolare lasciando la stringa vuota (o ogni combinazione). Notare che la dimensione dei caratteri è specificata in punti, non millimetri (o altre unità di misura); questa è l'unica eccezione.
Gli altri font disponibili sono `Times`, `Courier`, `Symbol` and `ZapfDingbats`.

Adesso possiamo disegnare una cella con [cell](fpdf/fpdf.html#fpdf.fpdf.FPDF.cell). Una cella è un'area rettangolare, in caso con bordo, che contiene del testo. È disegnata nella attuale posizione. Specifichiamo le sue dimensioni, il suo testo (centrato o allineato), se i bordi devono essere mostrati, e dove verrà spostata la posizione quando avremo finito (a destra, sotto, o all'inizio della riga successiva). Faremmo così:

```python
pdf.cell(40, 10, 'Hello World!', 1)
```

Per aggiungere una nuova cella di fianco alla precedente con testo centrato e poi spostarci alla riga successiva, faremmo:

```python
pdf.cell(60, 10, 'Powered by FPDF.', new_x="LMARGIN", new_y="NEXT", align='C')
```

**NB**: si può andare a capo anche con [ln](fpdf/fpdf.html#fpdf.fpdf.FPDF.ln). Questo metodo permette di specificare l'altezza dello spazio.

In fine, il documento è chiuso e salvato nella destinazione fornita attraverso 
[output](fpdf/fpdf.html#fpdf.fpdf.FPDF.output). Senza alcun parametro, `output()`
ritorna il PDF in un buffer `bytearray`.

## Tuto 2 - Intestazione, piè di pagina, interruzione di pagina ed immagini ##

Ecco un esempio composto da due pagine con intestazione, piè di pagina e logo:

```python
{% include "../tutorial/tuto2.py" %}
```

[Risultato PDF](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto2.pdf)

Questo esempio sfrutta i metodi [header](fpdf/fpdf.html#fpdf.fpdf.FPDF.header) e 
[footer](fpdf/fpdf.html#fpdf.fpdf.FPDF.footer) per processare intestazioni e piè di pagina. Vengono chiamati automaticamente. Esistono nella classe FPDF ma non eseguono operazioni,
quindi è necessario estendere la classe e sovrascriverli.

Il logo è stampato con il metodo [image](fpdf/fpdf.html#fpdf.fpdf.FPDF.image) specificando la posizione del suo angolo in alto a sinistra e la sua larghezza. L'altezza è calcolata automaticamente per rispettare le proporzioni dell'immagine.

Per stampare il numero della pagina, un valore nullo può essere passato come larghezza della cella. Significa che la cella "crescerà" fino al margine destro della pagina; è utile per centrare il testo. Il numero di pagina è ritornato da [page_no](fpdf/fpdf.html#fpdf.fpdf.FPDF.page_no); mentre per il numero totale di pagine, si ottiene attraverso il valore speciale `{nb}`
che verrà sostituito quando le pagine saranno generate.
Importante menzionare il metodo [set_y](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_y) che permette di selezionare una posizione assoluta all'interno della pagina, incominciando dall'alto o dal basso.

Un'altra feature interessante: l'interruzione di pagina automatica. Non appena una cella dovesse superare il limite nella pagina (a 2 centimetri dal fondo di default), ci sarebbe un'interruzione e un reset del font. Nonostante l'intestazione e il piè di pagina scelgano il proprio font (`helvetica`), il contenuto continua in `Times`.
Questo meccanismo di reset automatico si applica anche ai colori e allo spessore della linea.
Il limite può essere scelto con [set_auto_page_break](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_auto_page_break).


## Tuto 3 - Interruzioni di riga e colori ##

Continuiamo con un esempio che stampa paragrafi giustificati. Mostreremo anche l'utilizzo dei colori.

```python
{% include "../tutorial/tuto3.py" %}
```

[Risultato PDF](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto3.pdf)

[Testo Jules Verne](https://github.com/py-pdf/fpdf2/raw/master/tutorial/20k_c1.txt)

Il metodo [get_string_width](fpdf/fpdf.html#fpdf.fpdf.FPDF.get_string_width) permette di determinare la lunghezza di una stringa nel font selezionato, e viene utilizzato per calcolare la posizione e la larghezza della cornice intorno al titolo. Successivamente selezioniamo i colori 
(utilizzando [set_draw_color](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_draw_color),
[set_fill_color](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_fill_color) e 
[set_text_color](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_text_color)) e aumentiamo la larghezza della linea a 1mm (invece dei 0.2 di default) con
[set_line_width](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_line_width). In fine, stampiamo la cella (l'ultimo parametro a true indica che lo sfondo dovrà essere riempito).

Il metodo utilizzato per stampare i paragrafi è [multi_cell](fpdf/fpdf.html#fpdf.fpdf.FPDF.multi_cell).
Ogni volta che una linea raggiunge l'estremità destra della cella o c'è un carattere carriage return, avremo un'interruzione di linea e una nuova cella verrà automaticamente creata. Il testo è giustificato di default.

Due proprietà del documento vengono definite: il titolo 
([set_title](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_title)) e l'autore  
([set_author](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_author)). Le proprietà possono essere controllate in due modi.
Il primo è aprire direttamente il documento con Acrobat Reader, cliccare sul menù File
e scegliere l'opzione Proprietà del documento. la seconda, è di cliccare con il tasto destro e scegliere Proprietà del documento.

## Tuto 4 - Colonne multiple ##

Questo esempio è una variante del precedente, mostra come disporre il test attraverso colonne multiple.

```python
{% include "../tutorial/tuto4.py" %}
```

[Risultato PDF](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto4.pdf)

[Testo Jules Verne](https://github.com/py-pdf/fpdf2/raw/master/tutorial/20k_c1.txt)

_⚠️ This section has changed a lot and requires a new translation: <https://github.com/py-pdf/fpdf2/issues/267>_

English versions:

* [Tuto 4 - Multi Columns](https://py-pdf.github.io/fpdf2/Tutorial.html#tuto-4-multi-columns)
* [Documentation on TextColumns](https://py-pdf.github.io/fpdf2/TextColumns.html


## Tuto 5 - Creare tabelle ##

```python
{% include "../tutorial/tuto5.py" %}
```

[Risultato PDF](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto5.pdf) -
[Testo delle nazioni](https://github.com/py-pdf/fpdf2/raw/master/tutorial/countries.txt)

_⚠️ This section has changed a lot and requires a new translation: <https://github.com/py-pdf/fpdf2/issues/267>_

English versions:

* [Tuto 5 - Creating Tables](https://py-pdf.github.io/fpdf2/Tutorial.html#tuto-5-creating-tables)
* [Documentation on tables](https://py-pdf.github.io/fpdf2/Tables.html)

## Tuto 6 - Creare link e mescolare stili di testo ##

Questo tutorial spiegherà molti modi di inserire link interni al pdf, e come inserirne a sorgenti esterne.

Saranno mostrati anche molti modi di utilizzare diversi stili di testo (grassetto, corsivo e sottolineato) nello stesso testo.

```python
{% include "../tutorial/tuto6.py" %}
```

[Risultato PDF](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto6.pdf) -
[fpdf2-logo](https://raw.githubusercontent.com/py-pdf/fpdf2/master/docs/fpdf2-logo.png)

Il nuovo metodo qui utilizzato per stampare testo è
 [write()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.write)
. È molto simile a 
 [multi_cell()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.multi_cell)
 , ma con delle differenze:

- La fine della linea è al margine destro e la linea successiva inizia al margine sinistro.
- La posizione attuale si sposta alla fine del testo stampato.

Il metodo quindi ci permette di scrivere un blocco di testo, cambiare lo stile del testo, e continuare a scrivere esattamente da dove eravamo rimasti. D'altro canto, il suo peggior svantaggio è che non possiamo giustificare il testo come con 
 [multi_cell()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.multi_cell)
 method.

Nella prima pagina dell'esempio, abbiamo usato
 [write()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.write)
 per questo scopo. L'inizio della frase è scritta in font normale, poi utilizzando
 [set_font()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.set_font)
 siamo passati al sottolineato e abbiamo finito la frase.

Per aggiungere un link interno che puntasse alla seconda pagina, abbiamo utilizzato 
 [add_link()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.add_link)
che crea un area cliccabile che abbiamo chiamato "link"  che redirige ad un altro punto del documento.

Per creare un link esterno utilizzando un'immagine, abbiamo usato
 [image()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.image)
. Il metodo ha l'opzione di passare un link come argomento. Il link può essere sia interno che esterno.

In alternativa, un'altra opzione per cambiare lo stile e aggiungere link è di utilizzare `write_html()`. È un parser hrml che permette di aggiungere testo, cambiare stile e aggiungere link utilizzando html.
