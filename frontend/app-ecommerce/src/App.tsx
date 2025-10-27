import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// --- 1. DEFINIÇÃO DE TIPOS ---

// Tipo para o PRODUTO (do ms-catalogo)
interface Produto {
  id: number;
  nome: string;
  descricao: string;
  preco: number;
  imagem_url: string;
}

// Tipo para o ITEM DENTRO DO CARRINHO (do ms-carrinho)
interface ItemCarrinho {
  id: number;
  user_id: string;
  produto_id: number;
  nome_produto: string;
  preco_produto: number;
  quantidade: number;
  imagem_url: string | null;
}

// Tipo para o CARRINHO COMPLETO (resposta do ms-carrinho)
interface Carrinho {
  user_id: string;
  items: ItemCarrinho[];
  valor_total: number;
}

// Tipo para o PAYLOAD de adição (o que enviamos para o ms-carrinho)
interface ItemCreatePayload {
  produto_id: number;
  nome_produto: string;
  preco_produto: number;
  quantidade: number;
  imagem_url: string | null;
}

// --- 2. CONFIGURAÇÃO ---
// Para um projeto real, isso viria de um login, mas aqui vamos "chumbar"
const USER_ID = "gabriela_demo_user";

// --- 3. COMPONENTE PRINCIPAL ---
function App() {
  // --- Estados do Catálogo ---
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [loadingProdutos, setLoadingProdutos] = useState(true);

  // --- Estados do Carrinho ---
  const [carrinho, setCarrinho] = useState<Carrinho | null>(null);
  const [loadingCarrinho, setLoadingCarrinho] = useState(true);
  
  // --- Estado de Erro ---
  const [error, setError] = useState<string | null>(null);

  // --- API Endpoints ---
  const API_GATEWAY_URL = "http://localhost:8080";
  const CATALOGO_API = `${API_GATEWAY_URL}/api/catalogo`;
  const CARRINHO_API = `${API_GATEWAY_URL}/api/carrinho/${USER_ID}`;


  // --- 4. FUNÇÕES DE BUSCA DE DADOS (useEffect) ---

  // Efeito para buscar o Catálogo de Produtos
  useEffect(() => {
    const fetchProdutos = async () => {
      try {
        const response = await axios.get(`${CATALOGO_API}/produtos/`);
        setProdutos(response.data);
      } catch (err) {
        console.error("Erro ao buscar produtos:", err);
        setError("Falha ao carregar o catálogo.");
      } finally {
        setLoadingProdutos(false);
      }
    };
    fetchProdutos();
  }, [CATALOGO_API]);

  // Efeito para buscar o Carrinho do Usuário
  // (Vamos criar uma função separada para poder chamá-la de novo)
  const fetchCarrinho = async () => {
    setLoadingCarrinho(true);
    try {
      const response = await axios.get(CARRINHO_API);
      setCarrinho(response.data);
    } catch (err) {
      // Se der 404 (carrinho não existe), criamos um carrinho vazio localmente
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        setCarrinho({ user_id: USER_ID, items: [], valor_total: 0.0 });
      } else {
        console.error("Erro ao buscar carrinho:", err);
        setError("Falha ao carregar o carrinho.");
      }
    } finally {
      setLoadingCarrinho(false);
    }
  };

  // Busca o carrinho na primeira vez que o app carrega
  useEffect(() => {
    fetchCarrinho();
  }, [CARRINHO_API]); // Depende do USER_ID (via CARRINHO_API)


  // --- 5. FUNÇÕES DE AÇÃO (Carrinho) ---

  // Função para ADICIONAR ou ATUALIZAR um item no carrinho
  const handleAddToCart = async (produto: Produto) => {
    // 1. Verifica se o item já está no carrinho
    const itemExistente = carrinho?.items.find(
      (item) => item.produto_id === produto.id
    );
    
    // 2. Define a nova quantidade
    const novaQuantidade = itemExistente ? itemExistente.quantidade + 1 : 1;

    // 3. Cria o payload (dados) para enviar à API
    const payload: ItemCreatePayload = {
      produto_id: produto.id,
      nome_produto: produto.nome,
      preco_produto: produto.preco,
      quantidade: novaQuantidade,
      imagem_url: produto.imagem_url
    };

    try {
      // 4. Envia o POST para o ms-carrinho (endpoint de "adicionar_item")
      // Este endpoint (como fizemos) já lida com "criar" ou "atualizar"
      const response = await axios.post(CARRINHO_API, payload);
      
      // 5. Atualiza o estado local do carrinho com a resposta da API
      setCarrinho(response.data);

    } catch (err) {
      console.error("Erro ao adicionar item:", err);
      setError("Não foi possível adicionar o item ao carrinho.");
    }
  };

  // Função para REMOVER um item do carrinho
  const handleRemoveFromCart = async (produto_id: number) => {
    try {
      // 1. Envia o DELETE para o ms-carrinho
      const response = await axios.delete(`${CARRINHO_API}/${produto_id}`);
      
      // 2. Atualiza o estado local do carrinho
      setCarrinho(response.data);

    } catch (err) {
      console.error("Erro ao remover item:", err);
      setError("Não foi possível remover o item do carrinho.");
    }
  };

  // --- 6. RENDERIZAÇÃO (JSX) ---
  return (
    <div className="app-layout"> {/* Layout dividido em 2 colunas */}
      
      {/* --- COLUNA DO CATÁLOGO --- */}
      <main className="catalogo-container">
        <h1>💖 Catálogo de Labubus 💖</h1>
        
        {loadingProdutos && <p className="loading-message">Carregando catálogo...</p>}
        {error && <p className="error-message">{error}</p>}
        
        <div className="catalogo-grid">
          {produtos.map(produto => (
            <div className="produto-card" key={produto.id}>
              <img 
                src={produto.imagem_url} 
                alt={produto.nome} 
                className="produto-imagem"
              />
              <div className="produto-info">
                <h2>{produto.nome}</h2>
                <p className="produto-descricao">{produto.descricao}</p>
                <div className="produto-footer">
                  <p className="produto-preco">R$ {produto.preco.toFixed(2)}</p>
                  {/* Botão para adicionar ao carrinho */}
                  <button 
                    className="add-to-cart-btn"
                    onClick={() => handleAddToCart(produto)}
                  >
                    Adicionar 🛒
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* --- COLUNA DO CARRINHO --- */}
      <aside className="carrinho-container">
        <h2>Meu Carrinho 🛍️</h2>
        
        {loadingCarrinho && <p>Carregando carrinho...</p>}
        
        {!loadingCarrinho && carrinho && carrinho.items.length === 0 && (
          <p>Seu carrinho está vazio.</p>
        )}

        {!loadingCarrinho && carrinho && carrinho.items.length > 0 && (
          <>
            <div className="carrinho-lista">
              {carrinho.items.map(item => (
                <div className="carrinho-item" key={item.produto_id}>
                  <img src={item.imagem_url || ''} alt={item.nome_produto} />
                  <div className="carrinho-item-info">
                    <p className="item-nome">{item.nome_produto}</p>
                    <p className="item-preco">
                      {item.quantidade} x R$ {item.preco_produto.toFixed(2)}
                    </p>
                  </div>
                  <button 
                    className="remove-item-btn"
                    onClick={() => handleRemoveFromCart(item.produto_id)}
                  >
                    &times;
                  </button>
                </div>
              ))}
            </div>
            
            <div className="carrinho-total">
              <h3>Total:</h3>
              <p>R$ {carrinho.valor_total.toFixed(2)}</p>
            </div>
          </>
        )}
      </aside>

    </div>
  )
}

export default App