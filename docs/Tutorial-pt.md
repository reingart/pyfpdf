# Tutorial #

Methods full documentation: [`fpdf.FPDF` API doc](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF)

[TOC]

## Tuto 1 - Exemplo Mínimo ##

Vamos começar com um exemplo clássico:

```python
{% include "../tutorial/tuto1.py" %}
```

[PDF resultante](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto1.pdf)

Após incluirmos o ficheiro da biblioteca, criamos um objeto `FPDF`. O
[FPDF](fpdf/fpdf.html#fpdf.fpdf.FPDF) construtor é construído com os seguintes parâmetros por omissão: 
Páginas são em formato A4 vertical e a unidade de medida é o milímetro.
Pode ser especificado explicitamente através de:

```python
pdf = FPDF(orientation="P", unit="mm", format="A4")
```

É possível colocar o PDF em modo horizontal (`L`) ou em outros formatos de página
(como `Letter` e `Legal`) e em outras unidades de medida (`pt`, `cm`, `in`).

Neste momento, não há nenhuma página, então temos que adicionar uma com
[add_page](fpdf/fpdf.html#fpdf.fpdf.FPDF.add_page). A origem está no canto superior esquerdo e a posição atual é, por padrão, colocada a 1 cm das bordas; as margens podem ser alteradas com [set_margins](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_margins).

Antes de imprimirmos o texto, é obrigatório selecionar uma fonte com
[set_font](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_font), caso contrário, o documento será inválido.
Nós escolhemos Helvetica bold 16:

```python
pdf.set_font('helvetica', 'B', 16)
```
Podemos formatar em itálico com `I`, sublinhar com` U` ou uma fonte normal
com uma string vazia (ou qualquer combinação). Observe que o tamanho da fonte é fornecido em pontos, não milímetros (ou outra unidade do utilizador); esta é a única exceção.
As outras fontes integradas são `Times`,` Courier`, `Symbol` e` ZapfDingbats`.

Agora podemos imprimir uma célula com [cell](fpdf/fpdf.html#fpdf.fpdf.FPDF.cell). Uma célula é uma área retangular, possivelmente emoldurada, que contém algum texto. É renderizado na posição atual. Nós especificamos as suas dimensões, o seu texto (centrado ou alinhado), se as bordas devem ser desenhadas, e para onde a posição atual se deve mover depois desta alteração (para a direita, abaixo ou no início da próxima linha). Para adicionar uma moldura, temos de fazer o seguinte:

```python
pdf.cell(40, 10, 'Hello World!', 1)
```

Para adicionar uma nova célula ao lado desta, com texto centralizado e ir para a próxima linha, teríamos de fazer:

```python
pdf.cell(60, 10, 'Powered by FPDF.', new_x="LMARGIN", new_y="NEXT", align='C')
```

**Nota**: a quebra de linha também pode ser feita com [ln](fpdf/fpdf.html#fpdf.fpdf.FPDF.ln). Esse método permite especificar, adicionalmente, a altura da quebra.

Finalmente, o documento é fechado e guardado no caminho do arquivo fornecido utilizando
[output](fpdf/fpdf.html#fpdf.fpdf.FPDF.output). Sem termos qualquer parâmetro fornecido, `output ()` retorna o buffer PDF `bytearray`.

## Tuto 2 - Cabeçalho, rodapé, quebra de página e imagem##

Aqui temos um exemplo de duas páginas com cabeçalho, rodapé e logótipo:

```python
{% include "../tutorial/tuto2.py" %}
```

[PDF resultante](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto2.pdf)

Este exemplo usa os [header](fpdf/fpdf.html#fpdf.fpdf.FPDF.header) e o [footer](fpdf/fpdf.html#fpdf.fpdf.FPDF.footer) para processar cabeçalhos e rodapés de página. Estes são chamados automaticamente. Eles já existem na classe FPDF, mas não fazem nada, portanto, temos que os estender a classe e substituí-los.

O logótipo é impresso utilizando o método [image](fpdf/fpdf.html#fpdf.fpdf.FPDF.image), especificando o seu canto superior esquerdo e sua largura. A altura é calculada automaticamente para respeitar as proporções da imagem.

Para imprimir o número da página, um valor nulo é passado como a largura da célula. Isso significa que a célula deve se estender até a margem direita da página; é útil para centralizar texto. O número da página atual é retornado pelo método [page_no](fpdf/fpdf.html#fpdf.fpdf.FPDF.page_no); quanto ao número total de páginas, é obtido por meio do valor especial `{nb}` que será substituído quando se fecha o documento.
Observe que o uso do método [set_y](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_y) permite definir a posição em um local absoluto da página, começando do início ou do fim.

Outro recurso interessante que se usa aqui é a quebra de página automática. Desde do momento em que uma célula cruza o limite da página (a 2 centímetros da parte inferior por
padrão), uma pausa é executada e a fonte restaurada. Embora o cabeçalho e rodapés selecionam a sua própria fonte (`helvetica`), o corpo continua com` Times`.
Este mecanismo de restauração automática também se aplica a cores e largura de linha.
O limite que dispara quebras de página pode ser definido com
[set_auto_page_break](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_auto_page_break).

## Tuto 3 - Quebras de linha e cores ##

Vamos continuar com um exemplo que imprime parágrafos justificados e o uso de cores.

```python
{% include "../tutorial/tuto3.py" %}
```

[PDF resultante](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto3.pdf)

[Texto de Júlio Verne](https://github.com/py-pdf/fpdf2/raw/master/tutorial/20k_c1.txt)

O método [get_string_width](fpdf/fpdf.html#fpdf.fpdf.FPDF.get_string_width) permite determinar o comprimento de uma string na fonte atual, e que é usada aqui para calcular a posição e a largura do quadro ao redor do título. Em seguida, as cores são definidas (via [set_draw_color](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_draw_color), [set_fill_color](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_fill_color) e [set_text_color](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_text_color)) e a espessura da linha é definida como 1 mm (contra 0,2 por padrão) com [set_line_width](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_line_width). Finalmente, produzimos a célula (se o último parâmetro for verdadeiro, indica que o plano de fundo deve ser preenchido).

O método usado para imprimir os parágrafos é [multi_cell](fpdf/fpdf.html#fpdf.fpdf.FPDF.multi_cell).
Cada vez que uma linha atinge a extremidade direita da célula ou um código de fim de linha é encontrado, uma quebra de linha é emitida e uma nova célula é criada automaticamente sob a atual. O texto é justificado por padrão.

Duas propriedades do documento são definidas: o título
([set_title](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_title)) e o autor
([set_author](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_author)). As propriedades podem ser visualizadas de duas maneiras:
A primeira é abrir o documento diretamente com o Acrobat Reader, vá para o menu Arquivo
e escolha a opção Propriedades do documento. 
O segundo, também disponível no plug-in, é clicar com o botão direito e selecionar Propriedades do documento.

## Tuto 4 - Multi Colunas ##

Este exemplo é uma variante do anterior, mostrando como colocar o texto em várias colunas.

```python
{% include "../tutorial/tuto4.py"%}
```

[PDF resultante](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto4.pdf)

[Texto de Júlio Verne](https://github.com/py-pdf/fpdf2/raw/master/tutorial/20k_c1.txt)

_⚠️ This section has changed a lot and requires a new translation: <https://github.com/py-pdf/fpdf2/issues/267>_

English versions:

* [Tuto 4 - Multi Columns](https://py-pdf.github.io/fpdf2/Tutorial.html#tuto-4-multi-columns)
* [Documentation on TextColumns](https://py-pdf.github.io/fpdf2/TextColumns.html


## Tuto 5 - Criar Tabelas ##

```python
{% include "../tutorial/tuto5.py"%}
```

[PDF resultante](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto5.pdf) -
[Texto dos países](https://github.com/py-pdf/fpdf2/raw/master/tutorial/countries.txt)

_⚠️ This section has changed a lot and requires a new translation: <https://github.com/py-pdf/fpdf2/issues/267>_

English versions:

* [Tuto 5 - Creating Tables](https://py-pdf.github.io/fpdf2/Tutorial.html#tuto-5-creating-tables)
* [Documentation on tables](https://py-pdf.github.io/fpdf2/Tables.html)

## Tuto 6 - Criar links e misturar estilos de texto ##

Este tutorial irá explicar várias maneiras de inserir links dentro de um documento PDF, bem como adicionar links para fontes externas.

Também mostrará várias maneiras de usar diferentes estilos de texto, (negrito, itálico, sublinhado) no mesmo texto.

```python
{% include "../tutorial/tuto6.py"%}
```

[PDF resultante](https://github.com/py-pdf/fpdf2/raw/master/tutorial/tuto6.pdf) -
[fpdf2-logo](https://raw.githubusercontent.com/py-pdf/fpdf2/master/docs/fpdf2-logo.png)



O novo método mostrado aqui para imprimir texto é [write()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.write). É muito parecido com [multi_cell ()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.multi_cell), sendo as principais diferenças:

- O fim da linha está na margem direita e a próxima linha começa na 
  margem esquerda.
- A posição atual move-se para o final do texto.

O método, portanto, nos permite escrever um pedaço de texto, alterar o estilo da fonte, e continuar do ponto exato em que paramos.
Por outro lado, a sua principal desvantagem é que não podemos justificar o texto como nós fazemos com o método [multi_cell()(https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.multi_cell) .

Na primeira página do exemplo, usámos [write()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.write)
para este propósito. O início da frase está escrita no estilo de texto normal, depois usando o  método [set_font()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.set_font), trocamos para sublinhado e acabámos a frase.

Para adicionar o link externo a apontar para a segunda página, nós usámos o método [add_link()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.add_link), que cria uma área clicável à qual demos o nome de “link” que direciona para outra parte do documento.

Para criar o link externo usando uma imagem, usámos [image()](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.image). O método tem a opção de passar um link como um dos seus argumentos. O link pode ser interno ou externo.

Como alternativa, outra opção para mudar o estilo da fonte e adicionar links é usar o método `write_html()`. É um “parser” que permite adicionar texto, mudar o estilo da fonte e adicionar links usando html.
