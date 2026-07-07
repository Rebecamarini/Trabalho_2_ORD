from sys import argv
from struct import pack, unpack, calcsize

NULO = -1
ORDEM = 4

# Exemplo da página de uma árvore-b de ordem = 4:
# num_chaves chave chave chave rrnFilho rrnFilho rrnFilho rrnFilho

# Número de chaves no formato 'H' (int de 2 bytes sem sinal)
# Chaves no formato 'ii' (id -> 'i' e byte offset -> 'i')
# RRN dos filhos no formato 'i'
PREFIXO = "<"
FORMATO_NUM_CHAVES = "H"
FORMATO_ID = "i"
FORMATO_BYTE_OFFSET = "i"
FORMATO_RRN_FILHO = "i"
FORMATO_PAG = PREFIXO + FORMATO_NUM_CHAVES + (FORMATO_ID+FORMATO_BYTE_OFFSET)*(ORDEM-1) + FORMATO_RRN_FILHO*ORDEM
TAM_PAG = calcsize(FORMATO_PAG)

# A nossa árvore terá um cabeçalho que guarda o rrn da página raiz
FORMATO_CAB = "i"
TAM_CAB = calcsize(PREFIXO + FORMATO_CAB)

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
        self.chaves: list[Chave] = []
        for _ in range(ORDEM - 1):
            self.chaves.append(Chave())
        self.rrn_filhos: list[int] = [NULO] * ORDEM

# -----------------------------------------------------
# LEITURA DE PÁGINA
# -----------------------------------------------------
# FUNÇÃO lePagina(rrn)
#   calcule o byte-offset da página a partir de rrn
#   faça seek no arquivo árvore-B para o byte-offset calculado
#   leia do arquivo árvore-B para pag
#   retorne pag
# fim FUNÇÃO

def calcula_pos_inicio_pag(rrn: int) -> int:
    '''
    Retorna o byte offset do início da página de RRN *rrn*
    '''
    return TAM_CAB + (TAM_PAG * rrn)
    
def constroi_pagina(infos_pag: tuple) -> Pagina:
    '''
    Recebe as informações de uma página em *infos* e as retorna como um dado do tipo Pagina
    '''
    # Criação das listas que colocarei as chaves e rrn dos filhos que estão em *infos_pag*
    num_chaves: int = infos_pag[0]
    chaves_pag: list[Chave] = []
    rrn_filhos_pag: list[int] = []
    
    # Inserção das chaves de *infos_pag* em *chaves_pag*
    for i in range(ORDEM - 1):
        chave: Chave = Chave()
        chave.id = infos_pag[(i*2)+1]
        chave.byte_offset = infos_pag[(i*2)+2]
        chaves_pag.append(chave)
    
    # Inserção dos RRNs dos filhos de *infos_pag* em *chaves_pag*
    for i in range(ORDEM):
        rrn_filho: int = infos_pag[(ORDEM-1)*2 + 1 + i]
        rrn_filhos_pag.append(rrn_filho)
    
    # Criação e preenchimento da página
    pag: Pagina = Pagina()
    pag.num_chaves = num_chaves
    pag.chaves = chaves_pag
    pag.rrn_filhos = rrn_filhos_pag
    
    # Coloca como saída a página criada
    return pag

