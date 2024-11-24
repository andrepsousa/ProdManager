
# ProdManager API

ProdManager é uma API RESTful desenvolvida com Python e Flask para o gerenciamento de produtos, permitindo operações CRUD (Create, Read, Update, Delete).

## Tecnologias Utilizadas

- Python 3.12
- Flask
- Flask-JWT-Extended
- SQLAlchemy
- SQLite

## Endpoints

### Listar todos os produtos
**GET** `/produtos`  
Retorna uma lista com todos os produtos.

### Consultar produto por ID
**GET** `/produtos/<int:id_product>`  
Retorna os detalhes de um produto específico.

### Criar um novo produto
**POST** `/produtos`  
**Body (JSON):**
```json
{
  "name": "Product Name",
  "price": 10.99,
  "description": "Product Description"
}
```

### Atualizar um produto
**PUT** `/produtos/<int:id_product>`  
**Body (JSON):**
```json
{
  "name": "Updated Product Name",
  "price": 15.99,
  "description": "Updated Product Description"
}
```

### Deletar um produto
**DELETE** `/produtos/<int:id_product>`  

## Configuração do Ambiente

1. Clone o repositório:
   ```bash
   git clone https://github.com/andrepsousa/ProdManager.git
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente no arquivo `.env`:
   ```env
   DATABASE_URL=sqlite:///produtos.db
   JWT_SECRET_KEY=sua_chave_secreta
   ```

5. Execute a aplicação:
   ```bash
   flask run
   ```


## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).