#Giovanni Minari Zanetti - 202014280
#OS - Windows
#IDE - Visual Studio Code

import resources

pc = 0x00000000
ri = 0x00000000
registers = resources.np.zeros(32, dtype=resources.np.int32)
registers[2] = 0x00003ffc
registers[3] = 0x00001800

def load_mem():
    it = 0
    with open('code.bin', 'rb') as file:
        code = file.read()
    with open('data.bin', 'rb') as file:
        data = file.read()
    for b in code:
        resources.sb(0, it, b)
        it += 1
        if it == 508:
            break
    it = 8192
    for b in data:
        resources.sb(0, it, b)
        it += 1
        if it == 12284:
            break
    return code, data

def geraImm(ri):
    ri32 = resources.np.int32(ri)
    if ri32 < 0:
        ri32 = ri32 & 0xFFFFFFFF
    return ri32

def fetch():
    global ri
    global pc
    ri = resources.lw(pc, 0)
    pc += 4
    return ri

def decode():
    global ri
    ri = geraImm(ri)
    opcode = ri & 0b1111111
    rs1 = (ri >> 15) & 0b11111
    rs2 = (ri >> 20) & 0b11111
    rd = (ri >> 7) & 0b11111
    shamt = (ri >> 20) & 0b11111
    funct3 = (ri >> 12) & 0b111
    funct7 = (ri >> 25) & 0b1111111
    imm12_i = (ri >> 20) & 0xFFF
    if len(bin(imm12_i)) == 14:     # Se nº de bits é 12, então o MSB tem que ser 1
        aux = imm12_i
        imm12_i = 0
        for i in range(2, len(bin(aux))):
            if i == 2:
                imm12_i += (-1)*2**(len(bin(aux))-(i+1))
            else:
                imm12_i += int(bin(aux)[i])*2**(len(bin(aux))-(i+1))
    imm12_s = ((ri >> 7) & 0x1F) + ((ri >> 20) & 0xFE0)
    if len(bin(imm12_s)) == 14:     # Se nº de bits é 12, então o MSB tem que ser 1
        aux = imm12_s
        imm12_s = 0
        for i in range(2, len(bin(aux))):
            if i == 2:
                imm12_s += (-1)*2**(len(bin(aux))-(i+1))
            else:
                imm12_s += int(bin(aux)[i])*2**(len(bin(aux))-(i+1))
    imm13 = ((ri >> 19) & 0x1000) + ((ri << 4) & 0x800) + ((ri >> 20) & 0x7E0) + ((ri >> 7) & 0x1E)
    if len(bin(imm13)) == 15:     # Se nº de bits é 13, então o MSB tem que ser 1
        aux = imm13
        imm13 = 0
        for i in range(2, len(bin(aux))):
            if i == 2:
                imm13 += (-1)*2**(len(bin(aux))-(i+1))
            else:
                imm13 += int(bin(aux)[i])*2**(len(bin(aux))-(i+1))
    imm20_u = ri & 0xFFFFF000
    imm21 = ((ri >> 11) & 0x100000) + (ri & 0xFF000) + ((ri >> 9) & 0x800) + ((ri >> 20) & 0x7FE)
    if len(bin(imm21)) == 23:     # Se nº de bits é 21, então o MSB tem que ser 1
        aux = imm21
        imm21 = 0
        for i in range(2, len(bin(aux))):
            if i == 2:
                imm21 += (-1)*2**(len(bin(aux))-(i+1))
            else:
                imm21 += int(bin(aux)[i])*2**(len(bin(aux))-(i+1))
    return [opcode, rs1, rs2, rd, shamt, funct3, funct7, imm12_i, imm12_s, imm13, imm20_u, imm21]