def le_pagina(rrn: int) -> Pagina:
    '''
    Lê a página de RRN *rrn* armazenada no btree.dat e a retorna com um dado do tipo Pagina
    '''
    pos_inicio_pag: int = calcula_pos_inicio_pag(rrn)
    
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
    Escreve *pag* no RRN *rrn* de btree.dat
    '''
    pos_escrita_pag: int = calcula_pos_inicio_pag(rrn)

    with open("btree.dat", 'r+b') as arq_arvore_b:
        arq_arvore_b.seek(pos_escrita_pag)
        
        arq_arvore_b.write(pack(PREFIXO + FORMATO_NUM_CHAVES, pag.num_chaves))

        for chave in pag.chaves:
            arq_arvore_b.write(pack(PREFIXO + FORMATO_ID, chave.id))
            arq_arvore_b.write(pack(PREFIXO + FORMATO_BYTE_OFFSET, chave.byte_offset))
        
        for filho in pag.rrn_filhos:
            arq_arvore_b.write(pack(PREFIXO + FORMATO_RRN_FILHO, filho))
# -----------------------------------------------------

# -----------------------------------------------------
# CÁLCULO DO NOVO RRN
# -----------------------------------------------------
# FUNÇÃO novoRRN()
#   faça seek para o fim do arquivo
#   faça offset receber o byte-offset atual
#   retorne (offset – TAM_CAB) // TAM_PAG
# fim FUNÇÃO

def novo_rrn() -> int:
    ''' 
    Calcula o RRN da proxima pagina que sera gravada no arquivo da árvore.
    '''
    with open('btree.dat', 'rb') as arq_arvore_b:
        arq_arvore_b.seek(0, 2)
        tam_arq = arq_arvore_b.tell()
        return (tam_arq - TAM_CAB) // TAM_PAG
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

def busca_na_pagina (id: int, pagina: Pagina) -> tuple[bool, int]:
    '''
    Busca a chave de Id *id* em *pagina*
    Retorna um ou outro:
    - True e a posição que a chave está na página
    - False e a posição que a chave deveria estar nos filhos
    '''
    pos_chave: int = 0
    while pos_chave < pagina.num_chaves and id > pagina.chaves[pos_chave].id:
        pos_chave += 1 
    if pos_chave < pagina.num_chaves and id == pagina.chaves[pos_chave].id:
        return True, pos_chave
    else:
        return False, pos_chave
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

def busca_na_arvore(id: int, rrn: int) -> tuple[bool, int, int]:
    '''
    Busca a chave de Id *id* em uma árvore-B onde a raiz tem o RRN *rrn*
    Retorna uma tupla com:
    - Se o elemento foi achado ou não
    - O rrn da página
    - A posição da chave na página
    '''
    if rrn == NULO:
        return False, NULO, NULO
    else:
        pag: Pagina = le_pagina(rrn)
        achou, pos = busca_na_pagina(id, pag)
        if achou:
            return True, rrn, pos
        else:
            return busca_na_arvore(id, pag.rrn_filhos[pos])
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

def insere_chave_promo(chave: Chave, rrn_filho_dir: int, pag: Pagina) -> None:
    '''
    Insere a chave *chave* e o rrn *filho_dir* promovidos em *pag*

    '''
    if pag.num_chaves == (ORDEM - 1):
        pag.chaves.append(Chave())
        pag.rrn_filhos.append(NULO)
    i = pag.num_chaves
    while i > 0 and chave.id < pag.chaves [i-1].id:
        pag.chaves[i] = pag.chaves[i-1]
        pag.rrn_filhos[i+1] = pag.rrn_filhos[i]
        i =  i - 1
    pag.chaves[i] = chave 
    pag.rrn_filhos[i+1] = rrn_filho_dir
    pag.num_chaves = pag.num_chaves + 1

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
def divide(chave: Chave, rrn_filho_dir: int, pag:Pagina)-> tuple[Chave, int, Pagina, Pagina]:
    '''
    A funcao realiza a divisao de *pag* em duas em caso de promoção de *chave* e *rrn_filho_dir*
    Retorna uma tupla com:
    - A chave promovida 
    - O RRN do filho direito da chave promovida
    - A página atual 
    - A página nova depois da promoção
    '''
    insere_chave_promo(chave, rrn_filho_dir, pag)
    meio = ORDEM // 2
    chave_pro = pag.chaves[meio]
    rrn_filho_dir_pro = novo_rrn()
    pag_atual = Pagina()
    pag_atual.chaves = pag.chaves[:meio] + [Chave() for _ in range(ORDEM - 1 - meio)]
    pag_atual.rrn_filhos = pag.rrn_filhos[:meio + 1] + [NULO] * (ORDEM - (meio + 1))
    pag_atual.num_chaves = meio
 
    resto_chaves = pag.chaves[meio + 1:]
    resto_filhos = pag.rrn_filhos[meio + 1:]
    pag_nova = Pagina()
    pag_nova.chaves = resto_chaves + [Chave() for _ in range(ORDEM - 1 - len(resto_chaves))]
    pag_nova.rrn_filhos = resto_filhos + [NULO] * (ORDEM - len(resto_filhos))
    pag_nova.num_chaves = len(resto_chaves)

    return chave_pro, rrn_filho_dir_pro, pag_atual, pag_nova

    
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

def insere_chave(chave: Chave, rrn_atual: int) -> tuple[Chave|int, int, bool]:
    '''
    A funcao insere com divisão e promoção a *chave* na página de RRN *rrn_atual* 
    Retorna uma tupla com:
    - A chave promovida 
    - O RRN do filho direito da chave promovida
    - E se houve inserção
    '''
    if rrn_atual == NULO:
        chave_pro: Chave|int = chave 
        rrn_filho_dir_pro: int = NULO
        return chave_pro, rrn_filho_dir_pro, True
    else:
        pag = le_pagina(rrn_atual)
        achou, pos = busca_na_pagina(chave.id, pag)

    if achou:
        raise ValueError("Erro: Chave duplicada")
    
    chave_pro, rrn_filho_dir_pro, promo = insere_chave(chave, pag.rrn_filhos[pos])

    if not promo:
        return NULO, NULO , False
    else:
        assert isinstance(chave_pro, Chave)
        if pag.num_chaves < (ORDEM - 1):
            insere_chave_promo(chave_pro, rrn_filho_dir_pro, pag) 
            escreve_pagina(rrn_atual, pag)
            return NULO, NULO ,False
        else:
            chave_pro, rrn_filho_dir_pro, pag_atual, pag_nova = divide(chave_pro, rrn_filho_dir_pro,pag)
            escreve_pagina(rrn_atual, pag_atual)
            escreve_pagina(rrn_filho_dir_pro, pag_nova)
            return chave_pro, rrn_filho_dir_pro, True
        

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
def insere_na_arvore(chave: Chave, rrn_raiz: int) -> int:
    '''
    Insere *chave* na árvore-B que a raiz possui o RRN *rrn_raiz* e retorna 
    o RRN da raiz da árvore-B com o elemento inserido.
    '''
    chave_pro, rrn_filho_dir_pro, promo = insere_chave(chave, rrn_raiz)
    if promo:
        assert isinstance(chave_pro, Chave)
        pag_nova = Pagina()
        pag_nova.chaves[0] = chave_pro
        pag_nova.rrn_filhos[0] = rrn_raiz
        pag_nova.rrn_filhos[1] = rrn_filho_dir_pro
        pag_nova.num_chaves = pag_nova.num_chaves + 1
        rrn_raiz = novo_rrn()
        escreve_pagina(rrn_raiz,pag_nova)
    return rrn_raiz


def constroi_arvore() -> None:
    '''
    Lê games.dat registro por registro, monta a árvore-B em btree.dat
    '''
    # Cria o btree.dat com cabecalho indicando arvore vazia
    with open('btree.dat', 'wb') as arq_arvore_b:
        arq_arvore_b.write(pack(PREFIXO + FORMATO_CAB, NULO))

    rrn_raiz = NULO

    with open('games.dat', 'rb') as jogos:
        while True:
            offset = jogos.tell()          # offset
            tam_bytes = jogos.read(2)
            if not tam_bytes:
                break                       # fim do arquivo

            tam_int = int.from_bytes(tam_bytes, 'little')
            registro = jogos.read(tam_int).decode('utf-8')
            campos = registro.split(sep='|')
            id_reg = int(campos[0])

            chave = Chave()
            chave.id = id_reg
            chave.byte_offset = offset

            rrn_raiz = insere_na_arvore(chave, rrn_raiz)

    # atualiza o cabecalho com o RRN final da raiz
    with open('btree.dat', 'r+b') as arq_arvore_b:
        arq_arvore_b.seek(0)
        arq_arvore_b.write(pack(PREFIXO + FORMATO_CAB, rrn_raiz))


def le_raiz() -> int:
    '''
    Retorna o RRN da raiz de btree.dat, retorna NULO se o cabeçanho não corresponder a um RRN.
    '''
    with open('btree.dat', 'rb') as arq_arvore_b:
        raiz_bytes = arq_arvore_b.read(TAM_CAB)    # le os primeiros bytes do arquivo (o cabecalho)
        if len(raiz_bytes) == TAM_CAB:
            return unpack(PREFIXO + FORMATO_CAB, raiz_bytes)[0]   # decodifica esses bytes
        else:
            return NULO


def imprime_pagina(rrn: int, pag: Pagina):
    print("Página " + str(rrn) + ":")

    linha_chaves = "Chaves = "
    linha_offsets = "Offsets = "
    for i in range(len(pag.chaves)):
        linha_chaves = linha_chaves + str(pag.chaves[i].id)
        linha_offsets = linha_offsets + str(pag.chaves[i].byte_offset)
        if i < len(pag.chaves) - 1:
            linha_chaves = linha_chaves + " | "
            linha_offsets = linha_offsets + " | "
    print(linha_chaves)
    print(linha_offsets)

    linha_filhos = "Filhos = "
    for i in range(len(pag.rrn_filhos)):
        linha_filhos = linha_filhos + str(pag.rrn_filhos[i])
        if i < len(pag.rrn_filhos) - 1:
            linha_filhos = linha_filhos + " | "
    print(linha_filhos)



def imprime_arvore() -> None:
    '''
    Imprime todas as páginas da árvore-B guardada em btree.dat por ordem de RRN, destacando a página raiz.
    '''
    total_paginas = novo_rrn()
    rrn_raiz = le_raiz()

    for rrn in range(total_paginas):
        pag = le_pagina(rrn)

        if rrn == rrn_raiz:
            print("- - - - - - - - - - Raiz - - - - - - - - - -")

        imprime_pagina(rrn, pag)

        if rrn == rrn_raiz:
            print("- - - - - - - - - - - - - - - - - - - - - -")

        print()


def arquivo_existe(nome_arq: str) -> bool:
    try:
        arquivo = open(nome_arq, 'rb')
        arquivo.close()
        return True

    except FileNotFoundError:
        print(f'Erro: o arquivo "{nome_arq}" não existe')
        return False


def main() -> None: 
    flag = argv[1]

    if flag == '-b':
        # Criação do índice (árvore-B) a partir do arquivo de registros
        if not arquivo_existe("games.dat"):
            return
        
        constroi_arvore()
        print('Árvore construída com sucesso!')

    elif flag == '-e':
        # Execução de um arquivo de operações (apenas busca e inserção)
        if not arquivo_existe("games.dat"):
            return
        if not arquivo_existe("btree.dat"):
            return
        
        nome_arq_op: str = argv[2]
        rrn_raiz: int = le_raiz()

        with open(nome_arq_op, 'r', encoding='utf-8') as arq_op:
            for linha in arq_op:
                linha = linha.rstrip('\r\n')

                if not linha:
                    continue

                operacao, argumento = linha.split(' ', 1)

                if operacao == 'b':
                    id_registro: int = int(argumento)
                    print(f'Busca pelo registro de chave "{id_registro}"')
                    achou, rrn_pag, pos_na_pag = busca_na_arvore(id_registro, rrn_raiz)
                    if not achou:
                        print(f'Erro: chave "{id_registro}" não encontrada')
                    else:
                        pag: Pagina = le_pagina(rrn_pag)
                        byte_offset: int = (pag.chaves[pos_na_pag].byte_offset)
                        with open('games.dat', 'rb') as arq_jogos:
                            arq_jogos.seek(byte_offset)
                            tam_bytes: bytes = arq_jogos.read(2)
                            tam_registro: int = int.from_bytes(tam_bytes, 'little')
                            registro: str = arq_jogos.read(tam_registro).decode('utf-8')
                        print(f'{registro} ' f'({tam_registro} bytes - ' f'offset {byte_offset})')
                    print()

                elif operacao == 'i':
                    registro = argumento
                    id_registro = int(registro.split('|', 1)[0])
                    print(f'Inserção do registro de chave ' f'"{id_registro}"')
                    achou, _, _ = busca_na_arvore(id_registro, rrn_raiz)

                    if achou:
                        print(f'Erro: chave "{id_registro}" duplicada')
                    else:
                        registro_bytes: bytes = registro.encode('utf-8')
                        tam_registro = len(registro_bytes)
                        with open('games.dat', 'ab') as arq_jogos:
                            byte_offset = arq_jogos.tell()
                            arq_jogos.write(tam_registro.to_bytes(2, 'little'))
                            arq_jogos.write(registro_bytes)
                        chave = Chave()
                        chave.id = id_registro
                        chave.byte_offset = byte_offset
                        rrn_raiz = insere_na_arvore(chave, rrn_raiz)

                        # Atualiza o cabeçalho, pois uma divisão
                        # pode ter criado uma nova raiz.
                        with open('btree.dat', 'r+b') as arq_arvore_b:
                            arq_arvore_b.seek(0)
                            arq_arvore_b.write(
                            pack(PREFIXO + FORMATO_CAB, rrn_raiz))
                        print(f'{registro} ' f'({tam_registro} bytes - ' f'offset {byte_offset})')
                    print()
        print("As operações do arquivo *" + nome_arq_op + "* foram executadas com sucesso!")

    elif flag == '-p':
        # Impressão das informações do índice, i.e., da árvore-B
        if not arquivo_existe("btree.dat"):
            return
        
        imprime_arvore()
        
if __name__ == '__main__':
    main()