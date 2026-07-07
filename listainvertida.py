# exemplo campo: 100|God of War|2005|Hack and Slash|Sony|PlayStation 2|

from struct import pack, unpack, calcsize
from sys import argv
import io
import os

TAM_INDICE = 'i'

def busca_pos_lst_inv(ind_sec: list[list], chave_sec: str) -> int:
    '''
    Retorna a posição de *chave_sec* na lista invertida
    Se não achar, retorna -1
    
    *ind_sec* está ordenado
    '''
    ind_lst_inv = -1
    i = 0
    while ind_lst_inv == -1 and i < len(ind_sec):
        if ind_sec[i][0] == chave_sec:
            ind_lst_inv = ind_sec[i][1]
        i += 1
        
    return ind_lst_inv

def atualiza_ind_sec(lst_inv: list[list], ind_sec: list[list], chave_sec: str, i: int) -> tuple[list[list], list[list]]:
    '''
    Atualiza *lst_inv* e *ind_sec*
    
    *Eu acabei de inserir o registro na lista invertida
    '''
    ind = busca_pos_lst_inv(ind_sec, chave_sec)
    if ind == -1:
        ind_sec.append([chave_sec, len(lst_inv)-1])
        ind_sec.sort()
    else:
        elem_lst_inv = lst_inv[ind]
        while elem_lst_inv[i] != -1:
            elem_lst_inv = lst_inv[elem_lst_inv[i]]
        elem_lst_inv[i] = len(lst_inv)-1
    
    return lst_inv, ind_sec

def salva_ind_prim(ind_prim: list[list]) -> None:
    '''
    Salva *ind_prim* no disco.
    '''
    with open('primario.ind', 'wb') as arq_ind_prim:
        for entrada in ind_prim:
            buffer = pack('<'+(TAM_INDICE*2), entrada[0], entrada[1])
            arq_ind_prim.write(buffer)

def salva_lst_inv(lst_inv: list[list]) -> None:
    '''
    Salva *lst_inv* no disco.
    '''
    with open('listaInvertida.lst', 'wb') as arq_lst_inv:
        for entrada in lst_inv:
            buffer = pack('<'+(TAM_INDICE*3), entrada[0], entrada[1], entrada[2])
            arq_lst_inv.write(buffer)

def salva_ind_sec(ind_sec: list[list], nome_arq: str) -> None:
    '''
    Salva *ind_sec* no disco no seguinte formato:
    
    [tamanho da str em 2 bytes][str][posição na lista invertida]
    '''
    with open(nome_arq, 'wb') as arq_ind_sec:
        for entrada in ind_sec:
            nome_campo_bytes = entrada[0].encode('utf-8')
            tam_campo_bytes = len(nome_campo_bytes).to_bytes(2, 'little')
            
            arq_ind_sec.write(tam_campo_bytes)
            arq_ind_sec.write(nome_campo_bytes)
            arq_ind_sec.write(pack('<'+TAM_INDICE, entrada[1]))

def constroi_indices() -> None:
    '''
    Cria:
    - índice primário
    - índice secundário por gênero
    - índeice secundário por publicadora
    - lista invertida
    
    E escreve tudo no disco
    '''
    ind_prim: list[list] = []
    lst_inv: list[list] = []
    ind_sec_gen: list[list] = []
    ind_sec_pub: list[list] = []
    
    with open('games.dat', 'rb') as jogos:
        offset = jogos.tell()
        tam_bytes = jogos.read(2)
        
        while tam_bytes:
            tam_int = int.from_bytes(tam_bytes, 'little')
            registro = jogos.read(tam_int).decode('utf-8')
            campos = registro.split(sep='|')
            id = int(campos[0])
            
            ind_prim.append([id, offset])
            
            lst_inv.append([id, -1, -1])    
            lst_inv, ind_sec_gen = atualiza_ind_sec(lst_inv, ind_sec_gen, campos[3], 1)
            lst_inv, ind_sec_pub = atualiza_ind_sec(lst_inv, ind_sec_pub, campos[4], 2)
            
            offset = jogos.tell()
            tam_bytes = jogos.read(2)
            
        ind_prim.sort()
    
    salva_ind_prim(ind_prim)
    salva_lst_inv(lst_inv)
    salva_ind_sec(ind_sec_gen, 'genero.ind')
    salva_ind_sec(ind_sec_pub, 'publicadora.ind')

