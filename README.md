# Teste Técnico - Pleno - Ecommerce
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.0-blue)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange)](./LICENSE)

 - Projeto desenvolvido para a vaga da Mercafácil
- # Sumário
    - [Arquitetura](#arquitetura)
    - [Como Executar?](#como-executar)
        - [Environment Variables](#environment-variables)
        - [No terminal](#no-terminal)
        - [Executando com docker](#executando-com-docker)
    - [Exemplos](#exemplos)
        - [Product endpoints](#product-endpoints)
        - [Order Endpoints](#order-endpoints)
    - [Executando os testes](#executando-os-testes)
    - [Licença](#-licença)

## Arquitetura
 - O projeto foi desenvolvido seguindo o padrão MVC(Model, View, Controller).
 - Bibliotecas utilizadas:
    - FastAPI
        - TestClient (utilizado para realizar os testes dos endpoints juntamente ao pytest)
    - SQLModel (Uma versão otimizada do SQLAlchemy para o FastAPI)
    - Pytest (Para execução dos testes)
    - Uvicorn (servidor ASGI)
    - toml (Utilizado para a leitura do toml e manter a versão de acordo com o arquivo)
    - python-dotenv (Carregamento de arquivos .env )
 - Para simular o processamento de pedidos, o sistema possui um worker. Esse worker é uma funçao que altera o status do pedido seguindo a ordem (pending → processing → completed), todos os pedidos são colocados dentro de uma Queue que é consumida até o fim pelo worker. Quando a fila está vazia o worker se encerra, mas volta a ser criado no momento em que um novo pedido é adicionado
 - As pastas do projeto são:
  - [app](./app/): pasta da API
    - [controller](./app/controller/): pasta das rotas responsáveis por realizar o controle da aplicação
        - [log.py](./app/controller/log.py): neste arquivo encontra-se toda a configuração do middleware de logs
        - [order.py](./app/controller/order.py): neste arquivo encontra-se todos os endpoints referente aos pedidos
        - [product.py](./app/controller/product.py): neste arquivo encontra-se todos os endpoints referente aos produtos
        - [worker.py](./app/controller/worker.py): neste arquivo encontra-se a configuraçao do worker utilizando Process e Queue
    - [model](./app/model/): pasta com as models e configuraçoes do banco de dados
        - [models.py](./app/model/models.py): neste arquivo encontra-se todas as models, incluindo as que são utilizadas apenas para entrada e saida de dados quanto as tabelas do banco
        - [database.py](./app/model/database.py): neste arquivo se encontra as configuraçoes da conexão com o banco de dados
    - [main.py](./app/main.py): arquivo com a criação da API incluindo as rotas.
 - [Dockerfile](./Dockerfile): arquivo para criação da imagem Docker
    

## Como executar?
 - O projeto pode ser executado diretamente do terminal ou através de container docker.
 - Antes de executar o projeto, duplique o arquivo [.env.sample](.env.sample) para um arquivo chamado .env.
   
   ### **Environment Variables**
    - Para a execução do projeto é necessário definir algumas variáveis no arquivo .env, conforme o .env.sample, abaixo segue a descriçao de cada uma:
     - **PYTHONPATH**: caminho do projeto, por padrao deve ser apenas ".", a alteraçao dessa variavel pode afetar a execuçao dos testes.

     - **SQL_URL**: url de conexão com o banco, no momento o projeto foi desenvolvido utilizando apenas o SQLite, para a utilização de outros bds, pode ser necessaria instalaçoes de dependencias adicionais.

     - **SQL_TEST_URL**: url de conexão com o banco para a execução dos testes.         

     - **LOG_LEVEL** : nivel do log. Todos os logs de requisição e de resposta sao inseridos no banco, a alteraçao no level do log altera apenas o que será mostrado no terminal. Se estiver como INFO apenas informaçoes básicas como metodo, caminho e status code serão mostradas no terminal, caso esteja como DEBUG será mostrado todas as informações sobre requisição e sobre resposta.

     - **ENV**: Tipo de execução, podendo ser DEV ou PROD. EM caso de DEV o banco utilizado sera o presente na variavel **SQL_TEST_URL**, em caso de PROD será utilizado **SQL_URL**.

   ### **No terminal**:
    - Primeiramente será necessário ter a versão 3.10 ou superior do Python.
    - Com o python instalado, em seu terminal execute a instalação do Poetry para o gerenciamento e de dependencias:
        ```bash
        pip install poetry
        ```
    - Agora que você ja tem o poetry instalado, pode executar a instalaçao das dependencias e criação do virtual environment executando o comando a seguir:
        ```bash  
        poetry install
        ```
    - Inicie o server:
        ```bash  
        poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ```
    - Em seu navegador abra a [documentação da API em http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
    - Para mais informações sobre como utilizar o Poetry, visite este [link](https://python-poetry.org/docs/basic-usage/).

   ### **Executando com docker**
    - Crie a imagem Docker:
        ```bash
        docker build --pull --rm -f "Dockerfile" -t ecommerce_api_image:latest "."
        ```
    - Execute o container:
        ```bash
        docker run -dti -p 8000:8000 --env-file .env  --name ecommerce_api ecommerce_api_image 
        ```
    - Abra a documentação em seu navegador [API Documentation](http://127.0.0.1:8000/docs)

## Exemplos:
 - Abaixo segue exemplos de execução com curl para cada método.Todos métodos possuem validação dos dados enviados através do Pydantic:
    ### **Product Endpoints**:
      - **Get list [/products/]**: retorna a lista de produtos cadastrado
        ```bash
        curl -X 'GET' 'http://127.0.0.1:8000/products/' -H 'accept: application/json'
        ```
        ```json
            [
                {
                    "category": "Food",
                    "price": 10,
                    "description": "Potato chips",
                    "stock": 50,
                    "name": "Lays",
                    "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf"
                },
                {
                    "category": "Video Game",
                    "price": 2200,
                    "description": "Microsoft Console",
                    "stock": 10,
                    "name": "Xbox Series S",
                    "id": "b1954e1f-70fa-4de1-83d2-d29e913f73fd"
                }
                ]
        ```

    - **Get id [/products/{id}]**: retorna um produto especifico:
        ```bash
        curl -X 'GET' \
        'http://127.0.0.1:8000/products/7e531cb2-2b06-471e-bed9-aaa9cd343ccf' \
        -H 'accept: application/json'
        ```
        
        ```json
        {
            "category": "Food",
            "price": 10,
            "description": "Potato chips",
            "stock": 50,
            "name": "Lays",
            "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf"
        }
        ```
     - **Post [/products/]**: insere um produto no banco, o campo id é gerado automaticamente e não deve ser passado
        ```bash
        curl -X 'POST' \
        'http://127.0.0.1:8000/products/' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
                    "name": "Lays",
                    "description": "Potato chips",
                    "price": 10,
                    "stock": 50,
                    "category": "Food"
                }'
        ```
        
        ```json
            {
            "category": "Food",
            "price": 10,
            "description": "Potato chips",
            "stock": 50,
            "name": "Lays",
            "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf"
            }
        ```
     - **Put [/products/{id}]**: atualiza um produto no banco e retorna o objeto atualizado. Deve ser passado o id no path. 
        ```bash
        curl -X 'PUT' \
        'http://127.0.0.1:8000/products/7e531cb2-2b06-471e-bed9-aaa9cd343ccf' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
            "category": "Food",
            "price": 10,
            "description": "Potato chips",
            "stock": 60,
            "name": "Lays"
            
        }'
        ```
        
        ```json
        {
            "price": 10,
            "category": "Food",
            "description": "Potato chips",
            "stock": 60,
            "name": "Lays",
            "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf"
        }
        ```
        **Delete [/product/{id}]**: deleta um produto no banco e retorna o objeto deletado.
         ```bash
         curl -X 'DELETE' \
        'http://127.0.0.1:8000/products/baeab11e-595f-4040-94d7-052852435ff9' \
        -H 'accept: application/json'
         ```
        
        ```json
        {
            "price": 10,
            "description": "Potato chips",
            "category": "Food",
            "stock": 60,
            "name": "Elma Chips",
            "id": "baeab11e-595f-4040-94d7-052852435ff9"
        }
        ```
    ### **Order Endpoints**:

    - **Get list [/orders/]**: retorna a lista com os ultimos 20 pedidos cadastrados:
        ```bash
            curl -X 'GET' \
        'http://127.0.0.1:8000/orders/' \
        -H 'accept: application/json'
         ```
        
        ```json
        [
            {
                "order_id": "3664b1b5-e048-402f-afb2-b519dccbeebe",
                "customer_id": "cust345",
                "products": [
                {
                    "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf",
                    "quantity": 10,
                    "price": 10
                }
                ],
                "total_amount": 100,
                "status": "completed",
                "created_at": "2025-07-16T16:04:01Z"
            },
            {
                "order_id": "88f8983b-a997-4f89-bdbf-9539cd22ae3f",
                "customer_id": "cust123",
                "products": [
                {
                    "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf",
                    "quantity": 3,
                    "price": 10
                }
                ],
                "total_amount": 30,
                "status": "completed",
                "created_at": "2025-07-16T16:01:41Z"
            }
        ]
        ```
    - **Get id [/orders/{id}]**: retorna um pedido específico:
        ```bash
        curl -X 'GET' \
        'http://127.0.0.1:8000/orders/3664b1b5-e048-402f-afb2-b519dccbeebe' \
        -H 'accept: application/json'
         ```
        
        ```json
        {
            "order_id": "3664b1b5-e048-402f-afb2-b519dccbeebe",
            "customer_id": "cust345",
            "products": [
                {
                "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf",
                "quantity": 10,
                "price": 10
                }
            ],
            "total_amount": 100,
            "status": "completed",
            "created_at": "2025-07-16T16:04:01Z"
        }
        ```
    - **Post [/orders/]**: insere um novo pedido. Todo pedido inserido altera a quantidade de produtos no estoque. Não deve ser passado o valor do produto, o total da compra, o id do pedido, status e a data de criação, o valor do produto sera salvo juntamente com o pedido, sendo assim a alteraçao no valor do produto não ira alterar o valor em um pedido já criado, apenas nos pedidos futuros, os demais valores são calculados dentro do sistema. Todo pedido inserido é adicionado a uma fila que executa um processamento alterando o status do pedido. No momento essa fila apenas simula um processamento e altera no banco os status na seguinte ordem (pending → processing → completed)
        ```bash
        curl -X 'POST' \
        'http://127.0.0.1:8000/orders/' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
                "customer_id": "cust123",
                "products": [{"id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf", "quantity": 3}]
            }'
         ```
        ```json
        {
            "order_id": "88f8983b-a997-4f89-bdbf-9539cd22ae3f",
            "customer_id": "cust123",
            "products": [
                {
                "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf",
                "quantity": 3,
                "price": 10
                }
            ],
            "total_amount": 30,
            "status": "pending",
            "created_at": "2025-07-16T16:01:41Z"
        }
        ```
    - **Put [/orders/{id}]**: atualiza um pedido no banco bem como atualiza o estoque dos produtos adicionados,removidos  e/ou alterados do pedido.
        ```bash
        curl -X 'PUT' \
        'http://127.0.0.1:8000/orders/3664b1b5-e048-402f-afb2-b519dccbeebe' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
                "customer_id": "cust345",
                "products": [{"id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf", "quantity": 8}]
            }'
        ```

        ```json
        {
            "order_id": "3664b1b5-e048-402f-afb2-b519dccbeebe",
            "customer_id": "cust345",
            "products": [
                {
                "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf",
                "quantity": 8,
                "price": 10
                }
            ],
            "total_amount": 80,
            "status": "completed",
            "created_at": "2025-07-16T16:04:01Z"
        }
        ```
    - **Delete [/orders/{id}]**: deleta um pedido do banco e retorna o pedido deletado.
        ```bash
        curl -X 'DELETE' \
        'http://127.0.0.1:8000/orders/da7afd14-6c1e-4a92-8b91-80fd96bf4f2e' \
        -H 'accept: application/json'
        ```
        
        ```json
        {
            "order_id": "da7afd14-6c1e-4a92-8b91-80fd96bf4f2e",
            "customer_id": "cust345",
            "products": [
                {
                "id": "7e531cb2-2b06-471e-bed9-aaa9cd343ccf",
                "quantity": 10,
                "price": 10
                }
            ],
            "total_amount": 100,
            "status": "completed",
            "created_at": "2025-07-16T16:15:27Z"
        }
        ```
## Executando os testes:
 - Todos os endpoints disponíves possuem testes automatizados que podem ser encontrados dentro da pasta [tests](./tests/controller/)
 - Para a execução dos testes é necessário primeiro a instalação das dependencias, veja na sessão "Como Executar?".
 - Após ter instalado o poetry e as dependencias do projeto execute conforme abaixo em seu terminal para executar todos os testes:
  ```bash
  poetry run pytest --cache-clear
  ```
 - Para executar apenas os testes do endpoint product execute:
  ```bash
  pytest --cache-clear tests/controller/test_controller_product.py
  ```

 - Para executar apenas os testes do endpoint order execute. Os testes do endpoint order levam mais tempo pois realizam a validação do worker e da busca por no maximo 20 ultimos pedidos validando a data também:
  ```bash
  pytest --cache-clear tests/controller/test_controller_order.py
  ```
## 📄 Licença
- Este projeto esta sobre a licença [Apache 2.0 License](./LICENSE).