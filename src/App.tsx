import React, { useState } from 'react';
import './index.css'; // usa o CSS já existente

function App() {
  const [tipo, setTipo] = useState("");
  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const [mensagem, setMensagem] = useState("");

  const fazerLogin = async () => {
    try {
      const resposta = await fetch("https://backend-estante-magica.tztdymttds.repl.co/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ usuario, senha, tipo })
      });

      const dados = await resposta.json();
      if (resposta.ok) {
        setMensagem(`✅ Login realizado com sucesso! Bem-vindo(a), ${dados.usuario}`);
      } else {
        setMensagem(`❌ ${dados.erro}`);
      }
    } catch (erro) {
      setMensagem("❌ Erro de conexão com o servidor.");
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

      {(tipo === "aluno" || tipo === "professor") && (
        <>
          <h2>Login de {tipo === "aluno" ? "Aluno" : "Professor"}</h2>
          <input type="text" placeholder="Usuário" value={usuario} onChange={e => setUsuario(e.target.value)} />
          <input type="password" placeholder="Senha" value={senha} onChange={e => setSenha(e.target.value)} />
          <button onClick={fazerLogin}>Entrar</button>
          <button onClick={() => { setTipo(""); setMensagem(""); }}>🔙 Voltar</button>
          {mensagem && <p>{mensagem}</p>}
        </>
      )}
    </div>
  );
}

export default App;
