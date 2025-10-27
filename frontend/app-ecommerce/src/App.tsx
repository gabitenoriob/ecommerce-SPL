import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// --- Tipos (Interfaces) ---
// (Cole as mesmas interfaces que definimos antes: 
// Produto, ItemCarrinho, Carrinho, ItemCreatePayload)
interface Produto {
  id: number;
  nome: string;
  descricao: string;
  preco: number;
  imagem_url: string;
}
interface ItemCarrinho {
  id: number;
  user_id: string;
  produto_id: number;
  nome_produto: string;
  preco_produto: number;
  quantidade: number;
  imagem_url: string | null;
}
interface Carrinho {
  user_id: string;
  items: ItemCarrinho[];
  valor_total: number;
}
interface ItemCreatePayload {
  produto_id: number;
  nome_produto: string;
  preco_produto: number;
  quantidade: number;
  imagem_url: string | null;
}

// --- API Endpoints ---
const API_GATEWAY_URL = "http://localhost:8888";
const CATALOGO_API = `${API_GATEWAY_URL}/api/catalogo`;

// --- Componente Principal ---
function App() {
  // --- 1. ESTADO DE AUTENTICAÇÃO ---
  // O usuário começa "deslogado"
  const [userId, setUserId] = useState<string | null>(null); 
  // Estado para o campo de input
  const [usernameInput, setUsernameInput] = useState("");

  // --- Estados do Catálogo ---
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [loadingProdutos, setLoadingProdutos] = useState(true);

  // --- Estados do Carrinho ---
  const [carrinho, setCarrinho] = useState<Carrinho | null>(null);
  const [loadingCarrinho, setLoadingCarrinho] = useState(true);
  
  // --- Estado de Erro ---
  const [error, setError] = useState<string | null>(null);

  // --- 2. EFEITOS (useEffect) ---
  
  // Este efeito roda QUANDO o userId MUDAR (ou seja, depois do login)
  useEffect(() => {
    // Só busca os dados SE o usuário estiver logado
    if (userId) {
      console.log(`Usuário ${userId} logado. Buscando dados...`);
      
      const fetchProdutos = async () => {
        setLoadingProdutos(true);
        try {
          const response = await axios.get(`${CATALOGO_API}/produtos/`);
          setProdutos(response.data);
        } catch (err) {
          setError("Falha ao carregar o catálogo.");
        } finally {
          setLoadingProdutos(false);
        }
      };

      const fetchCarrinho = async () => {
        setLoadingCarrinho(true);
        // Constroi a URL da API do carrinho DINAMICAMENTE
        const CARRINHO_API_URL = `${API_GATEWAY_URL}/api/carrinho/${userId}`;
        try {
          const response = await axios.get(CARRINHO_API_URL);
          setCarrinho(response.data);
        } catch (err) {
          setCarrinho({ user_id: userId, items: [], valor_total: 0.0 });
        } finally {
          setLoadingCarrinho(false);
        }
      };

      fetchProdutos();
      fetchCarrinho();
    }
  }, [userId]); // <- A "mágica": só roda quando o userId for definido

  
  // --- 3. FUNÇÕES DE AÇÃO ---

  // Função do nosso "Login Falso"
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault(); // Impede o refresh da página
    if (usernameInput.trim()) {
      setUserId(usernameInput.trim()); // Define o usuário
    }
  };

  // Função para ADICIONAR item (agora usa o 'userId' do estado)
  const handleAddToCart = async (produto: Produto) => {
    if (!userId) return; // Segurança: não faz nada se não tiver logado

    const CARRINHO_API_URL = `${API_GATEWAY_URL}/api/carrinho/${userId}`;
    const itemExistente = carrinho?.items.find((item) => item.produto_id === produto.id);
    const novaQuantidade = itemExistente ? itemExistente.quantidade + 1 : 1;
    
    const payload: ItemCreatePayload = {
      produto_id: produto.id,
      nome_produto: produto.nome,
      preco_produto: produto.preco,
      quantidade: novaQuantidade,
      imagem_url: produto.imagem_url
    };

    try {
      const response = await axios.post(CARRINHO_API_URL, payload);
      setCarrinho(response.data);
    } catch (err) {
      setError("Não foi possível adicionar o item.");
    }
  };

  // Função para REMOVER item (agora usa o 'userId' do estado)
  const handleRemoveFromCart = async (produto_id: number) => {
    if (!userId) return; // Segurança

    const CARRINHO_API_URL = `${API_GATEWAY_URL}/api/carrinho/${userId}`;
    try {
      const response = await axios.delete(`${CARRINHO_API_URL}/${produto_id}`);
      setCarrinho(response.data);
    } catch (err) {
      setError("Não foi possível remover o item.");
    }
  };

  // --- 4. RENDERIZAÇÃO CONDICIONAL ---

  // SEÇÃO 1: TELA DE LOGIN (se não há userId)
  if (!userId) {
    return (
      <div className="login-container">
        <form onSubmit={handleLogin}>
          <h1>Bem-vindo(a) à Loja Labubu</h1>
          <p>Digite um nome de usuário para começar:</p>
          <input 
            type="text" 
            placeholder="ex: gabriela"
            value={usernameInput}
            onChange={(e) => setUsernameInput(e.target.value)}
          />
          <button type="submit">Entrar</button>
        </form>
      </div>
    );
  }

  // SEÇÃO 2: A LOJA (se JÁ TEM userId)
  return (
    <div className="app-layout">      
      {/* --- COLUNA DO CATÁLOGO --- */}
      <main className="catalogo-container">
        <h1>💖 Catálogo 💖</h1>
        
        {loadingProdutos && <p className="loading-message">Carregando catálogo...</p>}
        {error && <p className="error-message">{error}</p>}
        
        <div className="catalogo-grid">
          {produtos.map(produto => (
            <div className="produto-card" key={produto.id}>
              {/* (O JSX do card é igual ao de antes) */}
              <img src={produto.imagem_url} alt={produto.nome} className="produto-imagem"/>
              <div className="produto-info">
                <h2>{produto.nome}</h2>
                <p className="produto-descricao">{produto.descricao}</p>
                <div className="produto-footer">
                  <p className="produto-preco">R$ {produto.preco.toFixed(2)}</p>
                  <button className="add-to-cart-btn" onClick={() => handleAddToCart(produto)}>
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
        
        {carrinho && carrinho.items.length === 0 && <p>Seu carrinho está vazio.</p>}

        {carrinho && carrinho.items.length > 0 && (
          <>
            <div className="carrinho-lista">
              {carrinho.items.map(item => (
                <div className="carrinho-item" key={item.produto_id}>
                  {/* (O JSX do item é igual ao de antes) */}
                  <img src={item.imagem_url || ''} alt={item.nome_produto} />
                  <div className="carrinho-item-info">
                    <p className="item-nome">{item.nome_produto}</p>
                    <p className="item-preco">{item.quantidade} x R$ {item.preco_produto.toFixed(2)}</p>
                  </div>
                  <button className="remove-item-btn" onClick={() => handleRemoveFromCart(item.produto_id)}>
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