def execute(decoded):
    global ri
    global registers
    global pc
    opcode = decoded[0]
    rs1 = decoded[1]
    rs2 = decoded[2]
    rd = decoded[3]
    shamt = decoded[4]
    funct3 = decoded[5]
    funct7 = decoded[6]
    imm12_i = decoded[7]
    imm12_s = decoded[8]
    imm13 = decoded[9]
    imm20_u = decoded[10]
    imm21 = decoded[11]
    if ri == 0x00000073:
        #ecall
        ecall = 0
        if registers[17] == 1:
            ecall = registers[10]
            print(ecall, end="")
        elif registers[17] == 4:
            ecall = resources.mem[registers[10]]
            strit = registers[10]
            string = ""
            while resources.mem[strit] != 0:
                string += chr(resources.mem[strit])
                strit += 1
            print(string, end="")
        elif registers[17] == 10:
            ecall = "\nprogram is finished running (0)"
            print(ecall)
        return ecall
    if opcode == 0b0110111:
        #lui
        if rd != 0:
            registers[rd] = imm20_u
        return
    elif opcode == 0b0010111:
        #auipc
        if rd != 0:
            registers[rd] = (pc - 4) + imm20_u
        return
    elif opcode == 0b1101111:
        #jal
        if rd != 0:
            registers[rd] = pc
        pc += (imm21 - 4)
        return
    elif opcode == 0b1100111 and funct3 == 0b000:
        #jalr
        if rd != 0:
            registers[rd] = pc
        pc = registers[rs1] + imm12_s
        return
    elif opcode == 0b1100011 and funct3 == 0b000:
        #beq
        if registers[rs1] == registers[rs2]:
            pc += (imm12_s - 4)
        return
    elif opcode == 0b1100011 and funct3 == 0b001:
        #bne
        if registers[rs1] != registers[rs2]:
            pc += (imm12_s - 4)
        return
    elif opcode == 0b1100011 and funct3 == 0b100:
        #blt
        if registers[rs1] < registers[rs2]:
            pc += (imm12_s - 4)
        return
    elif opcode == 0b1100011 and funct3 == 0b101:
        #bge
        if registers[rs1] >= registers[rs2]:
            pc += (imm12_s - 4)
        return
    elif opcode == 0b1100011 and funct3 == 0b110:
        #bltu
        if registers[rs1] < resources.np.uint32(registers[rs2]):
            pc += (imm12_s - 4)
        return
    elif opcode == 0b1100011 and funct3 == 0b111:
        #bgeu
        if registers[rs1] >= resources.np.uint32(registers[rs2]):
            pc += (imm12_s - 4)
        return
    elif opcode == 0b0000011 and funct3 == 0b000:
        #lb
        if rd != 0:
            registers[rd] = resources.lb(registers[rs1], imm12_i)
        return rd
    elif opcode == 0b0000011 and funct3 == 0b010:
        #lw
        if rd != 0:
            registers[rd] = resources.lw(registers[rs1], imm12_i)
        return rd
    elif opcode == 0b0000011 and funct3 == 0b100:
        #lbu
        if rd != 0:
            registers[rd] = resources.np.uint32(resources.lbu(resources[rs1], imm12_i))
        return rd
    elif opcode == 0b0100011 and funct3 == 0b000:
        #sb
        resources.sb(registers[rs2], imm12_s, registers[rs1])
        return
    elif opcode == 0b0100011 and funct3 == 0b010:
        #sw
        resources.sw(registers[rs2], imm12_s, registers[rs1])
        return
    elif opcode == 0b0010011 and funct3 == 0b000:
        #addi
        if rd != 0:
            registers[rd] = registers[rs1] + imm12_i
        return
    elif opcode == 0b0010011 and funct3 == 0b110:
        #ori
        if rd != 0:
            registers[rd] = registers[rs1] | imm12_i
        return
    elif opcode == 0b0010011 and funct3 == 0b111:
        #andi
        if rd != 0:
            registers[rd] = registers[rs1] & imm12_i
        return
    elif opcode == 0b0010011 and funct3 == 0b001 and funct7 == 0b0000000:
        #slli
        if rd != 0:
            registers[rd] = registers[rs1] << shamt
        return
    elif opcode == 0b0010011 and funct3 == 0b101 and funct7 == 0b0000000:
        #srli
        if rd != 0:
            registers[rd] = registers[rs1] >> shamt
        return
    elif opcode == 0b0010011 and funct3 == 0b101 and funct7 == 0b0100000:
        #srai
        if rd != 0:
            registers[rd] = registers[rs1] >> shamt
            if registers[rd] < 0:
                registers[rd] = (1 << 32) + registers[rd]
        return
    elif opcode == 0b0110011 and funct3 == 0b000 and funct7 == 0b0000000:
        #add
        if rd != 0:
            registers[rd] = registers[rs1] + registers[rs2]
        return
    elif opcode == 0b0110011 and funct3 == 0b000 and funct7 == 0b0100000:
        #sub
        if rd != 0:
            registers[rd] = registers[rs1] - registers[rs2]
        return
    elif opcode == 0b0110011 and funct3 == 0b010 and funct7 == 0b0000000:
        #slt
        if rd != 0:
            if registers[rs1] < registers[rs2]:
                registers[rd] = 1
            else:
                registers[rd] = 0
        return
    elif opcode == 0b0110011 and funct3 == 0b011 and funct7 == 0b0000000:
        #sltu
        if rd != 0:
            if registers[rs1] < resources.np.uint32(registers[rs2]):
                registers[rd] = 1
            else:
                registers[rd] = 0
        return
    elif opcode == 0b0110011 and funct3 == 0b100 and funct7 == 0b0000000:
        #xor
        if rd != 0:
            registers[rd] = registers[rs1] ^ registers[rs2]
        return
    elif opcode == 0b0110011 and funct3 == 0b110 and funct7 == 0b0000000:
        #or
        if rd != 0:
            registers[rd] = registers[rs1] | registers[rs2]
        return
    elif opcode == 0b0110011 and funct3 == 0b111 and funct7 == 0b0000000:
        #and
        if rd != 0:
            registers[rd] = registers[rs1] & registers[rs2]
        return

def step():
    fetch()
    dec = decode()
    exe = execute(dec)
    print("t1", registers[6])
    print("zero", registers[0])
    if exe == "program is finished running (0)" or pc > 0x1F40:
        return "end"

def run():
    global pc
    global registers
    while pc <= 0x1F40:
        fetch()
        dec = decode()
        exe = execute(dec)
        if exe == "program is finished running (0)":
            return "end"
    return "end"

load_mem()
while True:
    simulator = ""
    print('1 - step')
    print('2 - run')
    inp = int(input())
    if inp == 1:
        simulator = step()
        if simulator == "end":
            break
    elif inp == 2:
        simulator = run()
        if simulator == "end":
            break
