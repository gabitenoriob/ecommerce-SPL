import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// --- 1. DEFINIÇÃO DE TIPOS ---
// (Cole as mesmas interfaces que definimos antes)
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

// --- NOVOS TIPOS PARA O FRETE ---
interface OpcaoFrete {
  metodo: string;
  prazo_dias: number;
  valor: number;
}


// --- 2. API Endpoints ---
const API_GATEWAY_URL = "http://localhost:8888";
const CATALOGO_API = `${API_GATEWAY_URL}/api/catalogo`;
const FRETE_API = `${API_GATEWAY_URL}/api/frete`; // <-- NOVO

// --- 3. COMPONENTE PRINCIPAL ---
function App() {
  // --- Estados de Autenticação ---
  const [userId, setUserId] = useState<string | null>(null); 
  const [usernameInput, setUsernameInput] = useState("");

  // --- Estados do Catálogo ---
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [loadingProdutos, setLoadingProdutos] = useState(true);

  // --- Estados do Carrinho ---
  const [carrinho, setCarrinho] = useState<Carrinho | null>(null);
  const [loadingCarrinho, setLoadingCarrinho] = useState(true);
  
  // --- NOVOS ESTADOS DE FRETE ---
  const [cep, setCep] = useState(""); // O que o usuário digita
  const [opcoesFrete, setOpcoesFrete] = useState<OpcaoFrete[]>([]);
  const [freteSelecionado, setFreteSelecionado] = useState<OpcaoFrete | null>(null);
  const [loadingFrete, setLoadingFrete] = useState(false);
  
  // --- Estados Gerais ---
  const [error, setError] = useState<string | null>(null);

  // --- 4. EFEITOS (useEffect) ---
  
  // Efeito para buscar Catálogo e Carrinho (quando o userId muda)
  useEffect(() => {
    if (userId) {
      console.log(`Usuário ${userId} logado. Buscando dados...`);
      const CARRINHO_API_URL = `${API_GATEWAY_URL}/api/carrinho/${userId}`;

      const fetchProdutos = async () => {
        setLoadingProdutos(true);
        try {
          const response = await axios.get(`${CATALOGO_API}/produtos/`);
          setProdutos(response.data);
          setError(null);
        } catch (err) {
          setError("Falha ao carregar o catálogo.");
        } finally {
          setLoadingProdutos(false);
        }
      };

      const fetchCarrinho = async () => {
        setLoadingCarrinho(true);
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
  }, [userId]);

  // Efeito para limpar o frete se o carrinho mudar
  useEffect(() => {
    setOpcoesFrete([]);
    setFreteSelecionado(null);
  }, [carrinho]);

  
  // --- 5. FUNÇÕES DE AÇÃO ---

  // (handleLogin, handleAddToCart, handleRemoveFromCart - IGUAIS A ANTES)
  // ... (Cole as funções handleLogin, handleAddToCart, e handleRemoveFromCart aqui)
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (usernameInput.trim()) {
      setUserId(usernameInput.trim());
    }
  };

  const handleAddToCart = async (produto: Produto) => {
    if (!userId) return;
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

  const handleRemoveFromCart = async (produto_id: number) => {
    if (!userId) return;
    const CARRINHO_API_URL = `${API_GATEWAY_URL}/api/carrinho/${userId}`;
    try {
      const response = await axios.delete(`${CARRINHO_API_URL}/${produto_id}`);
      setCarrinho(response.data);
    } catch (err) {
      setError("Não foi possível remover o item.");
    }
  };

  // --- NOVA FUNÇÃO DE AÇÃO (Frete) ---
  const handleCalcularFrete = async () => {
    if (!cep.trim() || cep.replace("-", "").length !== 8) {
      alert("Por favor, digite um CEP válido com 8 dígitos.");
      return;
    }
    
    setLoadingFrete(true);
    setOpcoesFrete([]);
    setFreteSelecionado(null);
    setError(null);

    try {
      // 1. Chama o ms-frete via Gateway
      const response = await axios.post(`${FRETE_API}/calcular`, {
        cep: cep
      });
      
      // 2. Salva as opções no estado
      setOpcoesFrete(response.data.opcoes);

    } catch (err) {
      console.error("Erro ao calcular frete:", err);
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        setError("Nenhuma opção de entrega encontrada para este CEP.");
      } else {
        setError("Erro ao calcular o frete. Tente novamente.");
      }
    } finally {
      setLoadingFrete(false);
    }
  };


  // --- 6. RENDERIZAÇÃO CONDICIONAL ---

  // SEÇÃO 1: TELA DE LOGIN (Igual a antes)
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

  // SEÇÃO 2: A LOJA (JSX do carrinho foi MODIFICADO)
  
  // Cálculo do Total
  const subtotal = carrinho?.valor_total || 0;
  const valorFrete = freteSelecionado?.valor || 0;
  const totalGeral = subtotal + valorFrete;

  return (
    <div className="app-layout">      
      {/* --- COLUNA DO CATÁLOGO (Igual a antes) --- */}
      <main className="catalogo-container">
        <h1>💖 Catálogo 💖</h1>
        {loadingProdutos && <p className="loading-message">Carregando catálogo...</p>}
        {error && <p className="error-message">{error}</p>}
        <div className="catalogo-grid">
          {produtos.map(produto => (
            <div className="produto-card" key={produto.id}>
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

      {/* --- COLUNA DO CARRINHO (MODIFICADA) --- */}
      <aside className="carrinho-container">
        <h2>Meu Carrinho 🛍️</h2>
        
        {loadingCarrinho && <p>Carregando carrinho...</p>}
        
        {!loadingCarrinho && carrinho && carrinho.items.length === 0 && (
          <p>Seu carrinho está vazio.</p>
        )}

        {/* --- Lista de Itens (Igual) --- */}
        {!loadingCarrinho && carrinho && carrinho.items.length > 0 && (
          <div className="carrinho-lista">
            {carrinho.items.map(item => (
              <div className="carrinho-item" key={item.produto_id}>
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
        )}

        {/* --- Seção de Frete (NOVA) --- */}
        {/* Só mostra o frete se o carrinho não estiver vazio */}
        {!loadingCarrinho && carrinho && carrinho.items.length > 0 && (
          <div className="frete-container">
            <h4>Calcular Frete</h4>
            <div className="cep-input-group">
              <input 
                type="text" 
                placeholder="Digite seu CEP" 
                value={cep}
                onChange={(e) => setCep(e.target.value)}
                maxLength={9} // 00000-000
              />
              <button onClick={handleCalcularFrete} disabled={loadingFrete}>
                {loadingFrete ? "..." : "Calcular"}
              </button>
            </div>

            {/* Lista de Opções de Frete */}
            {opcoesFrete.length > 0 && (
              <div className="opcoes-frete-lista">
                {opcoesFrete.map(opcao => (
                  <div 
                    key={opcao.metodo} 
                    className={`opcao-frete-item ${freteSelecionado?.metodo === opcao.metodo ? 'selected' : ''}`}
                    onClick={() => setFreteSelecionado(opcao)}
                  >
                    <span className='metodo'>{opcao.metodo} ({opcao.prazo_dias} dias)</span>
                    <span className='valor'>R$ {opcao.valor.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* --- Total (MODIFICADO) --- */}
        {carrinho && (
          <div className="carrinho-total">
            <div className='total-linha'>
              <span>Subtotal:</span>
              <span>R$ {subtotal.toFixed(2)}</span>
            </div>
            
            {/* Só mostra o frete se tiver um selecionado */}
            {freteSelecionado && (
              <div className='total-linha frete'>
                <span>Frete ({freteSelecionado.metodo}):</span>
                <span>R$ {valorFrete.toFixed(2)}</span>
              </div>
            )}

            <div className='total-linha geral'>
              <span>Total:</span>
              <span>R$ {totalGeral.toFixed(2)}</span>
            </div>
          </div>
        )}

      </aside>
    </div>
  )
}

export default App