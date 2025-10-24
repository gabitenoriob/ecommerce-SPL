// Importa o useState (para guardar dados) e useEffect (para buscar dados)
import { useState, useEffect } from 'react'
// Importa o axios (para fazer a chamada HTTP)
import axios from 'axios'
// Importa o CSS
import './App.css'

// --- Definindo o "formato" (Tipo) de um Produto ---
// Isso ajuda o TypeScript a saber quais dados esperamos
interface Produto {
  id: number;
  nome: string;
  descricao: string;
  preco: number;
  imagem_url: string;
}

// --- Componente Principal da Aplicação ---
function App() {
  // --- Estados do Componente ---
  
  // 1. Onde vamos guardar a lista de produtos que vem da API
  const [produtos, setProdutos] = useState<Produto[]>([]);
  // 2. Um estado para sabermos se estamos "Carregando"
  const [loading, setLoading] = useState(true);
  // 3. Um estado para guardar qualquer mensagem de erro
  const [error, setError] = useState<string | null>(null);

  // --- Efeito (Effect) ---
  // O useEffect é usado para executar código "paralelamente",
  // como buscar dados em uma API.
  // O [] no final significa "rode este código apenas uma vez, quando o componente montar"
  useEffect(() => {
    // Função para buscar os dados
    const fetchProdutos = async () => {
      try {
        // 1. Tenta buscar os produtos do seu API Gateway
        const response = await axios.get('http://localhost:8080/api/catalogo/produtos/');
        
        // 2. Se der certo, salva os produtos no estado
        setProdutos(response.data);
        
        // 3. Imprime no console (para debug)
        console.log("Produtos carregados:", response.data);

      } catch (err) {
        // 4. Se der errado, salva a mensagem de erro no estado
        console.error("Erro ao buscar produtos:", err);
        setError("Falha ao carregar o catálogo. O backend está rodando?");
      } finally {
        // 5. Independentemente de sucesso ou erro, para de carregar
        setLoading(false);
      }
    };

    fetchProdutos(); // Chama a função que acabamos de criar
  }, []); // O [] vazio garante que isso rode só uma vez

  // --- Renderização (O que aparece na tela) ---

  // Se estiver carregando, mostra uma mensagem
  if (loading) {
    return <div className="loading-message">Carregando catálogo...</div>
  }

  if (error) {
    return <div className="error-message">{error}</div>
  }

  return (
    <div className="app-container">
      <h1>💖 Catálogo de Labubus 💖</h1>
      
      <div className="catalogo-grid">
        {/* Faz um "loop" (map) na lista de produtos */}
        {/* e cria um card para cada um */}
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
              <p className="produto-preco">R$ {produto.preco.toFixed(2)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App