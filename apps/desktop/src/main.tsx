import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/globals.css";
import { applyThemeClass, useThemeStore } from "./stores/theme-store";

// Inicializa a classe do tema salvo no elemento raiz
applyThemeClass(useThemeStore.getState().theme);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
