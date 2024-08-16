import json

# Função de codificação dos símbolos conforme a tabela fornecida
def encode_symbol(symbol):
    encoding = {
        '0': '1',
        '1': '11',
        'B': '111',
        'L': '1',
        'R': '11'
    }
    # Codificação dos estados
    if symbol.startswith('q'):
        n = int(symbol[1:])
        return '1' * (n + 1)
    # Codificação dos símbolos e movimentos
    return encoding.get(symbol, '')

# Função para codificar a transição da Máquina de Turing
def encode_transition(state_from, symbol_read, state_to, symbol_write, move_direction):
    return (encode_symbol(state_from) + '0' +
            encode_symbol(symbol_read) + '0' +
            encode_symbol(state_to) + '0' +
            encode_symbol(symbol_write) + '0' +
            encode_symbol(move_direction))

# Função principal para processar o arquivo JSON e gerar a codificação da Máquina de Turing
def process_turing_machine(json_file):
    with open(json_file, 'r') as file:
        machine = json.load(file)
    
    transitions = machine.get('transitions', [])
    encoded_transitions = []
    
    for transition in transitions:
        state_from = transition['from']
        symbol_read = transition['read']
        state_to = transition['to']
        symbol_write = transition['write']
        move_direction = transition['move']
        
        encoded_transitions.append(encode_transition(state_from, symbol_read, state_to, symbol_write, move_direction))
    
    # Juntando as transições codificadas com separadores
    encoded_string = '000' + '00'.join(encoded_transitions) + '000'
    return encoded_string

class TuringMachine:
    def __init__(self, encoded_description, input_string):
        self.fita1 = list(encoded_description + input_string)
        self.fita2 = ['1']  # Representação do estado inicial q0
        self.fita3 = []
        self.head1 = 0
        self.head2 = 0
        self.head3 = 0

    def simulate(self):
        # Passo 1: Validar formato da entrada
        if not self.is_valid_format():
            self.move_right_indefinitely(self.head1)
            return False

        # Passo 2: Copiar w para a fita 3
        self.copy_w_to_fita3()

        # Passo 4: Simular as transições
        while True:
            state_code = self.read_fita2()
            symbol_read = self.read_fita3()

            transition = self.find_transition(state_code, symbol_read)
            if transition is None:
                return False

            self.apply_transition(transition)

    def is_valid_format(self):
        # Considerando que o formato válido começa com '000' (indicando início de R(M))
        # e termina com '000' (indicando o final de R(M) e início de w)
        return ''.join(self.fita1[:3]) == '000' and '000' in ''.join(self.fita1[3:])


    def move_right_indefinitely(self, head):
        while True:
            head += 1

    def copy_w_to_fita3(self):
        # Encontrar o índice onde começa 'w' (após a última sequência '000')
        r_m_end_index = ''.join(self.fita1).rfind('000') + 3
        
        # Copiar cada símbolo de 'w' (após r_m_end_index) para a fita 3
        self.fita3 = self.fita1[r_m_end_index:]


    def read_fita2(self):
        return self.fita2[self.head2]

    def read_fita3(self):
        return self.fita3[self.head3]

    def find_transition(self, state_code, symbol_read):
        # Procurar na fita 1 pela sequência que codifica a transição:
        # state_code + '0' + symbol_read + ...
        encoded_transition = state_code + '0' + symbol_read

        fita1_str = ''.join(self.fita1)
        transition_start = fita1_str.find(encoded_transition)
        
        if transition_start == -1:
            return None

        # Extrair a transição completa
        transition_end = fita1_str.find('00', transition_start)
        if transition_end == -1:
            transition_end = len(fita1_str)
        
        return fita1_str[transition_start:transition_end]


    def apply_transition(self, transition):
        parts = transition.split('0')

        # Atualizar fita 2 com o novo estado
        self.fita2[self.head2] = parts[2]  # Novo estado
        
        # Escrever o novo símbolo na fita 3
        self.fita3[self.head3] = parts[3]  # Novo símbolo
        
        # Mover a cabeça da fita 3 conforme a direção
        if parts[4] == '1':  # Movimento à esquerda
            self.head3 = max(0, self.head3 - 1)
        elif parts[4] == '11':  # Movimento à direita
            self.head3 += 1
            if self.head3 >= len(self.fita3):
                self.fita3.append('B')  # Expandir fita 3 se necessário

if __name__ == '__main__':
    input_file = 'descricao_mt.json'
    encoded_representation = process_turing_machine(input_file)
    print(encoded_representation)

    input_string = '11111' # Exemplo de entrada
    mtu = TuringMachine(encoded_representation, input_string)
    mtu.simulate()
