import React, { useState } from "react";
import "./App.css";

function App() {
  const [tipo, setTipo] = useState("");
  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const [mensagem, setMensagem] = useState("");

  const fazerLogin = async () => {
    setMensagem("🔄 Verificando...");

    try {
      const resposta = await fetch(
        "https://estante-magica-backend.onrender.com/login",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ usuario, senha }),
        }
      );

      const dados = await resposta.json();

      if (resposta.ok) {
        setMensagem(`✅ Login bem-sucedido! Bem-vindo(a), ${dados.tipo}.`);
      } else {
        setMensagem(`❌ Erro: ${dados.erro}`);
      }
    } catch (erro) {
      setMensagem("🚫 Erro de conexão com o servidor.");
    }
  };

  return (
    <div className="container">
      <h1>📚 Estante Mágica</h1>

      {!tipo && (
        <>
          <p>Quem está acessando?</p>
          <button onClick={() => setTipo("aluno")}>Sou Aluno</button>
          <button onClick={() => setTipo("professor")}>Sou Professor</button>
        </>
      )}

      {tipo && (
        <>
          <h2>Login do {tipo}</h2>
          <input
            type="text"
            placeholder="Usuário"
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
          />
          <input
            type="password"
            placeholder="Senha"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
          />
          <button onClick={fazerLogin}>Entrar</button>
          <button onClick={() => setTipo("")}>🔙 Voltar</button>
          <p>{mensagem}</p>
        </>
      )}
    </div>
  );
}

export default App;
