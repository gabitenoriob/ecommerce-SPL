import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// --- 1. DEFINIÇÃO DE TIPOS ---
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

interface OpcaoFrete {
  metodo: string;
  prazo_dias: number;
  valor: number;
}

// --- NOVOS TIPOS PARA PEDIDOS E PAGAMENTO ---
interface ItemPedido {
  produto_id: number;
  nome_produto: string;
  preco_produto: number;
  quantidade: number;
  imagem_url: string | null;
}

interface Pedido {
  id: string; // ID do pedido
  user_id: string;
  items: ItemPedido[];
  valor_total: number;
  frete: OpcaoFrete;
  status: string; // ex: "Processando", "Concluído"
  data_pedido: string; // ISO string
}

interface PagamentoPayload {
  user_id: string;
  items: ItemCarrinho[];
  frete: OpcaoFrete;
  valor_total: number;
  status: string;
}

// Tipo para o estado de navegação
type ViewState = 'login' | 'loja' | 'recomendacoes' | 'pedidos' | 'pagamento';


// --- 2. API Endpoints ---
const API_GATEWAY_URL = "http://app.localhost:8888";
const CATALOGO_API = `${API_GATEWAY_URL}/api/catalogo`;
const FRETE_API = `${API_GATEWAY_URL}/api/frete`; 
// NOVOS ENDPOINTS
const PEDIDOS_API = `${API_GATEWAY_URL}/api/pedidos`;
const PAGAMENTO_API = `${API_GATEWAY_URL}/api/pagamentos`;
const RECOMENDACOES_API = `${API_GATEWAY_URL}/api/recomendacoes`;