def id_duplicado(ind_prim: list[list], registro: str) -> bool:
    '''
    Retorna True se o ID de *registro* já existe em *ind_prim*
    '''
    campos = registro.split(sep = '|') #separa o registro em campos 
    id = int(campos[0])
    
    duplicado = False
    for item in ind_prim: #verifica se o id esta duplicado e ja existe na lista de ind primario
        id_item = item[0]
        if id == id_item:
            duplicado = True
            return duplicado

    return duplicado

def insere_registro(ind_prim: list[list], lst_inv: list[list], ind_sec_gen: list[list], ind_sec_pub: list[list], registro: str) -> tuple[
    list[list], list[list], list[list], list[list], int, int]:
    '''
    Insere *registro* adequadamente nos índices e na lista invertida
    '''
    with open('games.dat', 'ab') as jogos:
        offset = jogos.tell()
        campos = registro.split(sep = '|') #separa o registro em campos 
        id = int(campos[0])
        
        ind_prim.append([id, offset])
        ind_prim.sort()
        
        lst_inv.append([id, -1, -1])    
        lst_inv, ind_sec_gen = atualiza_ind_sec(lst_inv, ind_sec_gen, campos[3], 1)
        lst_inv, ind_sec_pub = atualiza_ind_sec(lst_inv, ind_sec_pub, campos[4], 2)
        
        registro_bytes = registro.encode('utf-8')
        tam_registro_bytes = len(registro_bytes).to_bytes(2, 'little')
        
        jogos.write(tam_registro_bytes)
        jogos.write(registro_bytes)
    
    return ind_prim, lst_inv, ind_sec_gen, ind_sec_pub, id, len(registro_bytes)

def prox_oper(operacoes: io.BufferedReader) -> str:
    operacao = operacoes.read(1).decode()
    caracter = operacoes.read(1).decode()
    while caracter != ' ' and caracter != '':
        operacao += caracter
        caracter = operacoes.read(1).decode()
    return operacao

def carrega_ind_prim() -> list[list]:
    '''
    Carrega o arquivo primario.ind para a memória.
    As entradas tem o seguinte formato:
    
    [ID][offset]
    '''
    ind_prim: list[list] = []

    formato = '<' + (TAM_INDICE * 2)
    tam_entrada = calcsize('<' + (TAM_INDICE * 2))

    with open('primario.ind', 'rb') as arq_ind_prim:
        entrada = arq_ind_prim.read(tam_entrada)

        while entrada:
            id_jogo, offset = unpack(formato, entrada)
            ind_prim.append([id_jogo, offset])

            entrada = arq_ind_prim.read(tam_entrada)

    return ind_prim

def carrega_lst_inv() -> list[list]:
    '''
    Carrega o arquivo listaInvertida.lst para a memória.
    As entradas tem o seguinte formato:
    
    [ID][próximo genero][próxima publicadora]
    '''
    lst_inv: list[list] = []

    formato = '<' + (TAM_INDICE * 3)
    tam_entrada = calcsize(formato)

    with open('listaInvertida.lst', 'rb') as arq_lst_inv:
        entrada = arq_lst_inv.read(tam_entrada)

        while entrada:
            id_jogo, prox_genero, prox_publicadora = unpack(formato, entrada)
            lst_inv.append([id_jogo, prox_genero, prox_publicadora])

            entrada = arq_lst_inv.read(tam_entrada)

    return lst_inv

def carrega_ind_sec(nome_arq: str) -> list[list]:
    '''
    Carrega um índice secundário para a memória.

    As entradas tem o seguinte formato:
    [tamanho da string em 2 bytes][string][posição na lista invertida]
    '''
    ind_sec: list[list] = []

    with open(nome_arq, 'rb') as arq_ind_sec:
        tam_campo_bytes = arq_ind_sec.read(2)

        while tam_campo_bytes:
            tam_campo_int = int.from_bytes(tam_campo_bytes, 'little')

            nome_campo_bytes = arq_ind_sec.read(tam_campo_int)
            nome_campo_str = nome_campo_bytes.decode('utf-8')

            formato_pos = '<' + TAM_INDICE
            tam_pos = calcsize(formato_pos)

            pos_bytes = arq_ind_sec.read(tam_pos)
            pos_lst_inv = unpack(formato_pos, pos_bytes)[0]

            ind_sec.append([nome_campo_str, pos_lst_inv])

            tam_campo_bytes = arq_ind_sec.read(2)

    return ind_sec

