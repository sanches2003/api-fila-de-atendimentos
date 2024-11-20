from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI()

# Modelo de cliente
class Cliente(BaseModel):
    nome: str = Field(..., max_length=20)  # Nome obrigatório, máximo 20 caracteres
    tipo_atendimento: str = Field(..., pattern="^[NP]$")  # Apenas 'N' ou 'P'

# Estrutura de dados para a fila
fila = []

# Endpoint GET /fila - Listar clientes na fila
@app.get("/fila")
async def listar_fila():
    # Filtrar apenas clientes que ainda não foram atendidos
    fila_nao_atendida = [cliente for cliente in fila if not cliente["atendido"]]
    return fila_nao_atendida

# Endpoint GET /fila/{id} - Consultar cliente por ID
@app.get("/fila/{id}")
async def consultar_cliente(id: int):
    if id < 0 or id >= len(fila):
        raise HTTPException(status_code=404, detail="Cliente não encontrado na posição especificada.")
    cliente = fila[id]
    return cliente

# Endpoint POST /fila - Adicionar cliente à fila
@app.post("/fila")
async def adicionar_cliente(cliente: Cliente):
    novo_cliente = {
        "id": len(fila),  # ID baseado no tamanho atual da fila
        "nome": cliente.nome,
        "tipo_atendimento": cliente.tipo_atendimento,
        "data_chegada": datetime.now(),
        "atendido": False
    }
    fila.append(novo_cliente)
    return {"message": "Cliente adicionado com sucesso!", "cliente": novo_cliente}

# Endpoint PUT /fila - Atualizar a fila (marcar o cliente na posição 1 como atendido)
@app.put("/fila")
async def atualizar_fila():
    for cliente in fila:
        if cliente["id"] > 0:  # Atualizar posição dos clientes
            cliente["id"] -= 1
        elif cliente["id"] == 0:  # Marcar o cliente na posição 0 como atendido
            cliente["atendido"] = True
    return {"message": "Fila atualizada com sucesso!", "fila": fila}

# Endpoint DELETE /fila/{id} - Remover cliente da fila
@app.delete("/fila/{id}")
async def remover_cliente(id: int):
    if id < 0 or id >= len(fila):
        raise HTTPException(status_code=404, detail="Cliente não encontrado na posição especificada.")
    fila.pop(id)  # Remover cliente
    # Atualizar IDs dos clientes restantes
    for idx, cliente in enumerate(fila):
        cliente["id"] = idx
    return {"message": "Cliente removido com sucesso!", "fila": fila}