// --- 3. COMPONENTE PRINCIPAL ---
function App() {
  // --- Estados de Navegação e Autenticação ---
  const [viewState, setViewState] = useState<ViewState>('login');
  const [userId, setUserId] = useState<string | null>(null); 
  const [usernameInput, setUsernameInput] = useState("");

  // --- Estados do Catálogo ---
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [loadingProdutos, setLoadingProdutos] = useState(true);

  // --- Estados do Carrinho ---
  const [carrinho, setCarrinho] = useState<Carrinho | null>(null);
  const [loadingCarrinho, setLoadingCarrinho] = useState(true);
  
  // --- Estados de Frete ---
  const [cep, setCep] = useState(""); // O que o usuário digita
  const [opcoesFrete, setOpcoesFrete] = useState<OpcaoFrete[]>([]);
  const [freteSelecionado, setFreteSelecionado] = useState<OpcaoFrete | null>(null);
  const [loadingFrete, setLoadingFrete] = useState(false);

  // --- NOVOS ESTADOS DE RECOMENDAÇÕES ---
  const [recomendacoes, setRecomendacoes] = useState<Produto[]>([]);
  const [loadingRecomendacoes, setLoadingRecomendacoes] = useState(true);

  // --- NOVOS ESTADOS DE PEDIDOS ---
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [loadingPedidos, setLoadingPedidos] = useState(true);

  // --- NOVOS ESTADOS DE PAGAMENTO ---
  const [loadingPagamento, setLoadingPagamento] = useState(false);
  const [dadosCartao, setDadosCartao] = useState({ numero: "", nome: "", validade: "", cvv: "" });
  
  // --- Estados Gerais ---
  const [error, setError] = useState<string | null>(null);

  // --- 4. EFEITOS (useEffect) ---
  
  // Efeito para buscar TODOS os dados (quando o userId muda)
  useEffect(() => {
    if (userId) {
      console.log(`Usuário ${userId} logado. Buscando dados...`);
      const CARRINHO_API_URL = `${API_GATEWAY_URL}/api/carrinho/${userId}`;
      const PEDIDOS_API_URL = `${PEDIDOS_API}/${userId}`;
      const RECOMENDACOES_API_URL = `${RECOMENDACOES_API}/${userId}`; // Recomendacoes por usuário

      const fetchData = async () => {
        // Resetar estados de loading
        setLoadingProdutos(true);
        setLoadingCarrinho(true);
        setLoadingRecomendacoes(true);
        setLoadingPedidos(true);
        setError(null);

        try {
          // Fazer chamadas em paralelo
          const [produtosRes, carrinhoRes, recomendacoesRes, pedidosRes] = await Promise.allSettled([
            axios.get(`${CATALOGO_API}/produtos/`),
            axios.get(CARRINHO_API_URL),
            axios.get(RECOMENDACOES_API_URL), // Agora é real
            axios.get(PEDIDOS_API_URL) // Agora é real
          ]);

          // Processar Produtos
          if (produtosRes.status === 'fulfilled') {
            setProdutos(produtosRes.value.data);
          } else {
            setError("Falha ao carregar o catálogo.");
            console.error("Erro produtos:", produtosRes.reason);
          }

          // Processar Carrinho
          if (carrinhoRes.status === 'fulfilled') {
            setCarrinho(carrinhoRes.value.data);
          } else {
            // Assumir carrinho vazio se falhar
            setCarrinho({ user_id: userId, items: [], valor_total: 0.0 });
            console.error("Erro carrinho:", carrinhoRes.reason);
          }

          // Processar Recomendações (REAL)
          if (recomendacoesRes.status === 'fulfilled') {
            setRecomendacoes(recomendacoesRes.value.data);
          } else {
            // API Real falhou
            setRecomendacoes([]); 
            console.warn("API de Recomendações falhou:", recomendacoesRes.reason);
          }

          // Processar Pedidos (REAL)
          if (pedidosRes.status === 'fulfilled') {
            setPedidos(pedidosRes.value.data);
          } else {
            // API Real falhou
            setPedidos([]); // Vazio se falhar
            console.warn("API de Pedidos falhou:", pedidosRes.reason);
          }

        } catch (err) {
          console.error("Erro geral ao buscar dados:", err);
          setError("Não foi possível carregar os dados da loja.");
        } finally {
          // Finalizar todos os loadings
          setLoadingProdutos(false);
          setLoadingCarrinho(false);
          setLoadingRecomendacoes(false);
          setLoadingPedidos(false);
        }
      };

      fetchData();
    }
  }, [userId]); // Dependência correta é apenas o userId

  // Efeito para limpar o frete se o carrinho mudar
  useEffect(() => {
    setOpcoesFrete([]);
    setFreteSelecionado(null);
  }, [carrinho]);

  
  // --- 5. FUNÇÕES DE AÇÃO ---

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (usernameInput.trim()) {
      setUserId(usernameInput.trim());
      setViewState('loja'); // Navega para a loja após login
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

  // --- FUNÇÃO DE AÇÃO (Frete) ---
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

  // --- NOVAS FUNÇÕES DE NAVEGAÇÃO E PAGAMENTO ---

  const handleNavigate = (view: ViewState) => {
    setViewState(view);
    setError(null); // Limpa erros ao navegar
  };

  const handleGoToCheckout = () => {
    if (!freteSelecionado) {
      alert("Por favor, selecione uma opção de frete antes de continuar.");
      return;
    }
    setViewState('pagamento');
  };

  const handleUpdateCartao = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setDadosCartao(prev => ({ ...prev, [name]: value }));
  };

  const handleFinalizarCompra = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId || !carrinho || !freteSelecionado) return;

    setLoadingPagamento(true);
    setError(null);

    const payload: PagamentoPayload = {
      user_id: userId,
      items: carrinho.items,
      frete: freteSelecionado,
      valor_total: (carrinho.valor_total || 0) + (freteSelecionado.valor || 0),
      status: "Processando"};

    try {
      // 1. Chamar API de Pagamento (REAL)
       const response = await axios.post(PAGAMENTO_API, payload);
       // Supondo que a API de pagamento retorna o pedido criado no formato { pedido: Pedido }
       const novoPedido: Pedido = response.data.pedido;
      
      // Simulação REMOVIDA

      // 2. Adicionar pedido à lista local
      setPedidos(prevPedidos => [novoPedido, ...prevPedidos]);

      // 3. Limpar o carrinho (API)
      try {
        await axios.delete(`${API_GATEWAY_URL}/api/carrinho/${userId}/limpar`); 
      } catch (err) {
        // Se a API de limpar falhar, pelo menos limpamos localmente
        console.warn("API de limpar carrinho falhou (simulação OK).");
      }
      
      // 4. Limpar estados locais
      setCarrinho({ user_id: userId, items: [], valor_total: 0.0 });
      setFreteSelecionado(null);
      setOpcoesFrete([]);
      setCep("");
      setDadosCartao({ numero: "", nome: "", validade: "", cvv: "" });

      // 5. Redirecionar para Pedidos
      setViewState('pedidos');
      
    } catch (err) {
      console.error("Erro ao finalizar pagamento:", err);
      setError("Não foi possível processar seu pagamento. Tente novamente.");
    } finally {
      setLoadingPagamento(false);
    }
  };


  // --- 6. RENDERIZAÇÃO CONDICIONAL ---

  // SEÇÃO 1: TELA DE LOGIN
  if (viewState === 'login') {
    return (
      <div className="login-container">
        <form onSubmit={handleLogin} className="login-form">
          <h1>Bem-vindo(a) à Loja</h1>
          <p>Digite um nome de usuário para começar:</p>
          <input 
            type="text" 
            placeholder="ex: gabriela"
            value={usernameInput}
            onChange={(e) => setUsernameInput(e.target.value)}
            className="form-input"
          />
          <button type="submit" className="btn btn-primary">Entrar</button>
        </form>
      </div>
    );
  }

  // --- SE ESTIVER LOGADO ---
  
  // Cálculo do Total (movido para cima para ser usado no checkout)
  const subtotal = carrinho?.valor_total || 0;
  const valorFrete = freteSelecionado?.valor || 0;
  const totalGeral = subtotal + valorFrete;

  return (
    <div className="app-container-logged-in">
      {/* --- BARRA DE NAVEGAÇÃO PRINCIPAL --- */}
      <nav className="main-nav">
        <div className="nav-logo">Loja</div>
        <div className="nav-links">
          <button 
            className={`nav-btn ${viewState === 'loja' ? 'active' : ''}`} 
            onClick={() => handleNavigate('loja')}
          >
            Loja
          </button>
          <button 
            className={`nav-btn ${viewState === 'recomendacoes' ? 'active' : ''}`} 
            onClick={() => handleNavigate('recomendacoes')}
          >
            Recomendações
          </button>
          <button 
            className={`nav-btn ${viewState === 'pedidos' ? 'active' : ''}`} 
            onClick={() => handleNavigate('pedidos')}
          >
            Meus Pedidos
          </button>
        </div>
        <div className="nav-user">
          Olá, {userId}
        </div>
      </nav>

      {/* --- CONTEÚDO DA PÁGINA (CONDICIONAL) --- */}
      
      {/* --- VIEW 1: LOJA (Catálogo + Carrinho) --- */}
      {viewState === 'loja' && (
        <div className="app-layout">      
          <main className="catalogo-container">
            <h1>Catálogo</h1>
            {loadingProdutos && <p className="loading-message">Carregando catálogo...</p>}
            {error && !loadingProdutos && <p className="error-message">{error}</p>}
            <div className="catalogo-grid">
              {produtos.map(produto => (
                <div className="produto-card" key={produto.id}>
                  <img src={produto.imagem_url} alt={produto.nome} className="produto-imagem"/>
                  <div className="produto-info">
                    <h2>{produto.nome}</h2>
                    <p className="produto-descricao">{produto.descricao}</p>
                    <div className="produto-footer">
                      <p className="produto-preco">R$ {produto.preco.toFixed(2)}</p>
                      <button className="btn btn-primary" onClick={() => handleAddToCart(produto)}>
                        Adicionar
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </main>

          <aside className="carrinho-container">
            <h2>Meu Carrinho</h2>
            
            {loadingCarrinho && <p className="loading-message">Carregando...</p>}
            
            {!loadingCarrinho && carrinho && carrinho.items.length === 0 && (
              <p className="empty-message">Seu carrinho está vazio.</p>
            )}

            {!loadingCarrinho && carrinho && carrinho.items.length > 0 && (
              <div className="carrinho-lista">
                {carrinho.items.map(item => (
                  <div className="carrinho-item" key={item.produto_id}>
                    <img src={item.imagem_url || ''} alt={item.nome_produto} className="item-imagem" />
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
                    className="form-input"
                  />
                  <button onClick={handleCalcularFrete} disabled={loadingFrete} className="btn btn-secondary">
                    {loadingFrete ? "..." : "Calcular"}
                  </button>
                </div>

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

            {carrinho && carrinho.items.length > 0 && (
              <div className="carrinho-total">
                <div className='total-linha'>
                  <span>Subtotal:</span>
                  <span>R$ {subtotal.toFixed(2)}</span>
                </div>
                
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
            
            {/* Botão de Checkout (NOVO) */}
            {!loadingCarrinho && carrinho && carrinho.items.length > 0 && (
              <button 
                className="btn btn-primary btn-checkout" 
                onClick={handleGoToCheckout} 
                disabled={!freteSelecionado}
              >
                Ir para Pagamento
              </button>
            )}
            {!freteSelecionado && carrinho && carrinho.items.length > 0 && (
                <p className="frete-aviso">Calcule o frete para continuar.</p>
            )}
          </aside>
        </div>
      )}

      {/* --- VIEW 2: RECOMENDAÇÕES --- */}
      {viewState === 'recomendacoes' && (
        <main className="recomendacoes-container">
          <h1>Para Você</h1>
          {loadingRecomendacoes && <p className="loading-message">Carregando...</p>}
          {recomendacoes.length === 0 && !loadingRecomendacoes && (
            <p className="empty-message">Nenhuma recomendação encontrada.</p>
          )}
          <div className="catalogo-grid">
            {/* Reusar o card de produto */}
            {recomendacoes.map(produto => (
               <div className="produto-card" key={produto.id}>
                <img src={produto.imagem_url} alt={produto.nome} className="produto-imagem"/>
                <div className="produto-info">
                  <h2>{produto.nome}</h2>
                  <p className="produto-descricao">{produto.descricao}</p>
                  <div className="produto-footer">
                    <p className="produto-preco">R$ {produto.preco.toFixed(2)}</p>
                    <button className="btn btn-primary" onClick={() => handleAddToCart(produto)}>
                      Adicionar
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>
      )}

      {/* --- VIEW 3: PEDIDOS --- */}
      {viewState === 'pedidos' && (
        <main className="pedidos-container">
          <h1>Meus Pedidos</h1>
          {loadingPedidos && <p className="loading-message">Carregando...</p>}
          {pedidos.length === 0 && !loadingPedidos && (
            <p className="empty-message">Você ainda não fez nenhum pedido.</p>
          )}
          <div className="pedidos-lista">
            {pedidos.map(pedido => (
              <div className="pedido-card" key={pedido.id}>
                <div className="pedido-header">
                  <h3>Pedido #{pedido.id.substring(0, 8)}</h3>
                  <span className="status-pedido">Status: {pedido.status}</span>
                </div>
                <div className="pedido-body">
                  <p>Data: {new Date(pedido.data_pedido).toLocaleDateString()}</p>
                  <p>Total: R$ {pedido.valor_total.toFixed(2)}</p>
                  <p>Itens: {pedido.items.length}</p>
                </div>
                {/* TODO: Expandir para ver detalhes dos itens */}
              </div>
            ))}
          </div>
        </main>
      )}

      {/* --- VIEW 4: PAGAMENTO (CHECKOUT) --- */}
      {viewState === 'pagamento' && (
        <div className="checkout-container">
          <button className="btn-voltar" onClick={() => handleNavigate('loja')}>&larr; Voltar ao carrinho</button>
          <h1>Finalizar Pagamento</h1>
          {error && <p className="error-message">{error}</p>}

          <div className="checkout-layout">
            {/* Coluna de Resumo */}
            <div className="checkout-resumo">
              <h2>Resumo do Pedido</h2>
              <div className="carrinho-lista">
                {carrinho?.items.map(item => (
                  <div className="carrinho-item" key={item.produto_id}>
                    <img src={item.imagem_url || ''} alt={item.nome_produto} className="item-imagem" />
                    <div className="carrinho-item-info">
                      <p className="item-nome">{item.nome_produto}</p>
                      <p className="item-preco">{item.quantidade} x R$ {item.preco_produto.toFixed(2)}</p>
                    </div>
                    {/* Sem botão de remover aqui */}
                  </div>
                ))}
              </div>
              <div className="carrinho-total">
                <div className='total-linha'>
                  <span>Subtotal:</span>
                  <span>R$ {subtotal.toFixed(2)}</span>
                </div>
                <div className='total-linha frete'>
                  <span>Frete ({freteSelecionado?.metodo}):</span>
                  <span>R$ {valorFrete.toFixed(2)}</span>
                </div>
                <div className='total-linha geral'>
                  <span>Total:</span>
                  <span>R$ {totalGeral.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Coluna de Pagamento */}
            <form className="checkout-pagamento" onSubmit={handleFinalizarCompra}>
              <h2>Dados de Pagamento</h2>
              <p className="simulado-aviso">(Simulado - Apenas para fins de teste)</p>
              
              <label>Número do Cartão</label>
              <input type="text" name="numero" value={dadosCartao.numero} onChange={handleUpdateCartao} className="form-input" placeholder="0000 0000 0000 0000" required />
              
              <label>Nome no Cartão</label>
              <input type="text" name="nome" value={dadosCartao.nome} onChange={handleUpdateCartao} className="form-input" placeholder="Seu Nome Completo" required />
              
              <div className="input-group">
                <div>
                  <label>Validade</label>
                  <input type="text" name="validade" value={dadosCartao.validade} onChange={handleUpdateCartao} className="form-input" placeholder="MM/AA" required />
                </div>
                <div>
                  <label>CVV</label>
                  <input type="text" name="cvv" value={dadosCartao.cvv} onChange={handleUpdateCartao} className="form-input" placeholder="123" required />
                </div>
              </div>
              
              <button type="submit" className="btn btn-primary btn-finalizar" disabled={loadingPagamento}>
                {loadingPagamento ? "Processando..." : `Pagar R$ ${totalGeral.toFixed(2)}`}
              </button>
            </form>
          </div>
        </div>
      )}

    </div> // Fim de .app-container-logged-in
  )
}

export default App

