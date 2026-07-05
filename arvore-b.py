from sys import argv
from struct import pack, unpack, calcsize

NULO = -1
ORDEM = 4

# Convencionamos que:
# - Cabeçalho no fomrato 'H' (int de 2 bytes sem sinal)
# - Chaves no formato 'ii' (id -> 'i' e byte offset -> 'i')
# - Filhos no formato 'i'
# Exemplo de Página de uma árvore-b de ordem = 4:
# num_chaves chave chave chave rrnFilho rrnFilho rrnFilho rrnFilho
TAM_CAB = 2
FORMATO_PAG = "H" + "ii"*(ORDEM-1) + "i"*ORDEM
TAM_PAG = calcsize(FORMATO_PAG)

class Chave:
    '''
    representa a chave da árvore-B como um par [id, byte offset]
    '''
    def __init__(self) -> None:
        self.id: int = NULO
        self.byte_offset: int = NULO

# usar lista de paginas, rrn seria o elemento 
class Pagina:
    def __init__(self) -> None:
        self.num_chaves: int = 0
        self.chaves: list[Chave] = [Chave()] * (ORDEM - 1) # As chaves são um par [id, byte_offset]
        self.filhos: list = [NULO] * ORDEM

'''
def separa_id():
    with open('games.dat', 'rb') as jogos:
            tam_bytes = jogos.read(2)
            
            while tam_bytes:
                tam_int = int.from_bytes(tam_bytes, 'little')
                registro = jogos.read(tam_int).decode('utf-8')
                campos = registro.split(sep='|')
                id = int(campos[0])
    return id,
''' 

# -----------------------------------------------------
# LEITURA DE PÁGINA
# -----------------------------------------------------
# FUNÇÃO lePagina(rrn)
#   calcule o byte-offset da página a partir de rrn
#   faça seek no arquivo árvore-B para o byte-offset calculado
#   leia do arquivo árvore-B para pag
#   retorne pag
# fim FUNÇÃO

def constroi_pagina(infos_pag: tuple) -> Pagina:
    '''
    Recebe as informações de uma página em *infos* e as retorna como um dado do tipo Pagina
    '''
    # Criação das listas que colocarei as chaves e rr dos filhos que estão em *infos_pag*
    chaves_pag: list[int] = []
    rrn_filhos_pag: list[int] = []
    
    # Inserção das chaves de *infos_pag* em *chaves_pag*
    
    # Criação e preenchimento da página
    pag: Pagina = Pagina()
    pag.num_chaves = infos_pag[0]
    
    # Coloca como saída a página criada
    return pag

def le_pagina(rrn: int) -> Pagina:
    '''
    Lê a página de rrn *rrn* armazenada no btree.dat e a retorna com um dado do tipo Pagina
    '''
    pos_inicio_pag: int = TAM_CAB + (TAM_PAG * rrn)
    
    with open("btree.dat", 'rb') as arq_arvore_b:
        # Movimentação do ponteiro do *arq_arvore_b* até o início da página
        arq_arvore_b.seek(pos_inicio_pag, 0)
        
        # Leitura da página
        pag_bytes: bytes = arq_arvore_b.read(TAM_PAG)
        
        # Descodificação da página
        infos_pag: tuple = unpack(FORMATO_PAG, pag_bytes)

    # Coloca como saída um dado do tipo Pagina com as informações obtidas anteriormente
    return constroi_pagina(infos_pag)
# -----------------------------------------------------

# -----------------------------------------------------
# ESCRITA DE PÁGINA
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
# -----------------------------------------------------

# -----------------------------------------------------
# CÁLCULO DO NOVO RRN
# -----------------------------------------------------
# FUNÇÃO novoRRN()
#   faça seek para o fim do arquivo
#   faça offset receber o byte-offset atual
#   retorne (offset – TAM_CAB) // TAM_PAG
# fim FUNÇÃO

def novo_rrn ():
    ''' Calcula o novo rrn da proxima pagina que sera gravada 
    no arquivo da arvore.
    '''
    arq = open('games.dat', 'rb')
    arq.seek(0, 2)
    offset = arq.tell()
    return (offset - TAM_CAB)// TAM_PAG
# -----------------------------------------------------


# -----------------------------------------------------
# BUSCA NA PÁGINA
# -----------------------------------------------------
# FUNÇÃO buscaNaPagina(chave, pag)
#   faça pos receber 0
#   enquanto pos < pag.numChaves e chave > pag.chaves[pos] faça
#     incremente pos
#   se pos < pag.numChaves e chave == pag.chaves[pos] então
#     retorne Verdadeiro, pos
#   senão
#     retorne Falso, pos
# fim FUNÇÃO

