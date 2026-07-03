from sys import argv

NULO = -1
ORDEM: int = 4

class Pagina:
    def init(self) -> None:
        self.numChaves: int = 0
        self.chaves: list = [NULO] * (ORDEM-1) # as chaves são um par [chave, byte_offset]
        self.filhos: list = [NULO] * ORDEM

def main() -> None: 
    flag = argv[1]

    if flag == '-b':
        # Criação do índice (árvore-B) a partir do arquivo de registros
        print("flag -b")
    
    elif flag == '-e':
        # Execução de um arquivo de operações (apenas busca e inserção)
        print("flag -e")

    elif flag == '-p':
        # Impressão das informações do índice, i.e., da árvore-B
        print("flag -p")
        
if __name__ == '__main__':
    main()