def busca_ind_prim(id: int, ind_prim: list[list]) -> None:
    encontrado = False
    offset = -1
    for jogo in ind_prim:
        id_jogo = jogo[0]
        if id == id_jogo:
            encontrado = True
            offset = jogo[1]

    if encontrado:
        with open('games.dat','rb') as jogos:
            jogos.seek(offset, os.SEEK_SET)
            tam_bytes = jogos.read(2)
            tam = int.from_bytes(tam_bytes, byteorder='little')

            registro = jogos.read(tam)
            reg_decodificado = registro.decode('utf-8')
            print("Busca pelo registro de ID *" + str(id) + "*")
            print(reg_decodificado + "\n")
    else:
        print("O Índice não foi encontrado\n")

def busca_indice_secundario(ind_prim: list[list], lst_inv: list[list], ind_sec: list[list], chave_sec: str, i):
    pos_lista_invertida = -1
    
    for indice in ind_sec:
        chave = indice[0]
        if chave_sec == chave:
            pos_lista_invertida = indice[1]
    
    if pos_lista_invertida == -1:
        print("Não existe nenhum jogo com esse índice")
    else:
        itens: list[list] = []
        item = lst_inv[pos_lista_invertida]
        itens.append(item[0])
        
        while item[i] != -1:
            item = lst_inv[item[i]]
            itens.append(item[0])

        jogos = open('games.dat','rb')
        
        if i == 1:
            print("Busca por registros de gênero *" + chave_sec + "* (" + str(len(itens)) + " registros)")
        else:
            print("Busca por registros da publicadora *" + chave_sec + "* (" + str(len(itens)) + " registros)")

        for id in itens:
            offset = -1
            
            for jogo in ind_prim:
                id_jogo = jogo[0]
                if id == id_jogo:
                    offset = jogo[1]
                    
            jogos.seek(offset, os.SEEK_SET)
            tam_bytes = jogos.read(2)
            tam = int.from_bytes(tam_bytes, byteorder='little')

            registro = jogos.read(tam)
            reg_decodificado = registro.decode('utf-8')
            print(reg_decodificado)
            
        print()
        jogos.close()

def main() -> None: 
    flag = argv[1]

    if flag == '-b':
        try:
            arquivo = open("games.dat", 'rb')
            arquivo.close()
        except FileNotFoundError:
            print("Erro: o arquivo 'games.dat' não existe")
            
        constroi_indices()
        print('Índices construídos com sucesso!')
    
    if flag == '-e':
        arquivos_existem = True
        
        try:
            arq_jogos = open('games.dat', 'rb')
            arq_ind_prim = open('primario.ind', 'rb')
            arq_lst_inv = open('listaInvertida.lst', 'rb')
            arq_ind_sec_gen = open('genero.ind', 'rb')
            arq_ind_sec_pub = open('publicadora.ind', 'rb')

            arq_jogos.close()
            arq_ind_prim.close()
            arq_lst_inv.close()
            arq_ind_sec_gen.close()
            arq_ind_sec_pub.close()

        except FileNotFoundError:
            arquivos_existem = False
            print("Arquivos não encontrados")

        if arquivos_existem:
            ind_prim = carrega_ind_prim()
            lst_inv = carrega_lst_inv()
            ind_sec_gen = carrega_ind_sec('genero.ind')
            ind_sec_pub = carrega_ind_sec('publicadora.ind')
            
            nome_arq_oper = argv[2]
            with open(nome_arq_oper, 'rb') as operacoes:
                operacao = prox_oper(operacoes)
                
                while operacao != '':
                    argumento = operacoes.readline().decode('utf-8').strip()
                    
                    if operacao == 'i':
                        if id_duplicado(ind_prim, argumento):
                            print("Inserção não realizada, ID duplicado\n")
                        else:
                            ind_prim, lst_inv, ind_sec_gen, ind_sec_pub, id, tam_registro = insere_registro(ind_prim, lst_inv, ind_sec_gen, ind_sec_pub, argumento)
                            print("Inserção do registro de chave *" + str(id) + "* (" + str(tam_registro) + " bytes)\n")
                            
                    elif operacao == 'bp':
                        busca_ind_prim(int(argumento), ind_prim)
                    
                    elif operacao == 'bs1':
                        busca_indice_secundario(ind_prim, lst_inv, ind_sec_gen, argumento, 1)
                    
                    elif operacao == 'bs2':
                        busca_indice_secundario(ind_prim, lst_inv, ind_sec_pub, argumento, 2)
                    
                    elif operacao == 'r':
                        print("Operação não implementada")
                
                    operacao = prox_oper(operacoes)
                
                salva_ind_prim(ind_prim)
                salva_lst_inv(lst_inv)
                salva_ind_sec(ind_sec_gen, 'genero.ind')
                salva_ind_sec(ind_sec_pub, 'publicadora.ind')
                
    if flag == '-c':
        print("Operação não implementada")
        
if __name__ == '__main__':
    main()