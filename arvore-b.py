from sys import argv
from struct import pack, unpack, calcsize

NULO = -1
ORDEM = 4
TAM_CAB = 2

# *inventei que o id e o byte offset serão armazenados no formato 'i', logo:
# - id no formato 'i'
# - byte offset no formato 'i'
FORMATO_PAG = "h" + "ii"*(ORDEM-1) + "i"*ORDEM

TAM_PAG = calcsize(FORMATO_PAG)
#usar lista de paginas, rrn seria o elemento 
class Pagina:
    def __init__(self) -> None:
        self.num_chaves: int = 0
        self.chaves: list = [NULO] * (ORDEM - 1) # as chaves são um par [id, byte_offset]
        self.filhos: list = [NULO] * ORDEM
        
"""
Parte do enunciado do trabalho:
sendo programa.py o nome do arquivo com o seu código e -b a flag que sinaliza o modo de criação do índice. 
Sempre que ativada, essa funcionalidade lerá o arquivo games.dat e fará a inserção dos pares {chave, byte-offset} 
na árvore-B que deverá ser armazenada em um arquivo binário chamado btree.dat

Página:
|numChaves|chave chave chave|rrnFilho rrnFilho rrnFilho rrnFilho|
"""

# def separa_id():
#     with open('games.dat', 'rb') as jogos:
#             tam_bytes = jogos.read(2)
            
#             while tam_bytes:
#                 tam_int = int.from_bytes(tam_bytes, 'little')
#                 registro = jogos.read(tam_int).decode('utf-8')
#                 campos = registro.split(sep='|')
#                 id = int(campos[0])
#     return id, 

# 4 -  LEITURA DE PÁGINA
# -----------------------------------------------------
# FUNÇÃO lePagina(rrn)
#   calcule o byte-offset da página a partir de rrn
#   faça seek no arquivo árvore-B para o byte-offset calculado
#   leia do arquivo árvore-B para pag
#   retorne pag
# fim FUNÇÃO

# def constroi_pagina() -> tuple

def le_pagina(rrn: int) -> Pagina:
    '''
    Essa função vai ler a página de rrn *rrn* armazenada no btree.dat e retorná-la com um dado do tipo Pagina
    '''
    pos_inicio_pag: int = TAM_CAB + (TAM_PAG * rrn)
    with open("btree.dat", 'rb') as arq_arvore_b:
        arq_arvore_b.seek(0, pos_inicio_pag) # movo o ponteiro do arquivo até o início da página
        pag_bytes: bytes = arq_arvore_b.read(TAM_PAG) # leio a página
        infos_pag: tuple = unpack(FORMATO_PAG, pag_bytes)
        
        pag: Pagina = Pagina()
        pag.num_chaves = infos_pag[0]
        # pag.chaves = infos_pag[1]
        # pag.filhos = infos_pag[2]
    
    return pag

# 5 - ESCRITA DE PÁGINA
# -----------------------------------------------------
# FUNÇÃO escrevePagina(rrn, pag)
#   calcule o byte-offset da página a partir do rrn
#   faça seek no arquivo árvore-B para o byte-offset calculado
#   escreva pag no arquivo árvore-B
# fim FUNÇÃO

def escreve_pagina(rrn: int, pag: Pagina) -> None:
    '''
    Essa função vai escrever *pag* no rrn *rrn* de btree.dat
    '''
    pos_inicio_pag: int = TAM_CAB + (TAM_PAG * rrn)

    with open("btree.dat", 'r+b') as arq_arvore_b:
        arq_arvore_b.seek(pos_inicio_pag)
        arq_arvore_b.write(pack("h", pag.num_chaves))

        for chave in pag.chaves:
            arq_arvore_b.write(pack("i", chave))
        
        for filho in pag.filhos:
            arq_arvore_b.write(pack("i", filho))
        

# 1 - BUSCA NA ÁRVORE
# -----------------------------------------------------
# FUNÇÃO buscaNaArvore(chave, rrn)
#   se rrn == NULO então  # condição de parada da recursão
#     retorne Falso, NULO, NULO
#   senão
#     leia a página armazenada no rrn para pag
#     achou, pos = buscaNaPagina(chave, pag)
#     # POS recebe a posição em que CHAVE ocorre em PAG 
#     # ou deveria ocorrer se estivesse em PAG 
#     se achou então
#       retorne Verdadeiro, rrn, pos
#     senão
#       # busque na página filha
#       retorne buscaNaArvore(chave, pag.filhos[pos])
#     fim se
#   fim se
# fim FUNÇÃO

def busca_na_arvore(chave: int, rrn: int) -> tuple[bool, int, int]:
    '''
    busca *chave* na árvore-b que a raiz tem o rrn *rrn*
    Retorna uma tupla com:
    - Se o elemento foi achado ou não
    - O rrn da página
    - A posição da chave na página
    '''
    if rrn == NULO:
        return False, NULO, NULO
    else:
        pag: Pagina = le_pagina("games.dat")
        achou, pos = busca_na_pagina(chave, pag)
        if achou:
            return True, rrn, pos
        else:
            return busca_na_arvore(chave, pag.filhos[pos])
        

def busca_na_pagina (chave: int, pagina: Pagina) -> tuple[bool, int]:
    '''busca *chave* na pagina que contem a chave buscada 
    Retorna a posicao em que ela esta
    '''
    pos = 0 
    while pos < pagina.numChaves and chave > pagina.chaves[pos]:
        pos =+1 
    if pos < pos < pagina.numChaves and chave == pagina.chaves[pos]:
        return True, pos
    else:
        return False, pos

def novo_rrn ():
    ''' Calcula o novo rrn da proxima pagina que sera gravada 
    no arquivo da arvore.
    '''
    arq = open('games.dat', 'rb')
    arq.seek(0, 2)
    offset = arq.tell()
    return (offset - TAM_CAB)// TAM_PAG







def main() -> None: 
    flag = argv[1]

    if flag == '-b':
        # Criação do índice (árvore-B) a partir do arquivo de registros
        print("flag -b")
        
        with open('btree.dat', 'wb') as arq_arvore_b:
            print("Arquivo criado com sucesso!")
    
    elif flag == '-e':
        # Execução de um arquivo de operações (apenas busca e inserção)
        print("flag -e")

    elif flag == '-p':
        # Impressão das informações do índice, i.e., da árvore-B
        print("flag -p")
        
if __name__ == '__main__':
    main()