def busca_na_pagina (chave: int, pagina: Pagina) -> tuple[bool, int]:
    '''busca *chave* na pagina que contem a chave buscada 
    Retorna a posicao em que ela esta
    '''
    pos = 0 
    while pos < pagina.num_chaves and chave > pagina.chaves[pos]:
        pos =+1 
    if pos < pos < pagina.num_chaves and chave == pagina.chaves[pos]:
        return True, pos
    else:
        return False, pos
# -----------------------------------------------------


# -----------------------------------------------------
# BUSCA NA ÁRVORE
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
# -----------------------------------------------------


# -----------------------------------------------------
# INSERÇÃO DE CHAVE E FILHO PROMOVIDOS EM UMA PÁGINA
# -----------------------------------------------------
# FUNÇÃO insereChavePromo(chave, filhoD, pag)
#   se pag estiver cheia, aumente a sua capacidade
#   faça i receber pag.numChaves
#   enquanto i > 0 e chave < pag.chaves[i-1] faça
#     pag.chaves[i] = pag.chaves[i-1]
#     pag.filhos[i+1] = pag.filhos[i]
#     decremente i
#   faça pag.chaves[i] receber chave
#   faça pag.filhos[i+1] receber filhoD
#   incremente pag.numChaves
# fim FUNÇÃO


# -----------------------------------------------------


# -----------------------------------------------------
# DIVISÃO DE PÁGINA
# -----------------------------------------------------
# FUNÇÃO divide(chave, filhoD, pag)
#   insira chave e filhoD em pag  # usando a função insereChavePromo
#   faça meio receber ORDEM // 2
#   faça chavePro receber pag.chaves[meio]
#   faça filhoDpro receber o RRN que a pNova terá no arquivo árvore-b
#   faça pAtual receber o conteúdo de pag até meio
#   faça pNova receber o conteúdo de pag a partir de meio+1
#   retorne chavePro, filhoDpro, pAtual, pNova
# fim FUNÇÃO

# -----------------------------------------------------


# -----------------------------------------------------
# INSERÇÃO DE CHAVE (COM DIVISÃO E PROMOÇÃO)
# -----------------------------------------------------
# FUNÇÃO insereChave(chave, rrnAtual)
#   se rrnAtual == NULO então  # condição de parada da recursão
#     chavePro = chave
#     filhoDpro = NULO
#     retorne chavePro, filhoDpro, Verdadeiro
#   senão
#     leia a página armazenada em rrnAtual para pag
#     achou, pos = buscaNaPagina(chave, pag)
#   fim se

#   se achou então
#     gere um erro de valor – "Chave duplicada"
#   fim se

#   chavePro, filhoDpro, promo = insereChave(chave, pag.filhos[pos])

#   # continuação, logo após a chamada recursiva
#   se não promo então
#     retorne NULO, NULO, Falso
#   senão
#     se existe espaço em pag para inserir chavePro então
#       insira chavePro e filhoDpro (chave promovida e filha) em pag
#       escreva pag no arquivo em rrnAtual
#       retorne NULO, NULO, Falso
#     senão
#       chavePro, filhoDpro, pag, novaPag = divide(chavePro, filhoDpro, pag)
#       escreva pag no arquivo em rrnAtual
#       escreva novaPag no arquivo em filhoDpro
#       retorne chavePro, filhoDpro, Verdadeiro
#     fim se
#   fim se
# fim função

# -----------------------------------------------------


# -----------------------------------------------------
# INSERÇÃO NA ÁRVORE (TRATA PROMOÇÃO DA RAIZ)
# -----------------------------------------------------
# FUNÇÃO insereNaArvore(chave, raiz)
#   chavePro, filhoDpro, promoção = insereChave(chave, raiz)
#   se promoção então
#     inicialize pNova
#     pNova.chaves[0] = chavePro   # nova chave raiz
#     pNova.filhos[0] = raiz       # filho esquerdo
#     pNova.filhos[1] = filhoDpro  # filho direito
#     incremente pNova.numChaves
#     faça raiz receber o RRN da pNova  # RRN da nova raiz
#     escreva pNova no arquivo em raiz
#   fim se
#   retorne raiz
# fim FUNÇÃO


# -----------------------------------------------------


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